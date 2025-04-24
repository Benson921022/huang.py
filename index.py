import requests
from bs4 import BeautifulSoup


import firebase_admin
from firebase_admin import credentials, firestore
cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred)

from flask import Flask, render_template, request
from datetime import datetime, timezone, timedelta
from waitress import serve

app = Flask(__name__)

@app.route("/")
def index():
    homepage = "<h1>黃柏彰Python網頁(時間+8)</h1>"
    homepage += "<a href=/mis>MIS</a><br>"
    homepage += "<a href=/today>顯示日期時間</a><br>"
    homepage += "<a href=/welcome?nick=tcyang&work=pu>傳送使用者暱稱</a><br>"
    homepage += "<a href=/account>網頁表單傳值</a><br>"
    homepage += "<a href=/about>柏彰簡介網頁</a><br>"
    homepage += "<br><a href=/read>讀取Firestore資料</a><br>"
    homepage += "<br><a href=/movie>讀取開眼電影即將上映影片，寫入Firestore</a><br>"
    homepage += "<br><a href='/searchQ'>電影查詢</a><br>"
    

    return homepage


@app.route("/mis")
def course():
    return "<h1>資訊管理導論</h1>"


@app.route("/today")
def today():
    tz = timezone(timedelta(hours=+8))
    now = datetime.now(tz)
    return render_template("today.html", datetime = str(now))


@app.route("/about")
def me():
    return render_template("about.html")

@app.route("/welcome", methods=["GET"])
def welcome():
    user = request.values.get("nick")
    w = request.values.get("work")
    return render_template("welcome.html", name= user, work = w)


@app.route("/account", methods=["GET", "POST"])
def account():
    if request.method == "POST":
        user = request.form["user"]
        pwd = request.form["pwd"]
        result = "您輸入的帳號是：" + user + "; 密碼為：" + pwd 
        return result
    else:
        return render_template("account.html")

@app.route("/read")
def read():
    Result = ""
    db = firestore.client()
    collection_ref = db.collection("靜宜資管")    
    docs = collection_ref.get()    
    for doc in docs:         
        Result += "文件內容：{}".format(doc.to_dict()) + "<br>"    
    return Result

@app.route("/movie")
def movie():
  url = "http://www.atmovies.com.tw/movie/next/"
  Data = requests.get(url)
  Data.encoding = "utf-8"
  sp = BeautifulSoup(Data.text, "html.parser")
  result=sp.select(".filmListAllX li")
  lastUpdate = sp.find("div", class_="smaller09").text[5:]
  
  db = firestore.client()
  count = 0 

  for item in result:
        img = item.find("img")
        print("片名:",img.get("alt"))
        print("海報:",img.get("src"))
        a = item.find("a")
        print("介紹:","http://www.atmovie.com.tw" + a.get("href"))
        print("編號:",a.get("href")[7:9])
        div = item.find(class_="runtime")
        #print("日期:", div.text[15:5])

        if div.text.find("片長:")> 0:
            FilmLen = div.text[21:]
            print("片長:", div.text[21:])
        else:
            FilmLen = "無"
            print("目前無片長資訊")

        doc = {
            "title": img.get("alt"),
            "picture": img.get("src"),
            "hyperlink": "http://www.atmovie.com.tw" + a.get("href"),
            "showDate": div.text[5:15],
            "showLength": FilmLen,
        
        }

        db = firestore.client()
        doc_ref = db.collection("黃柏彰").document(a.get("href")[7:9])
        doc_ref.set(doc)
        count += 1

  return "資料庫已更新" 

@app.route("/searchQ", methods=["POST", "GET"])
def searchQ():
    if request.method == "POST":
        MovieTitle = request.form.get("MovieTitle", "")
        info = ""
        db = firestore.client()     
        collection_ref = db.collection("電影")
        docs = collection_ref.order_by("showDate").get()
        for doc in docs:
            if MovieTitle in doc.to_dict().get("title", ""): 
                info += "片名：" + doc.to_dict()["title"] + "<br>" 
                info += "影片介紹：" + doc.to_dict()["hyperlink"] + "<br>"
                info += "片長：" + doc.to_dict()["showLength"] + " 分鐘<br>" 
                info += "上映日期：" + doc.to_dict()["showDate"] + "<br><br>"           
        if info == "":
            info = "找不到符合的電影"
        return info
    else:  
        return render_template("input.html")



if __name__ == "__main__":
    app.run()
    serve(app,host='0.0.0.0',post=8080)
