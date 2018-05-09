# -*- coding:utf-8 -*-

import os


def delete_dir(dirc):
    if os.path.isdir(dirc):
        for item in os.listdir(dirc):
            path = os.path.join(dirc, item)
            if os.path.isdir(path) is True:
                delete_dir(path)

    if not os.listdir(dirc):
        os.rmdir(dirc)
        print("移除空目录：" + dirc)
