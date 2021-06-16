import os
from utils.Utils import save_log
import cv2
import random


class kamera():
    def __init__(self, folder='dakon'):
        self.sumberdata = folder
        self.list_dir = os.listdir(folder)

    def ambilgambar(self):
        files = os.listdir(self.sumberdata)
        imgfile = random.choice(files)
        save_log(f'{self.sumberdata + imgfile}')
        while not imgfile.endswith(".png"):
            imgfile = random.choice(files)
            print(self.sumberdata + imgfile)
        img = cv2.imread(self.sumberdata + imgfile)
        return img


if __name__ == '__main__':
    part_num = '1'
    img_dir = '/media/mapin/Windows/dataset_to_label/Kuro/'
    target_dir = os.path.join(img_dir, part_num)
    cam1 = kamera(target_dir)
