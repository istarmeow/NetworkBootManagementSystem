import urllib


def rename_image(image_name, new_name):
    url = 'http://192.168.96.99:8898/images'

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


def rename_logs():
    url = 'http://192.168.96.99:8898/renamelogs'
    try:
        req = urllib.request.urlopen(url, timeout=3)
        if req.getcode() == 200:
            date = req.read().decode('utf-8')
            return date
        else:
            print('无法连接')
            return None
    except urllib.error.URLError:
        return None