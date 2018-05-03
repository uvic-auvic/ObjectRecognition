import os
import cv2
import numpy as np
import time
import tensorflow as tf

# Resources
pwd = os.getcwd()
VIDEO = "jabulani_vid2.mp4"
GRAPH = "frozen_inference_graph.pb"
LABEL = "annotation.pbtxt"

# Files
graph_file = os.path.join(pwd, "output_graph", GRAPH)
video_file = os.path.join(pwd, VIDEO)
label_file = os.path.join(pwd, LABEL)

def detect_objects(sess, tf_graph, frame_rgb):
    image_expanded = np.expand_dims(frame_rgb, axis=0)
    image_tensor = tf_graph.get_tensor_by_name('image_tensor:0')

    # Grab the confidence levels for each class
    boxes = tf_graph.get_tensor_by_name('detection_boxes:0')
    scores = tf_graph.get_tensor_by_name('detection_scores:0')
    classes = tf_graph.get_tensor_by_name('detection_classes:0')
    num_detections = tf_graph.get_tensor_by_name('num_detections:0')

    boxes, scores, classes, num_detections = sess.run(
        [boxes, scores, classes, num_detections],
        feed_dict={image_tensor: image_expanded})

if __name__ == "__main__":
    # Load TF graph 
    with tf.gfile.GFile(graph_file, 'rb') as f:
        graph_def = tf.GraphDef()
        graph_def.ParseFromString(f.read())
        tf.import_graph_def(graph_def, name='')

    detection_graph = tf.get_default_graph()
    sess = tf.Session(graph=detection_graph)

    # Init Video file to read from
    cap = cv2.VideoCapture(video_file)

    print("\n")
    print(25*"#")
    print("# Starting benchmarking #")
    print(25*"#")

    times = []

    # Start looping over video
    counter = 0
    sum = 0
    try:
        while cap.isOpened():
            valid_frame, frame = cap.read()
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            duration = -time.time()
            detect_objects(sess, detection_graph, frame_rgb)
            duration += time.time()
            print("[{:05d}] Detection took {:.2f} ms".format(counter, duration * 1000))
            counter += 1
            sum += duration * 1000
    except KeyboardInterrupt:
        pass
    finally:
        print("Closing TensorFlow Session")
        sess.close()
        

    print(25*"#")
    print("# Finished benchmarking")
    print(25*"#")
    average = sum / counter
    print("{} Frames processed. Avg time: {:.2f} ms".format(counter, average))
