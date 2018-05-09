# -*- coding:utf-8 -*-
import xlrd
import os


def get_from_excel(file_name):


    print(os.listdir())
    file_open = xlrd.open_workbook(file_name)
    table = file_open.sheets()[0]
    nrows = table.nrows  # 行
    ncols = table.ncols  # 列
    print('有%d行，%d列' % (nrows, ncols))

    for row in range(1, nrows):
        for col in range(ncols):
            print(table.cell(row, col).value, end='  ')
        print('\n')


if __name__ == '__main__':
    file_path = os.getcwd() + '\configfiles'
    os.chdir(file_path)
    file_name = 'pxe_config.xlsx'
    get_from_excel(file_name)