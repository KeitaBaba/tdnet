from bs4 import BeautifulSoup
import urllib.request
import datetime
import MySQLdb
import json
import requests
import list

#MySQL接続
connection = MySQLdb.connect(
    host='host', user='user', passwd='password', db='db', charset='utf8')
cursor = connection.cursor()

#テーブル作成
cursor.execute("""CREATE TABLE IF NOT EXISTS tekijikaiji(
                id INT auto_increment,
                date VARCHAR(10) CHARACTER SET utf8 COLLATE utf8_general_ci,
                company_code INT,
                company_name VARCHAR(300) CHARACTER SET utf8 COLLATE utf8_general_ci,
                company_title VARCHAR(300) CHARACTER SET utf8 COLLATE utf8_general_ci,
                company_url VARCHAR(300) CHARACTER SET utf8 COLLATE utf8_general_ci,
                PRIMARY KEY (id));""")

WEB_HOOK_URL= "WEB_HOOK_URL"

#日付設定
d_today = datetime.date.today()
sdate = d_today.strftime('%Y%m%d')

#tdnet取得
url = f"https://www.release.tdnet.info/inbs/I_list_001_{sdate}.html"
sub_url="https://www.release.tdnet.info/inbs/"
html = urllib.request.urlopen(url)
bs = BeautifulSoup(html.read(),"html.parser")
tables = bs.find_all("table")[3]
trs=tables.find_all("tr")

for tr in trs:
    date=tr.find("td",class_="kjTime").get_text()
    code=tr.find("td",class_="kjCode").get_text()
    name=tr.find("td",class_="kjName").get_text()
    title=tr.find("td",class_="kjTitle")
    title_text=title.get_text()
    url=sub_url+title.find("a").get("href")

    #新情報ならdbに保存,slack通知
    if code in list.code_list:
        cursor.execute("SELECT * FROM tekijikaiji WHERE company_name = %s AND company_title = %s", (name,title_text))
        if cursor.rowcount== 0:
            print("更新あり")
            requests.post(WEB_HOOK_URL, data=json.dumps({
            "text" : name,
              'attachments': [{
                    'title': title_text,
                   'title_link': url
                }]
            }))
            cursor.execute("INSERT INTO tekijikaiji VALUES (%s, %s, %s, %s, %s, %s)", (0, date, code, name, title_text, url))
    
    
connection.commit()
connection.close()