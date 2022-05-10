#!/usr/bin/python3
# -*- coding: utf-8 -*-
import os, time, cv2, sys
import numpy as np
from HandleRAW_UI import Ui_MainWindow
from PyQt5.QtWidgets import *
from matplotlib import pyplot as plt
import pandas as pd
from PyQt5.QtCore import QThread, pyqtSignal, QDateTime, QObject

try_raw_path = r'D:\Python\Project\Ref_Data\RAWtestseria-0\20220427_000800_218397_0.raw'
folder_name_string_pattern1 = '0x'
folder_name_string_pattern2 = '0X'
filename_extension = '.raw'
# 11030080 = 320*34469 uint8
# 5515040  = 320*34469 uint16

class HandleRAW_UI(QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None):  # parent=None,so the HaiTu_UI is the topmost window
        super(HandleRAW_UI, self).__init__(
            parent)  # the super().__init__() excutes the constructor fo father, then we can use the property of father
        self.GR_stdev_list = None
        self.B_stdev_list = None
        self.R_stdev_list = None
        self.GB_median_list = None
        self.GR_median_list = None
        self.B_median_list = None
        self.R_median_list = None
        self.GB_ave_list = None
        self.GB_stdev_list = None
        self.GR_ave_list = None
        self.B_ave_list = None
        self.R_ave_list = None
        self.ticks = None
        self.labels = None
        self.x_axis_label = None
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

    def init(self):
        self.setupUi(myWindow)
        myWindow.setWindowTitle('海图_RAW Analysis Tool')
        self.buttonORaction()

        # # create thread
        # self.thread = QThread()
        # self.backend = BackendThread()
        # # connect signal
        # self.backend.update_date.connect(self.handleDisplay)
        # self.backend.moveToThread(self.thread)
        # # start thread
        # self.thread.started.connect(self.backend.run)
        # self.thread.start()

    # All Button Event
    def buttonORaction(self):
        self.pushButton.clicked.connect(lambda: HandleRAW_UI.openFileEvent(self))
        # self.actionOpen.triggered.connect(lambda: HandleRAW_UI.openFileEvent(self))
        self.plot_wave.clicked.connect(lambda: HandleRAW_UI.ttt_plot_wave(self))
        self.btn_display_raw.clicked.connect(lambda: HandleRAW_UI.display_raw(self))
        # self.display_stdev.clicked.connect(lambda: HandleRAW_UI.display_stdev(self))

    def openFileEvent(self):
        self.raw_file_list = list()
        self.folder_list = []
        folder_name_list = []
        self.file_path = QFileDialog.getExistingDirectory(self.centralwidget, 'Choose Folder',
                                                            r'C:')  # return value is tuple type
        if self.file_path == '':
            self.handleDisplay('No object selected')
            return
        for root, dirs, files in os.walk(self.file_path):
            for dir in dirs:
                folder_name_list.append(dir)
                if os.path.join(root, dir):
                    self.folder_list.append(os.path.join(root, dir))
        folder_name_list = self.folder_list
        # sort the list with the back number
        folder_pd = pd.DataFrame([i.split('-') for i in folder_name_list])
        # # judge the data is Light Intensity(Dec), or register value(Hex)
        if folder_name_string_pattern1 in folder_pd[1][0] or folder_name_string_pattern2 in folder_pd[1][0]:
            self.labels = folder_pd[1].tolist()
            folder_pd[1] = folder_pd[1].map(lambda x: str(x)[2:])  # delete '0x'
            folder_pd[1] = folder_pd[1].apply(lambda x: int(x, 16))  # convert Hex to Dec
            self.ticks = folder_pd[1].tolist()
            self.x_axis_label = 'Register Value'
        else:
            self.x_axis_label = 'Light Intensity'
            folder_pd[1] = folder_pd[1].astype(int)
            # get the Light Intensity, put into list, sort them.
            self.light_list = folder_pd[1].tolist()
            self.light_list.sort()
            self.labels = self.light_list
            self.ticks = self.light_list
        folder_pd = folder_pd.sort_values(by=1, ascending=True)
        folder_pd = folder_pd.values.tolist()
        self.folder_list = []
        for i in range(len(folder_pd)):
            # self.folder_list.append(folder_pd[i][0] + '-' + str(folder_pd[i][1]))
            self.folder_list.append(folder_pd[i][0] + '-' + str(self.labels[i]))
        self.start_handle()

    def start_handle(self):
        print('I AM WORKING......')
        # self.textEdit.append('Start calculation......')
        self.handleDisplay('<font color=\"#0000FF\">---- I AM WORKING...... ----<font>')
        time_start = time.time()
        self.handlePathOrFile()
        time_end = time.time()
        self.handleDisplay('\r\n')
        self.handleDisplay('<font color=\"#0000FF\">---- Finished!!! ----<font>')
        self.handleDisplay('Take time:' + str(round(time_end - time_start, 3)) + 'S')
        self.handleDisplay(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
        self.handleDisplay('\r\n')
        print('All Finished')

    # display data with textEdit append
    def handleDisplay(self, data):
        self.textEdit.append(data)
        app.processEvents()

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
                if filename_extension in self.file_list[list_loop]:
                    self.raw_file_list.append(self.file_list[list_loop])
                    raw_file_list.append(self.file_list[list_loop])
            self.handleDisplay(str(folder))
            # self.handleDisplay('\n')

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

        self.ttt_plot_wave()


    def handle_raw(self, file_path, raw_file_list):
        AREA = [500, 500, 1500, 1500]
        # AREA = [500, 500, 501, 501]
        RGB_Count_SUM = (AREA[2]-AREA[0])*(AREA[3]-AREA[1])/4
        np.set_printoptions(precision=3)
        rows = 2064  # image row is V:2064     2064*2672 = 5515008
        cols = 2672  # image column is H:2672
        channels = 1  # image channel, the gray is 1
        slice_start = 32
        slice_end = rows * cols
        Frame_count = 32
        RGB_Result_list = []
        raw_sum = np.zeros((AREA[2] - AREA[0], AREA[3] - AREA[1]), dtype=np.uint64)  # be careful the data overflow
        # raw_stdev = np.zeros((AREA[2] - AREA[0], AREA[3] - AREA[1]), dtype=np.uint16)
        # raw_median = np.zeros((AREA[2] - AREA[0], AREA[3] - AREA[1]), dtype=np.uint16)
        frame_list = list()
        raw_median_list = [[0 for col in range(len(raw_file_list))] for row in
                           range((AREA[2] - AREA[0]) * (AREA[3] - AREA[1]))]
        for file_loop in range(len(raw_file_list)):
            raw_file = file_path + '\\' + raw_file_list[file_loop]
            total_pixels = np.fromfile(raw_file, dtype='>u2')  # big endian, u2(uint16, 2byte)
            total_pixels = np.reshape(total_pixels[slice_start:], [rows, cols])  # do not need to shift the bin data, it is high zero padding
            # total_pixels = np.reshape(np.right_shift(total_pixels[slice_start:], 2), [rows, cols])
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
        GB_stdev_list_single = []
        B_stdev_list_single = []
        R_stdev_list_single = []
        GR_stdev_list_single = []
        for x_axis in range(int((AREA[2] - AREA[0])/2)):
            for y_axis in range(int((AREA[3] - AREA[1])/2)):
                GB_stdev_list_single.append(self.raw_ave[2*x_axis + 0, 2*y_axis + 0])
                B_stdev_list_single.append(self.raw_ave[2*x_axis + 0, 2*y_axis + 1])
                R_stdev_list_single.append(self.raw_ave[2*x_axis + 1, 2*y_axis + 0])
                GR_stdev_list_single.append(self.raw_ave[2*x_axis + 1, 2*y_axis + 1])
        GB_stdev = np.std(GB_stdev_list_single)
        B_stdev = np.std(B_stdev_list_single)
        R_stdev = np.std(R_stdev_list_single)
        GR_stdev = np.std(GR_stdev_list_single)
        RGB_Result_list.extend([GB_stdev, B_stdev, R_stdev, GR_stdev])

        self.display_ave_flag = True
        self.display_stdev_flag = True
        self.plot_wave_flag = True
        return RGB_Result_list

##===============================================================
    def display_raw(self):
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
        total_pixels = np.fromfile(r'D:\Python\Project\Ref_Data\700.raw', dtype='uint16')  #>u2
        array_data_dec = np.reshape(total_pixels[slice_start:], [rows, cols])
        cv2.imshow('Infared image-640*512-8bit', array_data_dec)
        # 如果是uint16的数据请先转成uint8。不然的话，显示会出现问题。
        cv2.waitKey()
        cv2.destroyAllWindows()
        print('finished')
##===============================================================

    def ttt_plot_wave(self):
        print('Plotting')
        # self.x_axis_label = 'you can change the label if you want'
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
        # merge two list(x is Light Intensity, y is the measured value)
        for i, j in zip(self.ticks, R_ave_list):
            R_ave_dict[i] = j
        for i, j in zip(self.ticks, B_ave_list):
            B_ave_dict[i] = j
        for i, j in zip(self.ticks, GR_ave_list):
            GR_ave_dict[i] = j
        for i, j in zip(self.ticks, GB_ave_list):
            GB_ave_dict[i] = j
        for i, j in zip(self.ticks, R_median_list):
            R_median_dict[i] = j
        for i, j in zip(self.ticks, B_median_list):
            B_median_dict[i] = j
        for i, j in zip(self.ticks, GR_median_list):
            GR_median_dict[i] = j
        for i, j in zip(self.ticks, GB_median_list):
            GB_median_dict[i] = j
        for i, j in zip(self.ticks, R_stdev_list):
            R_stdev_dict[i] = j
        for i, j in zip(self.ticks, B_stdev_list):
            B_stdev_dict[i] = j
        for i, j in zip(self.ticks, GR_stdev_list):
            GR_stdev_dict[i] = j
        for i, j in zip(self.ticks, GB_stdev_list):
            GB_stdev_dict[i] = j
        # write to excel
        Data_name = [self.x_axis_label, 'R_ave', 'B_ave', 'GR_ave', 'GB_ave', 'R_median', 'B_median', 'GR_median',
                     'GB_median', 'R_stdev', 'B_stdev', 'GR_stdev', 'GB_stdev']
        title_name = {"name": Data_name}
        df = pd.DataFrame(title_name, columns=Data_name)
        df.loc[:, Data_name[0]] = self.labels
        df.loc[:, Data_name[1]] = R_ave_list
        df.loc[:, Data_name[2]] = B_ave_list
        df.loc[:, Data_name[3]] = GR_ave_list
        df.loc[:, Data_name[4]] = GB_ave_list
        df.loc[:, Data_name[5]] = R_median_list
        df.loc[:, Data_name[6]] = B_median_list
        df.loc[:, Data_name[7]] = GR_median_list
        df.loc[:, Data_name[8]] = GB_median_list
        df.loc[:, Data_name[9]] = R_stdev_list
        df.loc[:, Data_name[10]] = B_stdev_list
        df.loc[:, Data_name[11]] = GR_stdev_list
        df.loc[:, Data_name[12]] = GB_stdev_list
        note_path = str(self.file_path + '/Note_data_' + time.strftime("%Y%m%d%H%M%S", time.localtime()) + '.xlsx')
        df.to_excel(note_path)
        fig = plt.figure(figsize=(25, 20))
        ##################################################################
        Average = fig.add_subplot(3, 1, 1)
        plt.xlabel(self.x_axis_label)
        plt.ylabel("Average Value")
        plt.title("RGB & " + self.x_axis_label)
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
        plt.xticks(self.ticks, self.labels, rotation=270)
        ################################################################
        Median = fig.add_subplot(3, 1, 2)
        x = list(range(len(R_median_list)))
        plt.xlabel(self.x_axis_label)
        plt.ylabel("Median Value")
        plt.title("RGB & " + self.x_axis_label)
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
        plt.xticks(self.ticks, self.labels, rotation=270)
        ##################################################################
        x = list(range(len(R_stdev_list)))
        Stdev = fig.add_subplot(3, 1, 3)
        plt.xlabel(self.x_axis_label)
        plt.ylabel("Standard Deviation  Value")
        plt.title("RGB & " + self.x_axis_label)
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
        plt.xticks(self.ticks, self.labels, rotation=270)

        plt.subplots_adjust(left=None, bottom=None, right=None, top=None, wspace=None, hspace=0.5)  # adjust the distence
        plt.show()

class BackendThread(QObject):
    # define signal
    update_date = pyqtSignal(str)
    # handle the function
    def run(self):
        while 1:
            # refresh
            for i in range(1, 11):
                self.update_date.emit(str(i))
                time.sleep(1)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    myWindow = QMainWindow()
    HTUI = HandleRAW_UI()
    myWindow.show()
    sys.exit(app.exec_())
