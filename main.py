#!/usr/bin/python3
# -*- coding: utf-8 -*-
import os, time, cv2, sys
import numpy as np
from HandleRAW_UI import Ui_MainWindow
from PyQt5.QtWidgets import *
from matplotlib import pyplot as plt
import pandas as pd
import struct, openpyxl

try_raw_path = r'D:\Python\Project\Ref_Data\RAWtestseria-0\20220427_000800_218397_0.raw'

# 11030080 = 320*34469 uint8
# 5515040  = 320*34469 uint16

class HandleRAW_UI(QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None):  # parent=None,so the HaiTu_UI is the topmost window
        super(HandleRAW_UI, self).__init__(
            parent)  # the super().__init__() excutes the constructor fo father, then we can use the property of father
        # self.GR_stdev_list = None
        # self.B_stdev_list = None
        # self.R_stdev_list = None
        # self.GB_median_list = None
        # self.GR_median_list = None
        # self.B_median_list = None
        # self.R_median_list = None
        # self.GB_ave_list = None
        # self.GB_stdev_list = None
        # self.GR_ave_list = None
        # self.B_ave_list = None
        # self.R_ave_list = None
        self.note_data = None
        self.light_list = None
        self.folder_list = None
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
        # self.handle_raw_single()
    def init(self):
        self.setupUi(myWindow)
        myWindow.setWindowTitle('海图')
        self.buttonORaction()

    # All Button Event
    def buttonORaction(self):
        self.pushButton.clicked.connect(lambda: HandleRAW_UI.start_handle(self))
        self.actionOpen.triggered.connect(lambda: HandleRAW_UI.openFileEvent(self))
        # self.plot_wave.clicked.connect(lambda: HandleRAW_UI.plot_wave(self))
        self.display_ave.clicked.connect(lambda: HandleRAW_UI.display_ave(self))
        self.display_stdev.clicked.connect(lambda: HandleRAW_UI.display_stdev(self))

    def openFileEvent(self):
        self.raw_file_list = list()
        self.folder_list = []
        folder_name_list = []
        try:
            print('get folder')
            self.file_path = QFileDialog.getExistingDirectory(None, 'Choose Folder',
                                                            r'D:\PythonProject')  # return value is tuple type
        except Exception as e:
            print(e.args)
            print(str(e))
            print(repr(e))
        print(self.file_path)
        for root, dirs, files in os.walk(self.file_path):
            for dir in dirs:
                folder_name_list.append(dir)
                if os.path.join(root, dir):
                    self.folder_list.append(os.path.join(root, dir))
        folder_name_list = self.folder_list
        # sort the list with the back number
        folder_pd = pd.DataFrame([i.split('-') for i in folder_name_list])
        folder_pd[1] = folder_pd[1].astype(int)
        # get the Light Intensity, put into list, sort them.
        self.light_list = folder_pd[1].tolist()
        self.light_list.sort()
        folder_pd = folder_pd.sort_values(by=1, ascending=True)
        folder_pd = folder_pd.values.tolist()
        self.folder_list = []
        for i in range(len(folder_pd)):
            self.folder_list.append(folder_pd[i][0] + '-' + str(folder_pd[i][1]))
        print(self.folder_list)
        self.start_handle()

    def start_handle(self):
        print('I am Working......')
        self.textEdit.append('Start calculation......')
        time_start = time.time()
        note_path = str(self.file_path + '/Note_data_' + time.strftime("%Y%m%d%H%M%S", time.localtime()) + '.txt')
        self.note_data = open(note_path, 'w')
        self.handlePathOrFile()
        time_end = time.time()
        self.textEdit.append('\r\n')
        self.textEdit.append('----Finished!!!----')
        self.textEdit.append('Take time:' + str(time_end - time_start) + ' S')
        self.textEdit.append(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
        self.textEdit.append('\r\n')
        print('All Finished')

    def handlePathOrFile(self):
        # get_RGB_Result_list order:
        # GB_median,B_median,R_median,GR_median,GB_ave,B_ave,R_ave,GR_ave,GB_stdev,B_stdev,R_stdev,GR_stdev
        self.R_ave_list = []
        self.B_ave_list = []
        self.GR_ave_list = []
        self.GB_ave_list = []
        self.R_median_list = []
        self.B_median_list = []
        self.GR_median_list = []
        self.GB_median_list = []
        self.R_stdev_list = []
        self.B_stdev_list = []
        self.GR_stdev_list = []
        self.GB_stdev_list = []
        get_RGB_Result_list = []
        for folder in self.folder_list:
            # print(os.listdir(folder))
            raw_file_list = []
            self.file_list = os.listdir(folder)
            for list_loop in range(len(self.file_list)):
                if '.raw' in self.file_list[list_loop]:
                    self.raw_file_list.append(self.file_list[list_loop])
                    raw_file_list.append(self.file_list[list_loop])
            self.textEdit.append(str(folder))
            self.textEdit.append('\r\n')
            # self.textEdit.append('Ready......')
            # self.textEdit.append('\r\n')

            get_RGB_Result_list = self.handle_raw(folder, raw_file_list)
            self.GB_median_list.append(get_RGB_Result_list[0])
            self.B_median_list.append(get_RGB_Result_list[1])
            self.R_median_list.append(get_RGB_Result_list[2])
            self.GR_median_list.append(get_RGB_Result_list[3])
            self.GB_ave_list.append(get_RGB_Result_list[4])
            self.B_ave_list.append(get_RGB_Result_list[5])
            self.R_ave_list.append(get_RGB_Result_list[6])
            self.GR_ave_list.append(get_RGB_Result_list[7])
            self.GB_stdev_list.append(get_RGB_Result_list[8])
            self.B_stdev_list.append(get_RGB_Result_list[9])
            self.R_stdev_list.append(get_RGB_Result_list[10])
            self.GR_stdev_list.append(get_RGB_Result_list[11])

        # print(self.GB_median_list)
        # print(self.B_median_list)
        # print(self.R_median_list)
        # print(self.GR_median_list)
        # print(self.GB_ave_list)
        # print(self.B_ave_list)
        # print(self.R_ave_list)
        # print(self.GR_ave_list)
        # print(self.GB_stdev_list)
        # print(self.B_stdev_list)
        # print(self.R_stdev_list)
        # print(self.GR_stdev_list)
        self.ttt_plot_wave()


    def handle_raw(self, file_path, raw_file_list):
        AREA = [500, 500, 1500, 1500]
        RGB_Count_SUM = (AREA[2]-AREA[0])*(AREA[3]-AREA[1])/4
        np.set_printoptions(precision=3)
        rows = 2064  # image row is V:2064     2064*2672 = 5515008
        cols = 2672  # image column is H:2672
        channels = 1  # image channel, the gray is 1
        slice_start = 32
        slice_end = rows * cols
        Frame_count = 32
        RGB_Result_list = []
        raw_sum = np.zeros((AREA[2] - AREA[0], AREA[3] - AREA[1]), dtype=np.uint64)
        # raw_stdev = np.zeros((AREA[2] - AREA[0], AREA[3] - AREA[1]), dtype=np.uint16)
        # raw_median = np.zeros((AREA[2] - AREA[0], AREA[3] - AREA[1]), dtype=np.uint16)
        frame_list = list()
        raw_median_list = [[0 for col in range(len(raw_file_list))] for row in
                           range((AREA[2] - AREA[0]) * (AREA[3] - AREA[1]))]
        for file_loop in range(len(raw_file_list)):
            raw_file = file_path + '\\' + raw_file_list[file_loop]
            total_pixels = np.fromfile(raw_file, dtype='>u2')
            total_pixels = np.reshape(np.right_shift(total_pixels[slice_start:], 2), [rows, cols])
            # choose the partial area
            choose_pixels = total_pixels[(AREA[0]):(AREA[2]), (AREA[1]):(AREA[3])]
            #raw_sum is the sum of 32 frame
            raw_sum = raw_sum + choose_pixels
            frame_list.append(np.mean(choose_pixels))
            if file_loop == 0:
                self.first_raw = choose_pixels
            ###################################################################
            # use two dimensional list([[32 data, because 32 frame]every pixel for single frame ]) to note the every pixel value
            ###################################################################
            xy_axis = 0
            for x_axis in range(AREA[2] - AREA[0]):
                for y_axis in range(AREA[3] - AREA[1]):
                    raw_median_list[xy_axis][file_loop] = choose_pixels[x_axis, y_axis]
                    xy_axis += 1
        self.frame_list = frame_list
        ###################################################################
        # loop again calculation numpy -- raw median value  -- time
        ###################################################################
        xy_axis = 0
        raw_median_list2np = []
        for x_axis in range(AREA[2] - AREA[0]):
            raw_median_list2np.append([])
            for y_axis in range(AREA[3] - AREA[1]):
                raw_median_list2np[x_axis].append(np.median(raw_median_list[xy_axis]))
                xy_axis += 1
        # print('raw_median_list2np:', raw_median_list2np)
        raw_median = np.array(raw_median_list2np)
        ###-------------------------------------------------------------------###
        # CALCULATE: <<<<<<<<<<DIV R G B>>>>>>>>>>
        # base on raw_median(the median of all frames) calculate R G B median
        ###-------------------------------------------------------------------###
        GB_median_list_single = []
        B_median_list_single = []
        R_median_list_single = []
        GR_median_list_single = []
        for x_axis in range(int((AREA[2] - AREA[0])/2)):
            for y_axis in range(int((AREA[3] - AREA[1])/2)):
                GB_median_list_single.append(raw_median[2*x_axis + 0, 2*y_axis + 0])
                B_median_list_single.append(raw_median[2*x_axis + 0, 2*y_axis + 1])
                R_median_list_single.append(raw_median[2*x_axis + 1, 2*y_axis + 0])
                GR_median_list_single.append(raw_median[2*x_axis + 1, 2*y_axis + 1])
        GB_median = np.median(GB_median_list_single)
        B_median = np.median(B_median_list_single)
        R_median = np.median(R_median_list_single)
        GR_median = np.median(GR_median_list_single)
        RGB_Result_list.extend([GB_median, B_median, R_median, GR_median])
        ###################################################################
        # calculation numpy -- raw average -- time
        ###################################################################
        self.raw_ave = raw_sum / Frame_count
        # print('raw_ave:', self.raw_ave)
        # print('frame_list:', frame_list)
        ###-------------------------------------------------------------------###
        # CALCULATE: <<<<<<<<<<DIV R G B>>>>>>>>>>
        # calculation numpy -- raw average for every pixel()
        # GB  B
        # R   GR
        ###-------------------------------------------------------------------###
        GB_sum = 0
        B_sum = 0
        R_sum = 0
        GR_sum = 0
        RGB_RAW_AVE = raw_sum / Frame_count
        # print('RGB_RAW_AVE:',RGB_RAW_AVE)
        # **_sum is the sum value of every color(GR GB R B)
        for x_axis in range(int((AREA[2] - AREA[0])/2)):
            for y_axis in range(int((AREA[3] - AREA[1])/2)):
                GB_sum = GB_sum + RGB_RAW_AVE[2*x_axis + 0, 2*y_axis + 0]
                B_sum = B_sum + RGB_RAW_AVE[2*x_axis + 0, 2*y_axis + 1]
                R_sum = R_sum + RGB_RAW_AVE[2*x_axis + 1, 2*y_axis + 0]
                GR_sum = GR_sum + RGB_RAW_AVE[2*x_axis + 1, 2*y_axis + 1]
        GB_ave = GB_sum / RGB_Count_SUM
        B_ave = B_sum / RGB_Count_SUM
        R_ave = R_sum / RGB_Count_SUM
        GR_ave = GR_sum / RGB_Count_SUM
        RGB_Result_list.extend([GB_ave, B_ave, R_ave, GR_ave])
        ###################################################################
        # calculation numpy -- raw stdev -- time
        ###################################################################
        raw_stdev = 0
        for file_loop in range(len(raw_file_list)):
            raw_file = file_path + '\\' + raw_file_list[file_loop]
            total_pixels = np.fromfile(raw_file, dtype='>u2')
            total_pixels = np.reshape(np.right_shift(total_pixels[slice_start:], 2), [rows, cols])
            # choose the partial area
            choose_pixels = total_pixels[(AREA[0]):(AREA[2]), (AREA[1]):(AREA[3])]
            raw_stdev = raw_stdev + (self.raw_ave - choose_pixels) ** 2
        self.raw_stdev = np.sqrt(raw_stdev / Frame_count)
        # print('raw_stdev:', self.raw_stdev)
        ###-------------------------------------------------------------------###
        # CALCULATE: <<<<<<<<<<DIV R G B>>>>>>>>>>
        ###-------------------------------------------------------------------###
        GB_stdev_list_single = []
        B_stdev_list_single = []
        R_stdev_list_single = []
        GR_stdev_list_single = []
        for x_axis in range(int((AREA[2] - AREA[0])/2)):
            for y_axis in range(int((AREA[3] - AREA[1])/2)):
                GB_stdev_list_single.append(self.raw_stdev[2*x_axis + 0, 2*y_axis + 0])
                B_stdev_list_single.append(self.raw_stdev[2*x_axis + 0, 2*y_axis + 1])
                R_stdev_list_single.append(self.raw_stdev[2*x_axis + 1, 2*y_axis + 0])
                GR_stdev_list_single.append(self.raw_stdev[2*x_axis + 1, 2*y_axis + 1])
        GB_stdev = np.std(GB_stdev_list_single)
        B_stdev = np.std(B_stdev_list_single)
        R_stdev = np.std(R_stdev_list_single)
        GR_stdev = np.std(GR_stdev_list_single)
        RGB_Result_list.extend([GB_stdev, B_stdev, R_stdev, GR_stdev])
        ###################################################################
        # CALCULATE: <<<<<<<<<<MIX R G B>>>>>>>>>>
        # calculation numpy -- space  --  signal row data base on upper cal
        ###################################################################
        # signal raw data -> signal average
        # step1: numpy average calculation base on the before average data of raw data
        # ave_value = np.mean(self.raw_ave)
        # self.textEdit.append('Average Value:' + str(ave_value))
        ###-----------------------------------------------------###
        # signal raw data -> signal median
        # step1: 2 dimensional convert to 1 dimensional
        # step2: numpy median operation
        # median_value = np.median(raw_median.flatten())
        # self.textEdit.append('Median Value:' + str(median_value))
        ###-----------------------------------------------------###
        # signal raw data -> signal stander dev
        # step1: 2 dimensional convert to 1 dimensional
        # step2: numpy standard deviation operation
        # std_dev_value = np.std(self.raw_stdev.flatten())
        # self.textEdit.append('Standard Deviation Value:' + str(std_dev_value))
        ###-----------------------------------------------------###
        self.display_ave_flag = True
        self.display_stdev_flag = True
        self.plot_wave_flag = True
        # print(self.first_raw)
        # print('Finished')
        # print('RGB_Result_list:', RGB_Result_list)
        return RGB_Result_list

##===============================================================
    def handle_raw_single(self):
        print('working')
        AREA = [500, 500, 1500, 1500]
        RGB_Count_SUM = (AREA[2]-AREA[0])*(AREA[3]-AREA[1])/4
        np.set_printoptions(precision=3)
        rows = 2064  # image row is V:2064     2064*2672 = 5515008
        cols = 2672  # image column is H:2672
        channels = 1  # image channel, the gray is 1
        slice_start = 32
        slice_end = rows * cols
        Frame_count = 32
        ######numpy
        total_pixels = np.fromfile(r'D:\Python\Project\PyTool_HandleRAW\700.raw', dtype='>u2')
        print('total_pixels:',total_pixels)
        array_data_dec = np.reshape(np.right_shift(total_pixels[32:], 2), [rows, cols])
        print('array_data_dec:', array_data_dec)
        ######open file read binary
        total_pixels = open(r'D:\Python\Project\PyTool_HandleRAW\700.raw', 'rb')
        data = total_pixels.read()
        # write_data = open(r'D:\Python\Project\PyTool_HandleRAW\rawdata.txt', 'w')
        # write_data.write('total_pixels')
        # print('data:', data)
        data_dec = struct.unpack('>' + int(len(data) / 2) * 'H', data)
        # print('data_dec:', data_dec)
        array_data_dec = np.reshape(np.right_shift(data_dec[32:], 2), [rows, cols])
        print('array_data_dec:', array_data_dec)
        ####### common
        number = array_data_dec.size  # 计算 X 中所有元素的个数
        X_row = np.size(array_data_dec, 0)  # 计算 X 的行数
        X_col = np.size(array_data_dec, 1)  # 计算 X 的列数
        print("number:", number)
        print("X_row:", X_row)
        print("X_col:", X_col)
        np.savetxt(r'D:\Python\Project\Ref_Data\np_raw2txt.txt',array_data_dec)
        # data_out = np.fromfile(r'D:\Python\Project\Ref_Data\np_raw2txt.txt', dtype=np.int32)
        # data_out = data_out.reshape(rows, cols)
        # print(data_out)


        # txt = open(r'D:\Python\Project\Ref_Data\np_raw2txt.txt', '+w')
        # txt.write(str(data))

        # total_pixels = total_pixels/4
        # total_pixels = total_pixels[slice_start:slice_end + slice_start]
        # total_pixels = total_pixels.reshape(rows, cols)
        # # choose the partial area
        # choose_pixels = total_pixels[(AREA[0]):(AREA[2]), (AREA[1]):(AREA[3])]

        # np.savetxt(r'D:\Python\Project\Ref_Data\np_raw2txt.txt', total_pixels)
        print('finished')
##===============================================================

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

    def ttt_plot_wave(self):
        print('Plotting')
        # The follow parameter need to plot waveform y-axis:R B GR GB; x-axis:Average/Median/Standard deviation
        R_ave_list = [round(i, 2) for i in self.R_ave_list]
        B_ave_list = [round(i, 2) for i in self.B_ave_list]
        GR_ave_list = [round(i, 2) for i in self.GR_ave_list]
        GB_ave_list = [round(i, 2) for i in self.GB_ave_list]
        R_median_list = self.R_median_list
        B_median_list = self.B_median_list
        GR_median_list = self.GR_median_list
        GB_median_list = self.GB_median_list
        R_stdev_list = [round(i, 2) for i in self.R_stdev_list]
        B_stdev_list = [round(i, 2) for i in self.B_stdev_list]
        GR_stdev_list = [round(i, 2) for i in self.GR_stdev_list]
        GB_stdev_list = [round(i, 2) for i in self.GB_stdev_list]

        R_ave_dict = {}
        B_ave_dict = {}
        GR_ave_dict = {}
        GB_ave_dict = {}
        R_median_dict = {}
        B_median_dict = {}
        GR_median_dict = {}
        GB_median_dict = {}
        R_stdev_dict = {}
        B_stdev_dict = {}
        GR_stdev_dict = {}
        GB_stdev_dict = {}
        # light_list_y = [self.light_list[0], 50, self.light_list[-1]]
        # merge two list(x is Light Intensity, y is the measured value)
        for i, j in zip(self.light_list, R_ave_list):
            R_ave_dict[i] = j
        for i, j in zip(self.light_list, B_ave_list):
            B_ave_dict[i] = j
        for i, j in zip(self.light_list, GR_ave_list):
            GR_ave_dict[i] = j
        for i, j in zip(self.light_list, GB_ave_list):
            GB_ave_dict[i] = j
        for i, j in zip(self.light_list, R_median_list):
            R_median_dict[i] = j
        for i, j in zip(self.light_list, B_median_list):
            B_median_dict[i] = j
        for i, j in zip(self.light_list, GR_median_list):
            GR_median_dict[i] = j
        for i, j in zip(self.light_list, GB_median_list):
            GB_median_dict[i] = j
        for i, j in zip(self.light_list, R_stdev_list):
            R_stdev_dict[i] = j
        for i, j in zip(self.light_list, B_stdev_list):
            B_stdev_dict[i] = j
        for i, j in zip(self.light_list, GR_stdev_list):
            GR_stdev_dict[i] = j
        for i, j in zip(self.light_list, GB_stdev_list):
            GB_stdev_dict[i] = j
        # write the data to txt file
        self.note_data.write('R_ave')
        self.note_data.write(str(R_ave_dict))
        self.note_data.write('\r')
        self.note_data.write('B_ave')
        self.note_data.write(str(B_ave_dict))
        self.note_data.write('\r')
        self.note_data.write('GR_ave')
        self.note_data.write(str(GR_ave_dict))
        self.note_data.write('\r')
        self.note_data.write('GB_ave')
        self.note_data.write(str(GB_ave_dict))
        self.note_data.write('\r')
        self.note_data.write('R_median')
        self.note_data.write(str(R_median_dict))
        self.note_data.write('\r')
        self.note_data.write('B_median')
        self.note_data.write(str(B_median_dict))
        self.note_data.write('\r')
        self.note_data.write('GR_median')
        self.note_data.write(str(GR_median_dict))
        self.note_data.write('\r')
        self.note_data.write('GB_median')
        self.note_data.write(str(GB_median_dict))
        self.note_data.write('\r')
        self.note_data.write('R_stdev')
        self.note_data.write(str(R_stdev_dict))
        self.note_data.write('\r')
        self.note_data.write('B_stdev')
        self.note_data.write(str(B_stdev_dict))
        self.note_data.write('\r')
        self.note_data.write('GR_stdev')
        self.note_data.write(str(GR_stdev_dict))
        self.note_data.write('\r')
        self.note_data.write('GB_stdev')
        self.note_data.write(str(GB_stdev_dict))
        self.note_data.write('\r')
        self.note_data.close()  # close is saving
        fig = plt.figure(figsize=(25, 20))
        # fig.autofmt_xdate()
        # x = list(range(len(self.R_ave_list)))
        # my_x_ticks = np.arange(self.light_list[0], 50, self.light_list[-1])
        # plt.xticks(my_x_ticks)
        # plt.legend(loc='upper left', ncol=1)  # 图例及位置： 1右上角，2 左上角 loc函数可不写 0为最优 ncol为标签有几列
        ##################################################################
        Average = fig.add_subplot(3, 1, 1)
        plt.xlabel("Light Intensity")
        plt.ylabel("Average Value")
        plt.title("RGB & Light Intensity")
        # for i in range(len(self.R_ave_list)):
        #     Average.plot(x, R_ave_list, color='r', marker='o')
        #     Average.plot(x, B_ave_list, color='b', marker='v')
        #     Average.plot(x, GR_ave_list, color='gold', marker='p')
        #     Average.plot(x, GB_ave_list, color='mediumseagreen', marker='d')
        x = [i for i in R_ave_dict.keys()]
        y = [i for i in R_ave_dict.values()]
        plt.plot(x, y, color='r', label='R_ave', marker='o')
        x = [i for i in B_ave_dict.keys()]
        y = [i for i in B_ave_dict.values()]
        plt.plot(x, y, color='b', label='B_ave', marker='v')
        x = [i for i in GR_ave_dict.keys()]
        y = [i for i in GR_ave_dict.values()]
        plt.plot(x, y, color='gold', label='GR_ave', marker='p')
        x = [i for i in GB_ave_dict.keys()]
        y = [i for i in GB_ave_dict.values()]
        plt.plot(x, y, color='mediumseagreen', label='GB_ave', marker='d')
        plt.legend(['R_ave', 'B_ave', 'GR_ave', 'GB_ave'], loc='upper left')
        plt.xticks(self.light_list, self.light_list, rotation=270)
        ################################################################
        Median = fig.add_subplot(3, 1, 2)
        x = list(range(len(R_median_list)))
        plt.xlabel("Light Intensity")
        plt.ylabel("Median Value")
        plt.title("RGB & Light Intensity")
        # for i in range(len(R_median_list)):
        #     Median.plot(x, R_median_list, color='r')
        #     Median.plot(x, B_median_list, color='b')
        #     Median.plot(x, GR_median_list, color='gold')
        #     Median.plot(x, GB_median_list, color='mediumseagreen')
        x = [i for i in R_median_dict.keys()]
        y = [i for i in R_median_dict.values()]
        plt.plot(x, y, color='r', label='R_median', marker='o')
        x = [i for i in B_median_dict.keys()]
        y = [i for i in B_median_dict.values()]
        plt.plot(x, y, color='b', label='B_median', marker='v')
        x = [i for i in GR_median_dict.keys()]
        y = [i for i in GR_median_dict.values()]
        plt.plot(x, y, color='gold', label='GR_median', marker='p')
        x = [i for i in GB_median_dict.keys()]
        y = [i for i in GB_median_dict.values()]
        plt.plot(x, y, color='mediumseagreen', label='GB_median', marker='d')
        plt.legend(['R_median', 'B_median', 'GR_median', 'GB_median'], loc='upper left')
        plt.xticks(self.light_list, self.light_list, rotation=270)
        ##################################################################
        x = list(range(len(R_stdev_list)))
        Stdev = fig.add_subplot(3, 1, 3)
        plt.xlabel("Light Intensity")
        plt.ylabel("Standard Deviation  Value")
        plt.title("RGB & Light Intensity")
        # for i in range(len(R_stdev_list)):
        #     Stdev.plot(x, R_stdev_list, color='r')
        #     Stdev.plot(x, B_stdev_list, color='b')
        #     Stdev.plot(x, GR_stdev_list, color='gold')
        #     Stdev.plot(x, GB_stdev_list, color='mediumseagreen')
        x = [i for i in R_stdev_dict.keys()]
        y = [i for i in R_stdev_dict.values()]
        plt.plot(x, y, color='r', label='R_stdev', marker='o')
        x = [i for i in B_stdev_dict.keys()]
        y = [i for i in B_stdev_dict.values()]
        plt.plot(x, y, color='b', label='B_stdev', marker='v')
        x = [i for i in GR_stdev_dict.keys()]
        y = [i for i in GR_stdev_dict.values()]
        plt.plot(x, y, color='gold', label='GR_stdev', marker='p')
        x = [i for i in GB_stdev_dict.keys()]
        y = [i for i in GB_stdev_dict.values()]
        plt.plot(x, y, color='mediumseagreen', label='GB_stdev', marker='d')
        plt.legend(['R_stdev', 'B_stdev', 'GR_stdev', 'GB_stdev'], loc='upper left')
        plt.xticks(self.light_list, self.light_list, rotation=270)

        plt.subplots_adjust(left=None, bottom=None, right=None, top=None, wspace=None, hspace=0.5)
        plt.show()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    myWindow = QMainWindow()
    HTUI = HandleRAW_UI()
    myWindow.show()
    sys.exit(app.exec_())


    # Data_name = ['Light Intensity', 'R_ave', 'B_ave', 'GR_ave', 'GB_ave', 'R_median', 'B_median', 'GR_median',
    #              'GB_median', 'R_stdev', 'B_stdev', 'GR_stdev', 'GB_stdev']
    # c = {"name": Data_name}
    # df = pd.DataFrame(c,columns=['name'])
    # print(df)
    # imgData = np.fromfile(try_raw_path, dtype=np.uint16)
    # total_pixels = imgData[0:5515040]
    # total_pixels = total_pixels.reshape(160, 34469)
    # print(total_pixels)
    # np.savetxt(r'D:\Python\Project\Ref_Data\np_raw2txt.txt', total_pixels, fmt='%d', delimiter='\t')
    # cv2.imshow('RAW_Standard Deviation', total_pixels)
    # cv2.waitKey()
    # cv2.destroyAllWindows()

    # a = np.arange(16).reshape(4, 4)
    # print(a)
    # print(a[1, 1])
    # s = []  # 创建一个空列表

    # for i in range(3):
    #     print(i)

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

    # data = [
    #     [1, 2],
    #     [3, 2],
    #     [4, 7],
    #     [2, 4],
    #     ]
    # x, y = zip(*data)
    # plt.scatter(x, y)
    # plt.show()