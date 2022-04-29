#!/usr/bin/python3
# -*- coding: utf-8 -*-
import os, time
import numpy as np
import openpyxl, cv2, sys
from HandleRAW_UI import Ui_MainWindow
from PyQt5 import QtGui, QtCore, QtWidgets
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtGui import QTextCursor
from matplotlib import pyplot as plt

try_raw_path = r'D:\Python\Project\Ref_Data\RAWtestseria-0\20220427_000800_218397_0.raw'


# 11030080 = 320*34469 uint8
# 5515040  = 320*34469 uint16

class HandleRAW_UI(QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None):  # parent=None,so the HaiTu_UI is the topmost window
        super(HandleRAW_UI, self).__init__(
            parent)  # the super().__init__() excutes the constructor fo father, then we can use the property of father
        self.raw_stdev = None
        self.raw_ave = None
        self.frame_list = None
        self.first_raw = None
        self.raw_file_list = None
        self.file_list = None
        self.file_path = None
        self.display_ave_flag = False
        self.display_stdev_flag = False
        self.plot_wave_flag = False
        self.init()

    def init(self):
        self.setupUi(myWindow)
        myWindow.setWindowTitle('海图')
        self.buttonORaction()

    # All Button Event
    def buttonORaction(self):
        self.pushButton.clicked.connect(lambda: HandleRAW_UI.start_handle(self))
        self.actionOpen.triggered.connect(lambda: HandleRAW_UI.openFileEvent(self))
        self.plot_wave.clicked.connect(lambda: HandleRAW_UI.plot_wave(self))
        self.display_ave.clicked.connect(lambda: HandleRAW_UI.display_ave(self))
        self.display_stdev.clicked.connect(lambda: HandleRAW_UI.display_stdev(self))

    def openFileEvent(self):
        self.file_path = QFileDialog.getExistingDirectory(None, 'Choose Folder',
                                                          r'D:\PythonProject\PyTool_HandleRAW')  # return value is tuple type
        self.file_list = os.listdir(self.file_path)
        self.raw_file_list = list()
        for list_loop in range(len(self.file_list)):
            if '.raw' in self.file_list[list_loop]:
                self.raw_file_list.append(self.file_list[list_loop])
        self.textEdit.append(str(self.file_path))
        self.textEdit.append('\r\n')
        self.textEdit.append('Ready......')
        self.textEdit.append('\r\n')

    def start_handle(self):
        self.textEdit.append('Start calculation......')
        time_start = time.time()
        self.handle_raw()
        time_end = time.time()
        time_take = time_end - time_start
        self.textEdit.append('\r\n')
        self.textEdit.append('----Finished!!!----')
        self.textEdit.append('Take time:' + str(time_take))
        self.textEdit.append(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
        self.textEdit.append('\r\n')

    def handle_raw(self):
        AREA = [500, 500, 1500, 1500]
        np.set_printoptions(precision=3)
        rows = 2064  # image row is V:2064     2064*2672 = 5515008
        cols = 2672  # image column is H:2672
        channels = 1  # image channel, the gray is 1
        slice_start = 32
        slice_end = rows * cols
        Frame_count = 32
        raw_sum = np.zeros((AREA[2] - AREA[0], AREA[3] - AREA[1]), dtype=np.uint8)
        raw_stdev = np.zeros((AREA[2] - AREA[0], AREA[3] - AREA[1]), dtype=np.uint8)
        raw_median = np.zeros((AREA[2] - AREA[0], AREA[3] - AREA[1]), dtype=np.uint8)
        # raw_mean = np.zeros((rows, cols), dtype=np.uint16)
        frame_list = list()
        raw_median_list = [[0 for col in range(len(self.raw_file_list))] for row in
                           range((AREA[2] - AREA[0]) * (AREA[3] - AREA[1]))]
        for file_loop in range(len(self.raw_file_list)):
            raw_file = self.file_path + '\\' + self.raw_file_list[file_loop]
            total_pixels = np.fromfile(raw_file, dtype='uint8')
            total_pixels = total_pixels[slice_start:slice_end + slice_start]
            # print(img)
            # print(len(img))
            total_pixels = total_pixels.reshape(rows, cols)
            # raw_sum = raw_sum + total_pixels
            # choose the partial area
            choose_pixels = total_pixels[(AREA[0]):(AREA[2]), (AREA[1]):(AREA[3])]
            # print('choose_pixels:', choose_pixels)
            raw_sum = raw_sum + choose_pixels
            frame_list.append(np.mean(choose_pixels))
            if file_loop == 0:
                self.first_raw = choose_pixels

            ###########################################################
            # use two dimensional list to note the every pixel value
            ###########################################################
            xy_axis = 0
            for x_axis in range(AREA[2] - AREA[0]):
                for y_axis in range(AREA[3] - AREA[1]):
                    raw_median_list[xy_axis][file_loop] = choose_pixels[x_axis, y_axis]
                    xy_axis += 1
        self.frame_list = frame_list
        # calculation numpy -- raw median value  -- time
        xy_axis = 0
        raw_median_list2np = []
        for x_axis in range(AREA[2] - AREA[0]):
            raw_median_list2np.append([])
            for y_axis in range(AREA[3] - AREA[1]):
                raw_median_list2np[x_axis].append(np.median(raw_median_list[xy_axis]))
                xy_axis += 1
        # print('raw_median_list2np:',raw_median_list2np)
        raw_median = np.array(raw_median_list2np)

        #######################################################
        # calculation numpy -- raw average -- time
        #######################################################
        self.raw_ave = raw_sum / Frame_count
        # print('raw_ave:', raw_ave)
        # print('frame_list:', frame_list)

        ###########################################################
        # calculation numpy -- raw stdev -- time
        ###########################################################
        for file_loop in range(len(self.raw_file_list)):
            raw_file = self.file_path + '\\' + self.raw_file_list[file_loop]
            total_pixels = np.fromfile(raw_file, dtype='uint8')
            total_pixels = total_pixels[slice_start:slice_end + Frame_count]
            total_pixels = total_pixels.reshape(rows, cols)
            # choose the partial area
            choose_pixels = total_pixels[(AREA[0]):(AREA[2]), (AREA[1]):(AREA[3])]
            raw_stdev = raw_stdev + (self.raw_ave - choose_pixels) ** 2
        self.raw_stdev = np.sqrt(raw_stdev / (Frame_count - 1))
        # print('raw_stdev:', raw_stdev)

        ###########################################################
        # calculation numpy -- space  --  signal row data base on upper cal
        ###########################################################
        # signal raw data -> signal average
        # step1: numpy average calculation base on the before average data of raw data
        ave_value = np.mean(self.raw_ave)
        self.textEdit.append('Average Value:' + str(ave_value))
        ###-----------------------------------------------------###
        # signal raw data -> signal median
        # step1: 2 dimensional convert to 1 dimensional
        # step2: numpy median operation
        median_value = np.median(raw_median.flatten())
        self.textEdit.append('Median Value:' + str(median_value))
        ###-----------------------------------------------------###
        # signal raw data -> signal stander dev
        # step1: 2 dimensional convert to 1 dimensional
        # step2: numpy standard deviation operation
        std_dev_value = np.std(raw_stdev.flatten())
        self.textEdit.append('Standard Deviation Value:' + str(std_dev_value))
        ###-----------------------------------------------------###
        self.display_ave_flag = True
        self.display_stdev_flag = True
        self.plot_wave_flag = True
        print(self.first_raw)
        print('Finished')

    def display_ave(self):
        if self.display_ave_flag:
            cv2.imshow('RAW_Average', self.raw_ave)
            # cv2.namedWindow('RAW_Average', cv2.WINDOW_NORMAL)
            cv2.waitKey()
            cv2.destroyAllWindows()
        else:
            self.textEdit.append('Please Choose File and Click Start Button!!!')

    def display_stdev(self):
        if self.display_stdev_flag:
            cv2.imshow('RAW_Standard Deviation', self.raw_stdev)
            # cv2.namedWindow('RAW_Standard Deviation', cv2.WINDOW_NORMAL)
            cv2.waitKey()
            cv2.destroyAllWindows()
        else:
            self.textEdit.append('Please Choose File and Click Start Button!!!')

    def plot_wave(self):
        if self.plot_wave_flag:
            plt.xlabel("Frame NO.")
            plt.ylabel("Mean Value")
            plt.title("The every frame's mean value")
            x = list(range(len(self.frame_list)))
            for i in range(len(self.frame_list)):
                plt.plot(x, self.frame_list, color='r')
            plt.show()
        else:
            self.textEdit.append('Please Choose File and Click Start Button!!!')


if __name__ == '__main__':
    app = QApplication(sys.argv)
    myWindow = QMainWindow()
    HTUI = HandleRAW_UI()
    myWindow.show()
    sys.exit(app.exec_())

    # a = np.arange(16).reshape(4, 4)
    # print(a)
    # print(a[1: 3, 1: 3])
    # s = []  # 创建一个空列表

    # s = [[0 for col in range(12)] for row in range(6)]
    # print(s)
    # for k in range(12):
    #     for i in range(3):  # 创建一个5行的列表（行）
    #         for j in range(4):  # 循环每一行的每一个元素（列）
    #             s[i+j][k] = i+j+k  # 为内层列表添加元素
    # print(s)

    # qaz = [1,2,3,4,5,6,7,8,9]
    # arr = np.array(qaz)
    # arr.reshape(3,3)
    # print(arr)
