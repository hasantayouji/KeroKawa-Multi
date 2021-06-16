import numpy as np
import time
import tensorflow as tf
import cv2

IMAGE_PATH = '/home/jetsonmapinai/Documents/AI Visual Inspection/dummy.png'
PB_PATH = '/home/jetsonmapinai/Documents/tf_trt_models/data/faster_rcnn_inception_v2_kdsk_feb5_50_trt.pb'

input_names = ['image_tensor']
output_names = ['detection_boxes', 'detection_classes', 'detection_scores', 'num_detections']

"""Load the TRT graph from the pre-build pb file."""

trt_graph_def = tf.GraphDef()
with tf.gfile.GFile(PB_PATH, 'rb') as pf:
    trt_graph_def.ParseFromString(pf.read())

with tf.Graph().as_default() as trt_graph:
    tf.import_graph_def(trt_graph_def, name='')

tf_config = tf.ConfigProto()
tf_config.gpu_options.allow_growth = True
tf_sess = tf.Session(config=tf_config, graph=trt_graph)

tf_input = tf_sess.graph.get_tensor_by_name('image_tensor:0')
tf_scores = tf_sess.graph.get_tensor_by_name('detection_scores:0')
tf_boxes = tf_sess.graph.get_tensor_by_name('detection_boxes:0')
tf_classes = tf_sess.graph.get_tensor_by_name('detection_classes:0')
tf_num_detections = tf_sess.graph.get_tensor_by_name('num_detections:0')


def do_detect(image):
    class_name = ["BG", "Keropos", "Kurokawa", "Dakon", "Scratch", "Hole", "D78", "Scratch_OK", "Water_Droplet",
                  "Keropos_Casting", "Step", "PartingLine"]
    scores, boxes, classes, num_detections = tf_sess.run([tf_scores, tf_boxes, tf_classes, tf_num_detections],
                                                         feed_dict={tf_input: image[None, ...]})
    ori = image.copy()
    boxes = boxes[0]
    scores = scores[0]
    classes = classes[0]
    num_detections = num_detections[0]
    cls_det = []
    bbox = []
    for i in range(int(num_detections)):
        if (scores[i] > 0.4 and classes[i] == 1) or (scores[i] >= 0.7 and (classes[i] == 2 or classes[i] == 9 or classes[i] == 10 or classes[i] == 11 or classes[i] == 12)) or (scores[i] > 0.98 and (classes[i] == 4)) or (scores[i] >= 0.5 and (classes[i] == 3)):
            box = boxes[i] * np.array([image.shape[0], image.shape[1], image.shape[0], image.shape[1]])
            image = cv2.rectangle(image, (int(box[1]), int(box[0])), (int(box[3]), int(box[2])), (0, 0, 255), 2)
            image = cv2.putText(image, '%s %.2f' % (class_name[int(classes[i])], scores[i]),
                                (int(box[1]) - 10, int(box[0]) - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 0, 255))
            cls_det.append(class_name[int(classes[i])])
            bbox.append(box)
    return ori, image, cls_det, bbox


def main():
    image = cv2.imread('/media/jetsonmapinai/Seagate Backup Plus Drive/IMG-MASSPRO/24-11-2020/NG/part 10059/sect 1/4.png')
    __, image, __, __ = do_detect(image)
    cv2.imshow('result', image)
    print("-------------------------------------")
    print("PRESS 'ESC' TO PERFORM BENCHMARK TEST WHEN IMAGE APPEARS AND IS IN FOCUS")
    print("-------------------------------------")
    cv2.waitKey(0)
    cv2.destroyAllWindows()

    num_samples = 50
    t0 = time.time()
    for i in range(int(num_samples)):
        t2 = time.time()
        scores, boxes, classes, num_detections = tf_sess.run([tf_scores, tf_boxes, tf_classes, tf_num_detections],
                                                             feed_dict={tf_input: image[None, ...]})
        print('%f [sec]' % (time.time() - t2))
    t1 = time.time()
    print('Average runtime: %f seconds' % (float(t1 - t0) / num_samples))

    tf_sess.close()


if __name__ == '__main__':
    main()
