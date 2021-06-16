import socket
import time


s0 = socket.socket()
port = 8501
s0.bind(('192.168.55.1', port))
s0.listen(5)

s, addr = s0.accept()

MR15 = '0'
MR5 = '1'
MR6 = '0'
MR301 = '0'
B204 = '0'
counter = 0

def terimaTemp():
    pesan = s.recv(1024).decode('utf-8')
    pesan = pesan.replace('\r', '')
    global counter, MR15, MR5, MR6, MR301
    print(pesan)
    if pesan.startswith('WR'):
        kirim = 'OK\r\n'
        s.send(kirim.encode('ascii'))
        if pesan == 'WR MR300 1':
            MR15 = '0'
            counter += 1
            print(counter)
        elif pesan == 'WR MR300 0':
            MR15 = '1'
    elif pesan.startswith('RD'):
        if pesan == 'RD MR15':
            kirim = f'{MR15}\r\n'
        elif pesan == 'RD MR5':
            kirim = f'{MR5}\r\n'
        elif pesan == 'RD MR6':
            kirim = f'{MR6}\r\n'
        elif pesan == 'RD MR301':
            kirim = f'{MR301}\r\n'
            if counter == 24:
                counter += 1
                print(counter)
        else:
            kirim = f'0\r\n'
        print(f'{pesan}: {kirim}')
        s.send(kirim.encode('ascii'))

terimaTemp()
terimaTemp()
terimaTemp()
terimaTemp()

trig = input("input 'start'  then enter to Auto...")
if trig == 'start':
    MR15 = '1'
    while True:
        terimaTemp()
        if counter < 12:
            MR5 = '1'
            MR6 = '0'
        elif counter >= 12 and counter < 24:
            MR5 = '0'
            MR6 = '1'
        elif counter == 24:
            MR301 = '1'
            MR5 = '0'
            MR6 = '0'
            MR15 = '0'
        elif counter == 25:
            MR301 = '0'
            counter = 0
            MR5 = '1'
            MR6 = '0'
            MR15 = '1'
            print('Finish one part')