# -*- coding:utf-8 -*-

import os
import platform
import shutil
import codecs


def create_bat(username, add_cmd):
    os.chdir(os.path.abspath('.'))
    if platform.system() == 'Windows':
        bat_path = os.path.abspath('.') + '\\networkbootsystem\\static\\batfolder'
        file_name = bat_path + '\\' + username + '.bat'
    if platform.system() == 'Linux':
        bat_path = os.path.abspath('.') + '/networkbootsystem/static/batfolder'
        file_name = bat_path + '/' + username + '.bat'

    print(os.path.abspath('.'))
    print(file_name)
    print(add_cmd)
    file = codecs.open(file_name, 'w', 'GBK')
    file.writelines('@echo off\r\n')
    for cmd in add_cmd:
        file.writelines(cmd + '\r\n')
    # file.writelines('pause')
    file.writelines('del %0\r\n')
    # file.write('@echo off\n' + add_cmd + '\ndel %0')
    file.close()
    return username + '.bat'


def del_files():
    os.chdir(os.path.abspath('.'))
    if platform.system() == 'Windows':
        bat_path = os.path.abspath('.') + '\\networkbootsystem\\static\\batfolder'
    if platform.system() == 'Linux':
        bat_path = os.path.abspath('.') + '/networkbootsystem/static/batfolder'
    shutil.rmtree(bat_path)
    os.mkdir(bat_path)

if __name__ == '__main__':
    create_bat("2", ("123", '321'))