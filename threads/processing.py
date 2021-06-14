import threading
from libraries import zmqimage
from inferences.inference import do_detect
import time
from utils.Utils import give_trig_eth, get_trig_eth
from inferences.decision import final_decision
from inferences.decisiond78 import d78_decision

zmqi_img = zmqimage.ZmqImageShowServer(open_port="tcp://*:5679")
zmqi = zmqimage.ZmqImageShowServer(open_port="tcp://*:3455")

zmqo = zmqimage.ZmqConnect(connect_to="tcp://192.168.0.77:3445")  # master/GUI
zmqo_aio_ng = zmqimage.ZmqConnect(connect_to="tcp://192.168.0.77:3435")
zmqo_save = zmqimage.ZmqConnect(connect_to="tcp://192.168.0.77:3535")  # saving


class Processing(threading.Thread):
    def run(self):
        slist1 = []
        slist2 = []
        slist3 = []
        slist4 = []
        slist5 = []
        slist6 = []
        blist1 = []
        blist2 = []
        blist3 = []
        blist4 = []
        blist5 = []
        blist6 = []
        ilist1 = []
        ilist2 = []
        ilist3 = []
        ilist4 = []
        ilist5 = []
        ilist6 = []
        i1 = 0
        i2 = 0
        D78 = get_trig_eth('MR1709')
        D26 = get_trig_eth('MR1509')
        while True:
            start = time.time()
            cam_pos1, img1 = zmqi_img.imreceive()
            cam_pos2, img2 = zmqi_img.imreceive()
            cam_pos3, img3 = zmqi_img.imreceive()
            if cam_pos1[0] == '1':
                i1 += 1
                mainprocess(slist1, slist2, slist3, blist1, blist2, blist3, ilist1, ilist2, ilist3,
                            ["Sec1", "Sec2", "Sec3"], i1, img1, img2, img3)
            elif cam_pos1[0] == '2' and cam_pos1[1] == 'T1':
                i2 += 1
                mainprocess2(slist4, slist5, blist4, blist5, ilist4, ilist5, ["Sec4", "Sec5"], i2, img2, img3)
            elif cam_pos1[0] == '2' and not cam_pos1[1] == 'T1':
                i2 += 1
                mainprocess(slist4, slist5, slist6, blist4, blist5, blist6, ilist4, ilist5, ilist6,
                            ["Sec4", "Sec5", "Sec6"], i2, img1, img2, img3)
            if i2 == 12 and cam_pos1[0] == 'Done':
                i1 = 0
                i2 = 0
                zmqo.imsend("Done", img1)
                if D26 == '1' or D78 == '1':
                    slist_all = [slist1, slist2, slist3, slist4, slist5, slist6]
                    blist_all = [blist1, blist2, blist3, blist4, blist5, blist6]
                    ilist_all = [ilist1, ilist2, ilist3, ilist4, ilist5, ilist6]
                    NG_list, NG_num, NG_sect, NG_img = d78_decision(blist_all, slist_all, ilist_all)
                else:
                    slist_all = [slist1, slist2, slist3, slist4, slist5]
                    blist_all = [blist1, blist2, blist3, blist4, blist5]
                    ilist_all = [ilist1, ilist2, ilist3, ilist4, ilist5]
                    NG_list, NG_num, NG_sect, NG_img = final_decision(blist_all, slist_all, ilist_all)
                print("paralel waiting CPT FALSE... ")
                print("################\n", NG_list, "\n################")
                zmqo.imsend('Done', img2)
                judgment = ''
                # zmqo.imsend(NG_list, dummy)
                if len(NG_list) < 1:
                    judgment = 'OK'
                    print('OK')
                    zmqo.imsend('OK', img3)
                    give_trig_eth('MR13', '1')
                else:
                    print('NG1')
                    judgment = 'NG: '
                    ngst = 'NG: '
                    for i in range(len(NG_list)):
                        print('NG: {} sebanyak {} di section{}'.format(NG_list[i], NG_num[i], NG_sect[i]))
                        ngst = ngst + ' ; ' + NG_list[i] + " di section {}".format(NG_sect[i])
                    zmqo_aio_ng.imsend({'ng': NG_list, 'section': NG_sect}, NG_img[0])
                    zmqo.imsend(ngst, img3)
                    print('NG2')
                    if D78 == '1' or D26 == '1':
                        print('NG3')
                        give_trig_eth('MR14', '1')
                    else:
                        give_trig_eth('MR14', '1')
                zmqo_save.imsend(judgment, img1)
                slist1.clear()
                slist2.clear()
                slist3.clear()
                slist4.clear()
                slist5.clear()
                slist6.clear()
                blist1.clear()
                blist2.clear()
                blist3.clear()
                blist4.clear()
                blist5.clear()
                blist6.clear()
                ilist1.clear()
                ilist2.clear()
                ilist3.clear()
                ilist4.clear()
                ilist5.clear()
                ilist6.clear()


def detection(img, sec, n):
    ori, pic, stat_list, boxes = do_detect(img)  # boxes dalam int

    if len(stat_list) < 1:
        pred = "OK"
        stat_list = ['OK']
        boxes = []
        pics = ['OK']
    else:
        pred = "NG"
        pics = pic

    pkt = {"sec": sec}
    zmqo_save.imsend(pkt, ori)
    print(sec + pred + str(n))
    zmqo.imsend(sec + pred + str(n), pic)
    return stat_list, boxes, pics


def mainprocess(listS1, listS2, listS3, listB1, listB2, listB3, listi1, listi2, listi3, scs, n, Pic1, Pic2, Pic3):
    start = time.time()
    res1, box1, img1 = detection(Pic1, scs[0], n)
    res2, box2, img2 = detection(Pic2, scs[1], n)
    res3, box3, img3 = detection(Pic3, scs[2], n)
    print(f'waktu detek: {time.time() - start}')
    listS3.append(res3)
    listB3.append(box3)
    listS1.append(res1)
    listS2.append(res2)
    listB1.append(box1)
    listB2.append(box2)
    listi1.append(img1)
    listi2.append(img2)
    listi3.append(img3)


def mainprocess2(listS2, listS3, listB2, listB3, listi2, listi3, scs, n, Pic1, Pic2, Pic3):
    zmqo.imsend("3", Pic1)
    res2, box2, img2 = detection(Pic2, scs[0], n)
    res3, box3, img3 = detection(Pic3, scs[1], n)
    listS3.append(res3)
    listB3.append(box3)
    listS2.append(res2)
    listB2.append(box2)
    listi2.append(img2)
    listi3.append(img3)
