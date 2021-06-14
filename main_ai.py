from threads.processing import Processing
from threads.imgcapture import CamCapture


def camthr():
    cam = CamCapture()
    cam.start()


def procthr():
    cim = Processing()
    cim.start()


if __name__ == '__main__':
    camthr()
    procthr()
