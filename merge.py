import os
import time
def mergeMp4(folderPath, tsList, target_path):
    # 開始時間
    start_time = time.time()
    print('開始合成影片..')
    video_name = folderPath.split(os.path.sep)[-1]
    target_filename = os.path.join(target_path, video_name + '.mp4')
    for i in range(len(tsList)):
        file = tsList[i].split('/')[-1][0:-3] + '.mp4'
        full_path = os.path.join(folderPath, file)
        if os.path.exists(full_path):
            with open(full_path, 'rb') as f1:
                with open(target_filename,
                          'ab') as f2:
                    f2.write(f1.read())
        else:
            print(file + " 失敗 ")
    end_time = time.time()
    print('花費 {0:.2f} 秒合成影片'.format(end_time - start_time))
    print('下載完成!')
    return os.path.getsize(target_filename)