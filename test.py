import os

import cv2
from PIL import Image as im
import numpy as np
from numba import jit, objmode
import time

'''
author：Mars
function：将1600x1200的raw图显示出来
res：cwf__1600x1200_10_3.raw

step1：
    将raw数据通过numpy的fromfile()函数以uint16读入，读入后是一个size为1600x1200的1维数组
    Tip：因为raw数据是AD10bit，所以要用uint16
step2：
    将数组reshape成1200x1600，因为图像是按1200x1600结构存储的
step3：
    将图像从10bit转成8bit。
    Question：为什么要转成8bit输出
    10bit输出时画面PIL.image.show()会过曝，猜测show()是按YUV 8bit显示的。
step4：
    通过PIL的image类的fromarray()函数将数组转成图像输出
'''
rawPath = r'D:\Python\Project\PyTool_HandleRAW\1000.raw'
imgSize = (2064, 2672)

def cvTest():

    # step1：
    rawData = np.fromfile(rawPath, dtype='>u2')
    print(np.shape(rawData))  # 1920000

    # step2：
    reshapeRawData = np.reshape(rawData[32:], imgSize)

    # step3：
    for i in range(reshapeRawData.shape[0]):
        for j in range(reshapeRawData.shape[1]):
            # 将10bit数转成8bit
            val = np.round(reshapeRawData[i][j] >> 6)
            if val >= 255:
                reshapeRawData[i][j] = 255
            elif val <= 0:
                reshapeRawData[i][j] = 0
            else:
                reshapeRawData[i][j] = val

    print(reshapeRawData.max())  # 200
    print(reshapeRawData.min())  # 3

    img = im.fromarray(reshapeRawData)

    img.show()
    # cv2.imshow(img)
    # cv2.waitKey()
    # cv2.destroyAllWindows()


def transfer_16bit_to_8bit():
    # image_16bit = cv2.imread(image_path, cv2.IMREAD_UNCHANGED)
    image_16bit = np.fromfile(rawPath, dtype='>u2')  # >u2
    image_16bit = np.reshape(image_16bit[32:], imgSize)
    min_16bit = np.min(image_16bit)
    max_16bit = np.max(image_16bit)
    # image_8bit = np.array(np.rint((255.0 * (image_16bit - min_16bit)) / float(max_16bit - min_16bit)), dtype=np.uint8)
    # 或者下面一种写法
    image_8bit = np.array(np.rint(255 * ((image_16bit - min_16bit) / (max_16bit - min_16bit))), dtype=np.uint8)
    print(image_16bit.dtype)
    print('16bit dynamic range: %d - %d' % (min_16bit, max_16bit))
    print(image_8bit.dtype)
    print('8bit dynamic range: %d - %d' % (np.min(image_8bit), np.max(image_8bit)))

    img = im.fromarray(image_8bit)
    img.show()

# class niubi():
@jit(nopython=True)
def cal_pypy(x, y):
    with objmode(tt='f8'):
        tt = time.time()
    sumtt = 0
    for i in range(x, y):
        sumtt += 1
    with objmode(endt='f8'):
        endt = time.time() - tt
    print('sumtt =', sumtt)
    print('cal_pypy time:', endt)

def cal_cpy(x, y):
    tt = time.time()
    sumtt = 0
    for i in range(x, y):
        sumtt += 1
    endt = time.time() - tt
    print('sumtt =', sumtt)
    print('cal_pypy time:', endt)


from multiprocessing import Process
import time


def task1():
    print("正在听音乐")
    print(os.getpid())
    time.sleep(1)


def task2():
    print("正在编程......")
    print(os.getpid())
    time.sleep(0.5)


def no_multi():
    task1()
    task2()


def use_multi():
    p1 = Process(target=task1)
    p2 = Process(target=task2)
    p1.start()
    p2.start()
    p1.join()
    p2.join()

    # p.join()  阻塞当前进程， 当p1.start()之后， p1就提示主进程， 需要等待p1进程执行结束才能向下执行， 那么主进程就乖乖等着， 自然不会执行p2.start()
    # [process.join() for process in processes]

def tttfor():
    x=10000
    y=10000
    t1 = time.time()
    for i in range(100000000):
        i += 1
    print(time.time() - t1)

if __name__ == '__main__':
    tttfor()