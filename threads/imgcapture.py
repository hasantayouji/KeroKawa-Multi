import threading
from libraries.basler_cam import kamera, get_img
from libraries import zmqimage
from utils.Utils import get_plc_data, change_plc_data, connectPLC, save_log

connectPLC()
basler1 = kamera(ip_address='192.168.0.235')
basler2 = kamera(ip_address='192.168.0.234')
basler3 = kamera(ip_address='192.168.0.123')
try:
    zmqo_images = zmqimage.ZmqConnect(connect_to="tcp://localhost:5678")
    save_log('Connected to processing script')
except:
    save_log('Unable to connect to processing script')

PART_FLAG = False


class CamCapture(threading.Thread):
    def run(self):
        global PART_FLAG
        while True:
            cam_status = get_plc_data('MR15')
            cam_pos_T1_1 = get_plc_data('MR5')
            cam_pos_T1_2 = get_plc_data('MR6')
            cam_pos_D26_1 = get_plc_data('MR9')
            cam_pos_D26_2 = get_plc_data('MR10')
            cam_pos_D78_1 = get_plc_data('MR11')
            cam_pos_D78_2 = get_plc_data('MR12')
            end_part = get_plc_data('MR301')
            if cam_status == '1':
                if cam_pos_T1_1 == '1' or cam_pos_D26_1 == '1' or cam_pos_D78_1 == '1':
                    cam1_img = basler1.ambilgambar()
                    cam2_img = basler2.ambilgambar()
                    cam3_img = basler3.ambilgambar()
                    change_plc_data('MR300', '1')
                    msg = ['1', '_']
                    zmqo_images.imsend(msg, cam1_img)
                    zmqo_images.imsend(msg, cam2_img)
                    zmqo_images.imsend(msg, cam3_img)
                elif cam_pos_T1_2 == '1' or cam_pos_D26_2 == '1' or cam_pos_D78_2 == '1':
                    if cam_pos_T1_2 == '1':
                        msg = ['2', 'T1']
                    else:
                        msg = ['2', '_']
                    cam1_img = basler1.ambilgambar()
                    cam2_img = basler2.ambilgambar()
                    cam3_img = basler3.ambilgambar()
                    change_plc_data('MR300', '1')
                    zmqo_images.imsend(msg, cam1_img)
                    zmqo_images.imsend(msg, cam2_img)
                    zmqo_images.imsend(msg, cam3_img)
                    PART_FLAG = True
                change_plc_data('MR300', '0')
            elif cam_status == '0' and end_part == '1' and PART_FLAG:
                PART_FLAG = False
                zmqo_images.imsend(["Done", "Done"], get_img())
                zmqo_images.imsend(["Done", "Done"], get_img())
                zmqo_images.imsend(["Done", "Done"], get_img())
                print('FINISH 1 PART')
