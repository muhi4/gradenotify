#!/usr/bin/env python3
# coding:UTF-8
import csv
import requests
import datetime
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from apscheduler.schedulers.blocking import BlockingScheduler
from time import sleep

username = "#"
password = "#"
options = Options()
# ヘッドレスモード(windowなしで実行)
options.add_argument('--headless')


def comf():
    # webドライバー設定
    driverpath = r"C:\chromedriver.exe"
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
    login_button = wait.until(
        expected_conditions.element_to_be_clickable((By.CLASS_NAME, "btn-submit")))
    login_button.click()

    wait.until(expected_conditions.presence_of_element_located(
        (By.CLASS_NAME, "seiseki")))
    seiseki = driver.find_element_by_class_name(
        "seiseki").find_elements_by_tag_name("tr")

    # 成績csv更新
    grade = []  # ページから取得分
    old_grade = []  # grade.csvから取得分
    for i in range(1, len(seiseki)-1):  # ページから成績取得
        td = seiseki[i].find_elements_by_tag_name("td")
        if td[1].text != '小　計':
            grade.append([td[3].text, td[6].text])  # 科目名、評定

    with open('grade.csv', 'r', encoding="utf-8_sig") as f:  # csvファイルから成績取得
        old_grade_read = csv.reader(f)
        old_grade = [row for row in old_grade_read]  # インデックスを使うためにlistとして取り込む

    # 成績の差分抽出(更新無:0,更新有:1)
    dif = []  # 更新分
    modi = []  # 修正分
    difflag = 0
    modiflag = 0
    j = 0
    for i in range(len(grade)):

        # 成績更新チェック
        if(j == len(old_grade) or grade[i][0] != old_grade[j][0]):
            difflag = 1
            dif.append(grade[i])
        else:
            # 修正チェック
            if grade[i][1] != old_grade[j][1]:
                modiflag = 1
                modi.append([old_grade[j][0], old_grade[j][1],
                            grade[i][1]])  # 科目名、更新前評定、更新後評定
            j += 1

    if(modiflag or difflag):
        print("new!")
        with open('grade.csv', 'w', encoding="utf-8_sig", newline="\n") as f:  # csvを上書き
            writer = csv.writer(f)
            writer.writerows(grade)

        # line送信用にstringを用意
        temp = []
        for i in range(len(modi)):
            temp.append(str(modi[i][0]) + ':' +
                        str(modi[i][1]) + '→' + str(modi[i][2]))
            if(i != len(modi)-1):
                temp.append('\n')
            else:
                if(len(dif) != 0):
                    temp.append('\n')
        for i in range(len(dif)):
            temp.append(str(dif[i][0]) + ':' + str(dif[i][1]))
            if(i != len(dif)-1):
                temp.append('\n')
        mes = "".join(temp)
        url = 'https://notify-api.line.me/api/notify'
        token = '#'
        headers = {'Authorization': 'Bearer ' + token}
        message = {'message': '成績が更新されました。\n' + mes}
        requests.post(url, headers=headers, data=message)
    driver.quit()
    now = datetime.datetime.now()
    print('done.')
    print(now)


def line():
    url = 'https://notify-api.line.me/api/notify'
    token = '#'
    headers = {'Authorization': 'Bearer ' + token}
    message = {'message': '成績を確認しました。'}
    requests.post(url, headers=headers, data=message)


if __name__ == "__main__":
    scheduler = BlockingScheduler()
    scheduler.add_job(comf, 'cron', minute=30)
    scheduler.add_job(line, 'cron', hour=21)
    scheduler.start()
