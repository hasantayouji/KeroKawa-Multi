from threads.processing import Processing
from threads.imgcapture import CamCapture
from utils.Utils import change_plc_data


def camthr():
    cam = CamCapture()
    cam.start()


def procthr():
    cim = Processing()
    cim.start()


if __name__ == '__main__':
    try:
        camthr()
        procthr()
    except:
        change_plc_data('MR0', '0')
        change_plc_data('MR13', '0')
        change_plc_data('MR14', '0')
        change_plc_data('MR300', '0')
    finally:
        change_plc_data('MR0', '0')
        change_plc_data('MR13', '0')
        change_plc_data('MR14', '0')
        change_plc_data('MR300', '0')
