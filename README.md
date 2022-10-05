gradenotify  
成績通知ソフト。証明書発行システムにアクセスして更新があればlinenotifyで通知。  
動作しているか確認のため毎日一度(21時)通知する。  


使い方  
1."linetoken.txt"をgradenotify.pyと同じディレクトリ内に作成する。  
2.LINENotify(https://notify-bot.line.me/ja/)でlineログイン、登録してトークンをlinetoken.txtの最初の行にコピペ。  
3.必要な環境を構築。requirements.txtに必要なモジュール、動作確認済みバージョンを記載。  
4.google chromeと対応するバージョンのchromedriver(https://chromedriver.chromium.org/downloads)をダウンロード。  
  chrimedriverを置くディレクトリパスはgradenotify.py内のgetseisekifromweb関数の"driverpath="の部分で定義されている。  
  raspberrypiで実行する場合、ドライバーの入手法が異なる(下に別途記載)。  
5.$python gradenotify.pyを実行。IDとパスワードを入力する。  
  パスワードは入力した文字が表示されないようにしている。表示されなくても入力は出来ている。  
  
raspberrypiでのドライバ入手法  
  $sudo apt install chromium-chromedriver でインストールする。  
  $which chromedriver でインストール場所を調べることができるため、インストールされたパスをgradenotify.py内に書く。  
  参考ページ：https://irohaplat.com/raspberry-pi-selenium-installation/  
  
ファイル、フォルダの説明  
oldversion：旧バージョンの本体、使用していたファイルを格納。  
gradenotify.yml：必要なモジュールを記載。  
grade.csv：確認済み成績。証明書発行システムから引っ張ってきた成績と比較するためのもの。  
linetoken.txt:lineのトークンを保存するファイル。トークン以外は何も書かないように注意。  
readme.txt：この説明ファイル。  
  

バージョン履歴  
v1.0.0：  
・成績更新の有無のみ通知。  
  
v2.0.0：  
・成績更新の内容(科目名、評定)、評定が変わったことも通知するよう変更。  
  
v2.1.0：  
・ヘッドレスモード動作に変更  
・バグ修正(更新項目が末尾に来る場合に更新が検知されない問題を修正)。  
  
v3.0.0(2022/04/01)：  
・grade.csvに出力されるデータに単位数を追加。  
・grade.csvファイルが無かった場合は生成するよう変更。  
・lineトークンの記述場所をコード内から別ファイルへ移動。  
・ユーザーIDとパスワードをコードに直接書かずにプログラムを起動してから入力を求めるよう変更。  
  
v3.1.0(2022/08/29):  
・修士のアカウントが増えてログイン時に選択が必要になった部分について、修士のアカウントを選ぶよう変更。  
・selenium4.0になり書き方が変わった部分について変更。  
