import openpyxl,time

output_file_path = '.\Out'

def creat_report_excel():
    name_time = time.strftime("%Y%m%d%H%M%S", time.localtime())
    report_file_name = 'TestReport_' + name_time + '.xlsx'
    save_path_name = output_file_path + '\\' + report_file_name
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = 'Test_Result'
    ws['A1'] = 'DUT_NO'
    ws['B1'] = 'Result'
    ws['C1'] = 'Fail_Item'
    ws['D1'] = 'Pin_Name'
    ws['E1'] = 'Fail_Value'
    ws['F1'] = 'Image_Status'
    wb.save(save_path_name)
    print('Finish report initial')
    return wb, ws