import time
import RPi.GPIO as gpio
from datetime import datetime
import pandas as pd
from glob import glob

hi_sw_pin = 20
lo_sw_pin = 21
control_out = 18


gpio.cleanup()

gpio.setmode(gpio.BCM)
gpio.setup(hi_sw_pin,gpio.IN,pull_up_down=gpio.PUD_DOWN)
gpio.setup(lo_sw_pin,gpio.IN,pull_up_down=gpio.PUD_DOWN)
gpio.setup(control_out,gpio.OUT)
pwmoutput = gpio.PWM(control_out,50) #GPIO１８をpwmoutputオブジェクトとして作成。50Hzで設定



#---------- 案件名 ----------#
project_title = "sansui_project"

#---------- csvファイルを保存するフォルダのパス ----------#
dir_path = "/home/tanakakouji/python/sansui/"

#---------- ヘッダー名作成 ----------#
# header = pd.MultiIndex.from_tuples([
        # ("","日時"),
        # ("","状態"),
        # ("","count")
        # ])
header = ["日時","状態","count"]


#---------- 新規ファイル作成と書き込み ----------#
def create_new_file_and_write(c,status,add):
    today_str = datetime.today().strftime("%y%m%d") #日付を文字列へ変換
    file_name = "{}_{}".format(project_title,today_str)
    #csv保存フォルダ内のcsvファイル名をリストで取得
    csv_list = glob("{}*.csv".format(dir_path))
    #csvファイルのパス
    file_path = "{}{}.csv".format(dir_path,file_name)
    #csvファイル名リスト内にf_nameのファイルが存在しない場合は、新規でfile_name名のファイルを作成する。
    if file_path not in csv_list:
        print("新規ファイル名:{}".format(file_name))
        df_h = pd.DataFrame(columns = header)
        df_h.to_csv(file_path, mode="w",encoding='cp932',index=False)
        c = 1 #その日の初回ONなのでカウント１とする。
    else:
	    print("ファイルに加筆:{}".format(file_name))
	    c += add #前回のカウントに＋addとする。	
	#---------- 日時設定 ----------#
    now = datetime.now().strftime("%Y/%m/%d %H:%M:%S")
    l = [now,status,c]
    print(l)

    #---------- 上記のリストとヘッダーをデータフレーム化 ----------#
    df = pd.DataFrame([l])
    #　（重要！）lでなく[l]とするのはlistをDataFrame化する際に一次元リストだと行方向（縦方向）にデータが書き込まれる。
    # 二重リストとすることで列方向に書き込まれる！
    try:
    #---------- CSVへの書き出し（追記） ----------#
        df.to_csv(file_path, mode="a",encoding='cp932',index=False,header=False)
    except:
	    print("csvへの書き込みエラー")
    return c


count = 0

hi_count = 1
lo_count = 1

while True:
    print("Hi ",gpio.input(hi_sw_pin ))
    print("Lo ",gpio.input(lo_sw_pin ))
    if ((gpio.input(hi_sw_pin )) == (gpio.input(lo_sw_pin )) ==1) and (lo_count == 1):
        print("ポンプON！")
        count = create_new_file_and_write(count,"ON",1)
        hi_count = 1
        lo_count = 0
        print("count:",count)
        pwmoutput.start(100) #PWMを初期化。また、初期の値を100(duty比)とする。
        time.sleep(5)

    if ((gpio.input(hi_sw_pin )) == (gpio.input(lo_sw_pin )) ==0) and (hi_count == 1):
        print("ポンプOFF！")
        create_new_file_and_write(count,"OFF",0)
        lo_count = 1
        hi_count = 0
        pwmoutput.stop()
        time.sleep(5)
    time.sleep(2)





















