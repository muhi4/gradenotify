#!/usr/bin/env python3
#coding:UTF-8
import csv
import requests
import datetime
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from apscheduler.schedulers.blocking import BlockingScheduler
from time import sleep

username = "#"
password = "#"
options = Options()

def comf():
    #webドライバー設定
    driver = webdriver.Chrome(executable_path="/usr/lib/chromium-browser/chromedriver",options=options)
    #ポータルにアクセス
    driver.get("https://cas.kumamoto-u.ac.jp/cas/login?service=https://uportal.kumamoto-u.ac.jp/uPortal/LoginTF")
    wait = WebDriverWait(driver, 60)
    main_window = driver.current_window_handle
    #id,パスワードを入力、送信
    username_box = driver.find_element_by_id('username')
    password_box = driver.find_element_by_id('password')
    username_box.send_keys(username)
    password_box.send_keys(password)
    login_button = driver.find_element_by_xpath("//*[@id='homepage']/div/div/div/form/table/tbody/tr[5]/td[2]/button")
    login_button.click()
    #sleep(10)
    #ログインボタンの読み込み待ち、クリック
    wait.until(expected_conditions.element_to_be_clickable((By.XPATH,"//*[@id='login']/div[2]/input[4]")))
    login_button = driver.find_element_by_xpath("//*[@id='login']/div[2]/input[4]")
    login_button.click()
    #ポータルの右側に移動
    wait.until(expected_conditions.visibility_of_element_located((By.XPATH,"/html/body/table[3]/tbody/tr/td[2]/table/tbody/tr[6]/td[2]/table/tbody/tr/td[1]/iframe")))
    iframe = driver.find_element_by_xpath("/html/body/table[3]/tbody/tr/td[2]/table/tbody/tr[6]/td[2]/table/tbody/tr/td[1]/iframe")
    driver.switch_to.frame(iframe)
    #ボタンクリック
    wait.until(expected_conditions.element_to_be_clickable((By.XPATH,"/html/body/ul/li[11]/a")))
    move_bottun = driver.find_element_by_xpath("/html/body/ul/li[11]/a")
    move_bottun.click()
    
    driver.switch_to.default_content()
    sleep(30)
    for window in driver.window_handles:
        driver.switch_to.window(window)
        if driver.title == '証明書の発行について':
            break
    wait.until(expected_conditions.element_to_be_clickable((By.XPATH,"//*[@id='button2']")))
    move_bottun = driver.find_elements_by_xpath("//*[@id='button2']")
    move_bottun[2].click()
    #sleep(20)
    wait.until(expected_conditions.presence_of_element_located((By.CLASS_NAME,"seiseki")))
    seiseki = driver.find_element_by_class_name("seiseki").find_elements_by_tag_name("tr")
    with open('output.csv','r') as f:
        old_seiseki = f.read()    
    
    if(int(old_seiseki) != len(seiseki)):
        print("new!")
        with open('output.csv','w') as f:#行数更新
            writer = csv.writer(f)
            writer.writerow([len(seiseki)])
        
        #成績csv更新
        grade = []
        old_grade = []
        dif = []
        for i in range(1,len(seiseki)-1):   #ページから成績取得
            td = seiseki[i].find_elements_by_tag_name("td")
            if td[1].text != '小　計':
                grade.append([td[3].text,td[6].text])
        with open('grade.csv','r') as f:  #csvファイルから成績取得
            old_grade_read = csv.reader(f)
            old_grade = [row for row in old_grade_read] #インデックスを使うためにlistとして取り込む
        
        #成績の差分抽出
        difflag = 0
        for i in range(len(grade)):
            difflag = 0
            for j in range(len(old_grade)):
                if(grade[i][0] == old_grade[j][0]):
                    difflag = 1
                    continue
            if(difflag == 0):
                dif.append(grade[i])
        for i in range(len(dif)): #差分出力
            print(dif[i])
        with open ('grade.csv','a') as f: #csvに差分を追記
            writer = csv.writer(f)
            writer.writerows(dif)
        
        #line送信用にstringを用意
        temp = []
        for i in range(len(dif)):
            temp.append(str(dif[i][0]) +':'+ str(dif[i][1]))
            if(i != len(dif)-1):
                temp.append('\n')
        mes = "".join(temp)
        
        url = 'https://notify-api.line.me/api/notify'
        token = '#'
        payload = {'message':'成績が更新されました。\n' + mes}    
        headers = {'Authorization': 'Bearer ' + token}
        line_notify = requests.post(url, data=payload, headers=headers)
    driver.quit()
    now = datetime.datetime.now()
    print('done.')
    print(now)

def line():
    url = 'https://notify-api.line.me/api/notify'
    token = '#'
    payload = {'message':'成績を確認しました。'}    
    headers = {'Authorization': 'Bearer ' + token}
    line_notify = requests.post(url, data=payload, headers=headers)

comf()
#scheduler = BlockingScheduler()
#scheduler.add_job(comf, 'cron',minute=30)
#scheduler.add_job(line, 'cron',hour=21)
#scheduler.start()