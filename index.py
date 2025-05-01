import requests
from bs4 import BeautifulSoup

import firebase_admin
from firebase_admin import credentials, firestore
cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred)

from flask import Flask, render_template, request,make_response, jsonify

from datetime import datetime, timezone, timedelta

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
    homepage += "<br><a href='/searchQ'>輸入關鍵字查詢電影</a><br>"
    homepage += "<br><a href='/searchR'>臺中市114年02月份十大易肇事路段(口)</a><br>"
    homepage += '<iframe width="350" height="430" allow="microphone;" src="https://console.dialogflow.com/api-client/demo/embedded/2573e812-2f68-4aca-8b81-f11f431c1e9f"></iframe>'

    return homepage

@app.route("/mis")
def course():
    return "<h1>資訊管理導論</h1>"

@app.route("/today")
def today():
    tz = timezone(timedelta(hours=+8))
    now = datetime.now(tz)
    return render_template("today.html", datetime=str(now))

@app.route("/about")
def me():
    return render_template("about.html")

@app.route("/welcome", methods=["GET"])
def welcome():
    user = request.values.get("nick")
    w = request.values.get("work")
    return render_template("welcome.html", name=user, work=w)

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
    result = sp.select(".filmListAllX li")
    db = firestore.client()
    count = 0

    for item in result:
        img = item.find("img")
        a = item.find("a")
        div = item.find(class_="runtime")

        # 處理片長
        if div and "片長:" in div.text:
            FilmLen = div.text.split("片長:")[-1].strip()
        else:
            FilmLen = "無"

        # 建立唯一ID（片碼）
        doc_id = a.get("href").split("/")[-2]

        doc = {
            "title": img.get("alt"),
            "picture": img.get("src"),
            "hyperlink": "http://www.atmovies.com.tw" + a.get("href"),
            "showDate": div.text[5:15],
            "showLength": FilmLen,
        }

        # 寫入「電影」 collection
        doc_ref = db.collection("電影").document(doc_id)
        doc_ref.set(doc)
        count += 1

    return f"共寫入 {count} 筆電影資料到 Firestore 的『電影』collection。"

@app.route("/searchQ", methods=["POST", "GET"])
def searchQ():
    if request.method == "POST":
        MovieTitle = request.form.get("MovieTitle", "").strip()
        info = ""
        db = firestore.client()
        collection_ref = db.collection("電影")
        docs = collection_ref.order_by("showDate").get()

        for doc in docs:
            movie = doc.to_dict()
            title = movie.get("title", "").strip()
            if MovieTitle.lower() in title.lower():  # 不區分大小寫
                info += f'<h3><a href="/movieinfo/{doc.id}">{movie["title"]}</a></h3>'
                info += f'<img src="{movie["picture"]}" width="150"><br>'
                info += f'片長：{movie["showLength"]} 分鐘<br>'
                info += f'上映日期：{movie["showDate"]}<br><br>'

        if info == "":
            info = "找不到符合的電影"
        return info
    else:
        return render_template("input.html")


@app.route("/movieinfo/<doc_id>")
def movieinfo(doc_id):
    db = firestore.client()
    doc_ref = db.collection("電影").document(doc_id)
    doc = doc_ref.get()
    if doc.exists:
        movie = doc.to_dict()
        html = f"<h2>{movie['title']}</h2>"
        html += f"<img src='{movie['picture']}' width='200'><br>"
        html += f"片長：{movie['showLength']} 分鐘<br>"
        html += f"上映日期：{movie['showDate']}<br>"
        html += f"<a href='{movie['hyperlink']}' target='_blank'>前往開眼電影介紹</a><br>"
        return html
    else:
        return "找不到這部電影"

@app.route("/searchR", methods=["GET", "POST"])
def max_accidents():
    if request.method == "POST":  
        keyword = request.form["keyword"]  
        result = ""  
        url = "https://datacenter.taichung.gov.tw/swagger/OpenData/1289c779-6efa-4e7c-bac8-aa6cbe84a58c"  # 資料來源API網址

        try:
            response = requests.get(url)  
            data = response.json()   

            # 確保資料格式正確
            if not isinstance(data, list):
                return "資料格式錯誤，請檢查API是否正確返回資料"

            # 遍歷資料，檢查是否包含關鍵字
            for item in data:
                if "路口名稱" in item and keyword.lower() in item["路口名稱"].lower():
                    result += f"{item['路口名稱']}：發生 {item.get('總件數', '未知')} 件，主因是 {item.get('主要肇因', '未知')}<br><br>"

            return result or "查無相關資料"  

        except Exception as e:  
            return f"資料處理發生錯誤：{str(e)}"

    else:
        
        return '''
        <form method="POST">
            <h2>查詢114年2月台中十大易肇事路口</h2>
            請輸入路口關鍵字：<input name="keyword">
            <input type="submit" value="查詢">
        </form>
        '''

@app.route("/rate")
def rate():
    url = "http://www.atmovies.com.tw/movie/next/"
    Data = requests.get(url)
    Data.encoding = "utf-8"
    sp = BeautifulSoup(Data.text, "html.parser")
    result=sp.select(".filmListAllX li")
    lastUpdate = sp.find(class_="smaller09").text[5:]

    for x in result:
        picture = x.find("img").get("src").replace(" ", "")
        title = x.find("img").get("alt")    
        movie_id = x.find("div", class_="filmtitle").find("a").get("href").replace("/", "").replace("movie", "")
        hyperlink = "http://www.atmovies.com.tw" + x.find("a").get("href")

        t = x.find(class_="runtime").text
        showDate = t[5:15]

        showLength = ""
        if "片長" in t:
            t1 = t.find("片長")
            t2 = t.find("分")
            showLength = t[t1+3:t2]

        r = x.find(class_="runtime").find("img")
        rate = ""
        if r != None:
            rr = r.get("src").replace("/images/cer_", "").replace(".gif", "")
            if rr == "G":
                rate = "普遍級"
            elif rr == "P":
                rate = "保護級"
            elif rr == "F2":
                rate = "輔12級"
            elif rr == "F5":
                rate = "輔15級"
            else:
                rate = "限制級"

        doc = {
            "title": title,
            "picture": picture,
            "hyperlink": hyperlink,
            "showDate": showDate,
            "showLength": showLength,
            "rate": rate,
            "lastUpdate": lastUpdate
        }

        db = firestore.client()
        doc_ref = db.collection("電影含分級").document(movie_id)
        doc_ref.set(doc)
    return "近期上映電影已爬蟲及存檔完畢，網站最近更新日期為：" + lastUpdate


@app.route("/webhook3", methods=["POST"])
def webhook3():
    # build a request object
    req = request.get_json(force=True)
    # fetch queryResult from json
    action =  req.get("queryResult").get("action")
    #msg =  req.get("queryResult").get("queryText")
    #info = "動作：" + action + "； 查詢內容：" + msg
    if (action == "rateChoice"):
        rate =  req.get("queryResult").get("parameters").get("rate")
        info = "我是黃柏彰開發的電影聊天機器人,您選擇的電影分級是：" + rate + "，相關電影：\n"
        db = firestore.client()
        collection_ref = db.collection("電影含分級")
        docs = collection_ref.get()
        result = ""
        for doc in docs:
            dict = doc.to_dict()
            if rate in dict["rate"]:
                result += "片名：" + dict["title"] + "\n"
                result += "介紹：" + dict["hyperlink"] + "\n\n"
        info += result
    return make_response(jsonify({"fulfillmentText": info}))





# 僅供本機測試時使用
if __name__ == "__main__":
    app.run(debug=True)
