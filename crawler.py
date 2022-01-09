import concurrent.futures
import copy
import os
import time
from functools import partial

import requests
from pcof import bytesconv

from config import headers


def scrape(ci, folderPath, downloadList, urls):
    os.path.split(urls)
    fileName = urls.split('/')[-1][0:-3]
    saveName = os.path.join(folderPath, fileName + ".mp4")
    if os.path.exists(saveName):
        # 跳過已下載
        print('當前目標: {0} 已下載, 故跳過...剩餘 {1} 個'.format(
            urls.split('/')[-1], len(downloadList)))
        downloadList.remove(urls)
    else:
        tick = time.time()
        response = requests.get(urls, headers=headers, timeout=10)
        if response.status_code == 200:
            content_ts = response.content
            if ci:
                content_ts = ci.decrypt(content_ts)  # 解碼
            with open(saveName, 'ab') as f:
                f.write(content_ts)
                # 輸出進度
            downloadList.remove(urls)
        tick = time.time() - tick
        speed = len(content_ts) / tick
        speed = bytesconv.bytes2human(speed)
        print(
            '\r當前下載: {0} , 剩餘 {1} 個, status code: {2}, speed: {3} {4}'.format(
                urls.split('/')[-1], len(downloadList), response.status_code,
                speed[0], speed[1]),
            end='',
            flush=True)


def prepareCrawl(ci, folderPath, tsList):
    downloadList = copy.deepcopy(tsList)
    # 開始時間
    start_time = time.time()
    print('開始下載 ' + str(len(downloadList)) + ' 個檔案..', end='')
    print('預計等待時間: {0:.2f} 分鐘 視影片長度與網路速度而定)'.format(len(downloadList) / 150))

    # 開始爬取
    startCrawl(ci, folderPath, downloadList)

    end_time = time.time()
    print('\n花費 {0:.2f} 分鐘 爬取完成 !'.format((end_time - start_time) / 60))


def startCrawl(ci, folderPath, downloadList):
    # 同時建立及啟用 20 個執行緒
    round = 0
    while (downloadList != []):
        with concurrent.futures.ThreadPoolExecutor(max_workers=8) as executor:
            executor.map(partial(scrape, ci, folderPath, downloadList),
                         downloadList)
        round += 1
        print(f', round {round}')
