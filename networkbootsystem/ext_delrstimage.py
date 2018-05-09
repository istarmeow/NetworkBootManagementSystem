import urllib


# 镜像删除
def del_image(image_name):
    url = 'http://192.168.96.99:8898/del_image'

    postdata = urllib.parse.urlencode({'image_name': image_name, })
    postdata = postdata.encode('utf-8')
    try:
        res = urllib.request.urlopen(url, postdata)
        print(res.status, res.reason)

        if res.status == 200:
            print('POST成功')
            return True
        else:
            print('POST失败')
            return True
    except urllib.error.HTTPError as ueH:
        print(ueH)
        return False


# 镜像还原
def restore_image(image_name, new_name):
    url = 'http://192.168.96.99:8898/restore_image'

    postdata = urllib.parse.urlencode({'image_name': image_name, 'new_name': new_name})
    postdata = postdata.encode('utf-8')
    try:
        res = urllib.request.urlopen(url, postdata)
        print(res.status, res.reason)

        if res.status == 200:
            print('POST成功')
            return True
        else:
            print('POST失败')
            return True
    except urllib.error.HTTPError as ueH:
        print(ueH)
        return False
