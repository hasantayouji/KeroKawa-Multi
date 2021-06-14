# Import socket module 
from libraries import zmqimage
import cv2
import time
import socket
from inferences.inference import do_detect  # paralel
from inferences.decision import final_decision
from libraries.basler_cam import kamera

basler1 = kamera(ip_address='192.168.0.235')
basler2 = kamera(ip_address='192.168.0.234')
basler3 = kamera(ip_address='192.168.0.123')

######################################################################################

try:
	zmqi = zmqimage.ZmqImageShowServer(open_port="tcp://*:3455")
	zmqo = zmqimage.ZmqConnect(connect_to="tcp://192.168.0.77:3445")  # master/GUI
	zmqo_aio_ng = zmqimage.ZmqConnect(connect_to="tcp://192.168.0.77:3435")
	print("AIO")
except:
	print('AIO Connection Error. Check AIO PC')

zmqo_save = zmqimage.ZmqConnect(connect_to="tcp://localhost:3535")  # saving

print('ETHERNET INITIALIZED')

dummy = cv2.imread('/home/jetsonmapinai/Documents/KeroKawa-Multi-versi2/7000.png')

Pic1 = dummy
Pic2 = dummy
Pic3 = dummy
# Create a socket object
s = socket.socket()

# Define the port on which you want to connect
port = 8501

# connect to the server on local computer
print('Connecting......')
try:
	s.connect(('192.168.0.10', port))
except:
	print('Connection Error. Check PLC or Hub')

#######################################################################################3

print('connected!')


def get_trig_eth(port_target):
	kirim = 'RD {}\r'.format(port_target)  # 'RD DM0001 \r'
	s.send(kirim.encode('ascii'))
	pesan = s.recv(1024)
	pesan = pesan.decode('utf-8')
	pesan = pesan.replace('\r\n', '')
	# print('pada {} : {}'.format(port_target,pesan))
	return pesan


def give_trig_eth(port_target, messg):
	kirim = 'WR {} {}\r'.format(port_target, messg)  # 'WR dm0010 1'
	while True:
		s.send(kirim.encode('ascii'))
		pesan = s.recv(1024).decode('utf-8')
		print(pesan)
		if pesan == 'OK\r\n':
			break


def get_img(pp1, pp2, pp3):
	pic2, p2 = basler2.ambilgambar()
	pic1, p1 = basler1.ambilgambar()
	pic3, p3 = basler3.ambilgambar()
	if p1 == 0:
		pic1 = pp1
	if p2 == 0:
		pic2 = pp2
	if p3 == 0:
		pic3 = pp3
	print(p1, p2, p3)
	return pic1, pic2, pic3


def txtNG(s_list):
	hasil = ''
	for k in s_list:
		hasil = hasil + ' ' + k
	return k


def detection(img, sec, n):
	while True:
		try:
			ori, pic, stat_list, boxes = do_detect(img)  # boxes dalam int
			break
		except Exception as e:
			print("error di detection", e)
			img = basler1.ambilgambar()

	if len(stat_list) < 1:
		pred = "OK"
		stat_list = ['OK']
		boxes = []
	else:
		pred = "NG"

	pkt = {"sec": sec}
	zmqo_save.imsend(pkt, ori)
	print(sec + pred + str(n))
	zmqo.imsend(sec + pred + str(n), pic)
	return stat_list, boxes


def get_result():
	global dummy
	print('mengirim hasil')
	zmqo.imsend('Done', dummy)


def section_done(prev_sec, cur_sec):
	global dummy
	if not prev_sec == cur_sec:
		issaved = True
		zmqo_save.imsend("Done", dummy)
	else:
		issaved = False
	return issaved, cur_sec


def mainprocess(listS1, listS2, listS3, listB1, listB2, listB3, scs, n):
	global Pic1, Pic2, Pic3
	print('SUKSES')
	Pic1, Pic2, Pic3 = get_img(Pic1, Pic2, Pic3)
	start = time.time()
	res1, box1 = detection(Pic1, scs[0], n)
	res2, box2 = detection(Pic2, scs[1], n)
	res3, box3 = detection(Pic3, scs[2], n)
	print(f'waktu detek: {time.time() - start}')
	give_trig_eth('MR300', '1')
	listS3.append(res3)
	listB3.append(box3)
	listS1.append(res1)
	listS2.append(res2)
	listB1.append(box1)
	listB2.append(box2)


def mainprocess2(listS2, listS3, listB2, listB3, scs, n):
	global Pic1, Pic2, Pic3
	print('SUKSES')
	Pic1, Pic2, Pic3 = get_img(Pic1, Pic2, Pic3)
	zmqo.imsend("3", Pic1)
	res2, box2 = detection(Pic2, scs[0], n)
	res3, box3 = detection(Pic3, scs[1], n)
	give_trig_eth('MR300', '1')
	listS3.append(res3)
	listB3.append(box3)
	listS2.append(res2)
	listB2.append(box2)


