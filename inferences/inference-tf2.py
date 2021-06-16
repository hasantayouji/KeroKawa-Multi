import numpy as np
import time
import cv2
import tensorflow as tf


IMAGE_PATH = '7000.png'
SAVEMODEL_PATH = '/home/jetsonmapinai/Documents/AI Visual Inspection/models/tf2_savedmodel/saved_model'

gpus = tf.config.experimental.list_physical_devices('GPU')
for gpu in gpus:
    try:
        tf.config.experimental.set_memory_growth(gpu, True)
    except RuntimeError as e:
        print(e)
    tf.config.experimental.set_virtual_device_configuration(
        gpu,
        [tf.config.experimental.VirtualDeviceConfiguration(
            memory_limit=3000)])
detect_fn = tf.saved_model.load(SAVEMODEL_PATH, tags=['serve'])


def do_detect(image):
    # image = clahein(clahe)
    class_name = ["BG", "Keropos", "Dakon", "Scratch", "Kurokawa", "Hole", "D78", "Scratch_OK", "Water_droplet"]
    ori = image.copy()
    input_tensor = tf.convert_to_tensor(image)
    input_tensor = input_tensor[tf.newaxis, ...]
    detections = detect_fn(input_tensor)
    boxes = detections['detection_boxes'][0].numpy()
    scores = detections['detection_scores'][0].numpy()
    classes = detections['detection_classes'][0].numpy().astype(int)
    cls_det = []
    bbox = []
    for i in range(len(boxes)):
        kelas = classes[i]
        if (scores[i] >= 0.1 and kelas == 1) or\
                (scores[i] >= 0.3 and kelas != 5 and kelas != 6 and kelas != 7 and kelas != 8):
            box = boxes[i] * np.array([image.shape[0], image.shape[1], image.shape[0], image.shape[1]])
            image = cv2.rectangle(image, (int(box[1]), int(box[0])), (int(box[3]), int(box[2])), (0, 0, 255), 2)
            image = cv2.putText(image, '%s %.2f' % (class_name[int(classes[i])], scores[i]),
                                (int(box[1]) - 10, int(box[0]) - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 0, 255))
            cls_det.append(class_name[kelas])
            bbox.append(box)
    return ori, image, cls_det, bbox


def clahein(image):
    gridsize = 8
    lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
    lab_planes = cv2.split(lab)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(gridsize, gridsize))
    lab_planes[0] = clahe.apply(lab_planes[0])
    lab = cv2.merge(lab_planes)
    bgr = cv2.cvtColor(lab, cv2.COLOR_LAB2BGR)
    return bgr


def main():
    image = cv2.imread(IMAGE_PATH)
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
        do_detect(image)
        print('%f [sec]' % (time.time() - t2))
    t1 = time.time()
    print('Average runtime: %f seconds' % (float(t1 - t0) / num_samples))


if __name__ == '__main__':
    main()
