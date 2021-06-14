import socket
from datetime import datetime

import cv2

# Koneksi untuk button manual
port = 8501
s = socket.socket()


def save_log(message):
    tgl, jam, __ = getTgl()
    with open(f'logs/logs_{tgl}.txt', 'a') as logfile:
        logfile.write(tgl + ' ' + jam + '  ' + message + '\n')


def connectPLC():
    save_log('Connecting to PLC')
    try:
        s.connect(('192.168.0.10', port))
        s.settimeout(3)
        save_log('PLC connected')
    except:
        save_log('PLC connection fail')
        print('PLC Connection Error. Check PLC or Hub')


def give_trig_eth(port_target, messg):
    kirim = 'WR {} {}\r'.format(port_target, messg)  # 'WR dm0010 1'
    save_log(f'Send command to PLC => {port_target}: {messg}')
    while True:
        try:
            s.send(kirim.encode('ascii'))
            pesan = s.recv(1024).decode('utf-8')
            if pesan == 'OK\r\n':
                print(f'{port_target} - {messg}')
                break
        except:
            print('Error')
            break


def get_trig_eth(port_target):
    try:
        kirim = 'RD {}\r'.format(port_target)  # 'RD DM0001 \r'
        s.send(kirim.encode('ascii'))
        pesan = s.recv(1024)
        pesan = pesan.decode('utf-8')
        pesan = pesan.replace('\r\n', '')
        save_log(f'Receive message from PLC => {port_target}: {pesan}')
        return pesan
    except:
        pesan = 'error'
        return pesan


def createQImage(pic):
    pic = cv2.cvtColor(pic, cv2.COLOR_BGR2RGB)
    qformat = QImage.Format_Indexed8
    if len(pic.shape) == 3:
        if pic.shape[2] == 4:
            qformat = QImage.Format_RGBA8888
        else:
            qformat = QImage.Format_RGB888
    pic = QImage(pic, pic.shape[1], pic.shape[0], pic.strides[0], qformat)
    return pic


def getTgl():
    waktu = datetime.now()
    tgl = waktu.strftime('%d-%m-%Y')
    jam = waktu.strftime('%H:%M:%S')
    bln = waktu.strftime('%m')

    return tgl, jam, bln


def getAllHistoryCount(tgl, flag='all'):
    with open(f'history_data/{tgl}_{flag}.csv') as fall:
        return len(fall.readlines()) + 10000


class PandasModel(QAbstractTableModel):
    def __init__(self, data):
        super().__init__()
        self._data = data

    def rowCount(self, parent=None):
        return self._data.shape[0]

    def columnCount(self, parent=None):
        return self._data.shape[1]

    def data(self, index, role=Qt.DisplayRole):
        if index.isValid():
            if role == Qt.DisplayRole:
                return str(self._data.iloc[index.row(), index.column()])
        return None

    def headerData(self, col, orientation=Qt.Horizontal, role=Qt.DisplayRole):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return self._data.columns[col]
        return None