def main_step():
	# kasih tau plc,jetson sudah siap
	give_trig_eth('MR0', '1')
	print('starting with PLC ethernet')
	istime = False
	slist1 = []
	slist2 = []
	slist3 = []
	slist4 = []
	slist5 = []
	blist1 = []
	blist2 = []
	blist3 = []
	blist4 = []
	blist5 = []
	i1 = 0
	i2 = 0
	isDone = True
	curS = 0
	while True:
		cpt = get_trig_eth('MR15')
		posOK = get_trig_eth('MR301')
		pos1 = get_trig_eth('MR9')
		pos2 = get_trig_eth('MR10')

		pos1T1 = get_trig_eth('MR5')
		pos2T1 = get_trig_eth('MR6')
		
		D26 = get_trig_eth('B204')
		if cpt == '1':
			print('MR15')
			### cek posisi ###
			if pos1 == '1' or pos1T1 == '1':
				if istime == False:
					start = time.time()
					give_trig_eth('MR13', '0')
					give_trig_eth('MR14', '0')
					istime = True
				print('Posisi 1')
				i1 += 1
				mainprocess(slist1, slist2, slist3, blist1, blist2, blist3, ["Sec1", "Sec2", "Sec3"], i1)
				curS = 1
				isSaved, curS = section_done(curS, 1)
				give_trig_eth("MR300", 0)

			elif pos2 == '1' or pos2T1 == '1':
				istime = False
				print('Posisi 2')
				i2 += 1
				mainprocess2(slist4, slist5, blist4, blist5, ["Sec4", "Sec5"], i2)
				isSaved, curS = section_done(curS, 2)
				give_trig_eth("MR300", 0)
				isDone = True

			elif posOK == '1' and isDone:
				print('Finishing')
				give_trig_eth("MR301", 0)
				isDone = False
				################ Finishing #################
				i1 = 0
				i2 = 0
				# global paralel
				isSaved, curS = section_done(curS, 3)
				zmqo.imsend("Done", dummy)

		else:
			if posOK == '1' and isDone:
				print('MR15 MATI')
				print('Finishing')
				isDone = False
				################ Finishing #################
				i1 = 0
				i2 = 0
				isSaved, curS = section_done(curS, 3)
				zmqo.imsend("Done", dummy)
				slist_all = [slist1, slist2, slist3, slist4, slist5]
				blist_all = [blist1, blist2, blist3, blist4, blist5]
				NG_list, NG_num, NG_sect = final_decision(blist_all, slist_all)
				print("paralel waiting CPT FALSE... ")
				print("################\n", NG_list, "\n################")
				zmqo.imsend('Done', dummy)
				judjment = ''
				#zmqo.imsend(NG_list, dummy)
				if len(NG_list) < 1:
					judjment = 'OK'
					print('OK')
					zmqo.imsend('OK', dummy)
					give_trig_eth('MR13', '1')
                    
				else:
					judjment = 'NG: '
					ngst = 'NG: '
					for i in range(len(NG_list)):
						print('NG: {} sebanyak {} di section{}'.format(NG_list[i], NG_num[i], NG_sect[i]))
						ngst = ngst + ' ; ' + NG_list[i] + " di section {}".format(NG_sect[i])
					zmqo.imsend(ngst, dummy)
					if D26 == '1':
						give_trig_eth('MR14', '1')
					else:
						give_trig_eth('MR14', '1')
				slist1 = []
				slist2 = []
				slist3 = []
				slist4 = []
				slist5 = []
				blist1 = []
				blist2 = []
				blist3 = []
				blist4 = []
				blist5 = []
                
                
                    
if __name__ == '__main__':
	give_trig_eth('MR1', '0')
	give_trig_eth('MR2', '0')
	give_trig_eth('MR3', '0')
	give_trig_eth('MR4', '0')
	give_trig_eth('MR13', '0') #OK
	give_trig_eth('MR14', '0') #NG
	give_trig_eth('MR15', '0')
	give_trig_eth('MR301', '0')
	try:
		main_step()
	except KeyboardInterrupt:
		# print (e)
		give_trig_eth('MR0', '0')
		give_trig_eth('MR1', '0')
		give_trig_eth('MR2', '0')
		give_trig_eth('MR3', '0')
		give_trig_eth('MR4', '0')
		give_trig_eth('MR13', '0')
		give_trig_eth('MR14', '0')
		give_trig_eth('MR15', '0')
		give_trig_eth('MR301', '0')
