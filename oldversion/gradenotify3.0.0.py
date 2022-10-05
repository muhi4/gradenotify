# gradenotify version3.0.0
# coding:UTF-8
import csv
import datetime
import getpass
import pathlib
from time import sleep

import requests
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from apscheduler.schedulers.blocking import BlockingScheduler

def getseisekifromweb(username, password):
    # webドライバー設定
    driverpath = "/usr/bin/chromedriver"
    options = Options()
    # options.add_argument('--headless')  # ヘッドレスモード(windowなしで実行)
    driver = webdriver.Chrome(executable_path=driverpath, options=options)
    # seisekipageにアクセス
    driver.get("https://kuss.kumamoto-u.ac.jp/ssk00.php?lang=ja")
    wait = WebDriverWait(driver, 30)
    # id,パスワードを入力、送信
    username_box = driver.find_element_by_id('username')
    password_box = driver.find_element_by_id('password')
    username_box.send_keys(username)
    password_box.send_keys(password)
    password_box.send_keys(Keys.ENTER)
    sleep(5)
    # ログインボタンの読み込み待ち、クリック
    login_button = wait.until(expected_conditions.element_to_be_clickable((By.CLASS_NAME, "btn-submit")))
    login_button.click()

    wait.until(expected_conditions.presence_of_element_located((By.CLASS_NAME, "seiseki")))
    seiseki = driver.find_element_by_class_name("seiseki").find_elements_by_tag_name("tr")

    grade = []
    for i in range(1, len(seiseki)-1):  # ページから取得した情報から成績を抽出
        td = seiseki[i].find_elements_by_tag_name("td")
        if td[1].text != '小　計':
            grade.append([td[3].text, td[4].text, td[6].text])  # 科目名、単位数、評定
    driver.quit()
    return grade

def getseisekifromcsv():
    old_grade = []
    pathlib.Path('grade.csv').touch(exist_ok=True)  # grade.csvが存在しない場合に生成
    with open('grade.csv', 'r', encoding="utf-8") as f:  # csvファイルから成績取得
        old_grade_read = csv.reader(f)
        # インデックスを使うためにlistとして取り込む
        old_grade = [row for row in old_grade_read]
    return old_grade

def checkupdates(grade, old_grade):
    # 成績の差分抽出(flagの値は更新無:0,更新有:1)
    dif = []  # 更新分
    modi = []  # 修正分
    difflag = False
    modiflag = False
    j = 0
    for i in range(len(grade)):
        # 成績更新チェック
        if(j == len(old_grade) or grade[i][0] != old_grade[j][0]):
            difflag = True
            dif.append(grade[i])
        else:
            # 修正チェック
            if grade[i][2] != old_grade[j][2]:
                modiflag = True
                modi.append([old_grade[j][0], old_grade[j][2], grade[i][2]]) # 科目名、更新前評定、更新後評定
            j += 1
    return dif, modi, difflag, modiflag

def createmessage(dif, modi):
    # line送信用
    mesforline = []
    # 修正分
    for i in range(len(modi)):
        mesforline.append(str(modi[i][0]) + ':' +str(modi[i][1]) + '→' + str(modi[i][2]))
        # 最終行でないとき
        if(i != len(modi)-1):
            mesforline.append('\n')
        else:
            # 最終行かつ更新がある場合(修正だけのときにメッセージの末尾に無駄な改行が発生しないようにするため)
            if(len(dif) != 0):
                mesforline.append('\n')
    # 更新分
    for i in range(len(dif)):
        mesforline.append(str(dif[i][0]) + ':' + str(dif[i][2]))
        if(i != len(dif)-1):
            mesforline.append('\n')

    return mesforline


def comf():
    grade = getseisekifromweb(username, password)
    old_grade = getseisekifromcsv()
    
    dif, modi, difflag, modiflag = checkupdates(grade, old_grade)

    if(modiflag or difflag):
        print("new!")
        with open('grade.csv', 'w', encoding="utf-8", newline="\n") as f:  # csvを上書き
            writer = csv.writer(f)
            writer.writerows(grade)

        mes = "成績が更新されました。\n" + "".join(createmessage(dif, modi))
        sendline(mes)

    now = datetime.datetime.now()
    print('done.')
    print(now)


def sendline(mes):
    url = 'https://notify-api.line.me/api/notify'
    token = linetoken
    headers = {'Authorization': 'Bearer ' + token}
    message = {'message': mes}
    requests.post(url, headers=headers, data=message)


if __name__ == "__main__":
    username = input("熊本大学IDを入力:")
    password = getpass.getpass("パスワードを入力:")
    with open("linetoken.txt", "r", encoding="UTF-8") as f:
        linetoken = f.readlines()[0]
    scheduler = BlockingScheduler()
    scheduler.add_job(func=comf, trigger='cron', minute=30)
    scheduler.add_job(func=sendline, trigger='cron', hour=21, args=["成績を確認しました。"])
    # scheduler.start()
    comf()
