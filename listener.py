import os
import re
import time
import urllib
from posixpath import dirname

import cloudscraper
import m3u8
import requests
from Crypto.Cipher import AES
from pcof import bytesconv

from conf.config import *
from config import headers
from crawler import prepareCrawl
from delete import deleteM3u8, deleteMp4
from merge import mergeMp4
from version import VERSION


def download(target, output_path):
    urlSplit = target.split('/')
    dir_name = urlSplit[-2]
    folderPath = os.path.join(output_path, dir_name)
    if not os.path.exists(folderPath):
        os.makedirs(folderPath)
    htmlfile = cloudscraper.create_scraper(browser='firefox',
                                           delay=10).get(target)
    result = re.search("https://.+m3u8", htmlfile.text)
    m3u8url = result[0]
    m3u8urlList = m3u8url.split('/')
    m3u8urlList.pop(-1)
    downloadurl = '/'.join(m3u8urlList)
    m3u8file = os.path.join(folderPath, dir_name + '.m3u8')
    urllib.request.urlretrieve(m3u8url, m3u8file)
    m3u8obj = m3u8.load(m3u8file)
    m3u8uri = ''
    m3u8iv = ''
    for key in m3u8obj.keys:
        if key:
            m3u8uri = key.uri
            m3u8iv = key.iv
    tsList = []
    for seg in m3u8obj.segments:
        tsUrl = downloadurl + '/' + seg.uri
        tsList.append(tsUrl)
    if m3u8uri:
        m3u8keyurl = downloadurl + '/' + m3u8uri

        response = requests.get(m3u8keyurl, headers=headers, timeout=10)
        contentKey = response.content

        vt = m3u8iv.replace("0x", "")[:16].encode()  # IV取前16位

        ci = AES.new(contentKey, AES.MODE_CBC, vt)  # 建構解碼器
    else:
        ci = ''

    deleteM3u8(folderPath)
    tick = time.time()
    prepareCrawl(ci, folderPath, tsList)
    tick = time.time() - tick
    size = mergeMp4(folderPath, tsList, output_path)
    speed = size / tick
    speed = bytesconv.bytes2human(speed)
    print('download use time: {} {}/s'.format(speed[0], speed[1]))
    deleteMp4(folderPath)


def main():
    saved = set()

    print('reading saved file:', saved_file)
    with open(saved_file, 'r') as f:
        saved = set(f.readlines())
    print('saved count: ', len(saved))

    while True:
        targets = list()
        print('VERSION=', VERSION, 'reading target file:', target_file)
        with open(target_file, 'r') as f:
            targets = f.readlines()
        print('target count:', len(targets))
        for target in targets:
            if target not in saved:
                retry = 0
                while retry < retry_count:
                    try:
                        print('begin download target: ', target)

                        download(target, output_path)

                        print('download target: ', target, ' success')
                        saved.add(target)
                        with open(saved_file, 'a') as f:
                            f.writelines([target])

                        print('update target file success')
                        break
                    except Exception as ex:
                        retry += 1
                        print('download target: ', target,
                              ' failed, retry count:', retry, ', excption: ',
                              ex)
            print('update saved file success')
            with open(target_file, 'r+') as f:
                lines = f.readlines()
                f.seek(0)
                f.truncate()
                f.writelines(lines[1:])
            print('sleep ', sleep_seconds, ' seconds...')
            time.sleep(sleep_seconds)


if __name__ == '__main__':
    main()
