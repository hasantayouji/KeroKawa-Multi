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


def change_plc_data(port_target, messg):
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


def get_plc_data(port_target):
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


def getTgl():
    waktu = datetime.now()
    tgl = waktu.strftime('%d-%m-%Y')
    jam = waktu.strftime('%H:%M:%S')
    bln = waktu.strftime('%m')
    return tgl, jam, bln
