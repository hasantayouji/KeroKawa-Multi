import os
from utils.Utils import save_log
import cv2
import random


class kamera():
    def __init__(self, folder='dakon'):
        self.sumberdata = folder
        self.list_dir = os.listdir(folder)

    def ambilgambar(self, i):
        print(self.sumberdata)
        files = sorted(os.listdir(self.sumberdata))
        list_file = []
        for fname in files:
            if fname.endswith('png'):
                list_file.append(fname)
        img = cv2.imread(self.sumberdata + list_file[i])
        return img


if __name__ == '__main__':
    part_num = '1'
    img_dir = '/media/mapin/Windows/dataset_to_label/Kuro/'
    target_dir = os.path.join(img_dir, part_num)
    cam1 = kamera(target_dir)
