# -*- coding:utf-8 -*-
import urllib.request
import urllib.error
import socket
import json


def judge_web_connection(url):
    try:
        with urllib.request.urlopen(url, timeout=2) as req:
            print(req.getcode())
            if req.getcode() == 200:
                return True
            else:
                return False
    except (socket.timeout, urllib.error.URLError):
        return False


if __name__ == '__main__':
    print(judge_web_connection("http://172.16.66.66:8898/images"))
