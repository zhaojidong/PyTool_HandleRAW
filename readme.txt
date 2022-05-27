1.目前plot waveform只设置了两个x label string。一个是光强（Light Intensity）一个是寄存器值（Register Value）。纵坐标都是RGB对应的均值，中位数和标准差。
2.文件夹名格式定义，根据最后一个‘-’字符，把最后一组字符串作为区分标准
0x/0X:    表示写寄存器，eg:0xff,0X09
十进制数：  表示改变光强，eg:50，150，2000
小数：     表示滤光片，eg:10%,12.7%