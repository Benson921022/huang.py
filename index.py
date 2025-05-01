import os
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timezone, timedelta
from flask import Flask, render_template, request, make_response, jsonify

import firebase_admin
from firebase_admin import credentials, firestore

# Firebase 初始化
cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred)
db = firestore.client()

app = Flask(__name__)

@app.route("/")
def index():
    homepage = """
    <h1>黃柏彰Python網頁(時間+8)</h1>
    <a href=/mis>MIS</a><br>
    <a href=/today>顯示日期時間</a><br>
    <a href=/welcome?nick=tcyang&work=pu>傳送使用者暱稱</a><br>
    <a href=/account>網頁表單傳值</a><br>
    <a href=/about>柏彰簡介網頁</a><br>
    <a href=/read>讀取Firestore資料</a><br>
    <a href=/movie>爬蟲電影資料，寫入Firestore</a><br>
    <a href=/rate>爬蟲含分級電影資料，寫入Firestore</a><br>
    <a href=/searchQ>輸入關鍵字查詢電影</a><br>
    <a href=/searchR>查詢台中肇事路段</a><br><br>
    <iframe width="350" height="430" allow="microphone;" src="https://console.dialogflow.com/api-client/demo/embedded/2573e812-2f68-4aca-8b81-f11f431c1e9f"></iframe>
    """
    return homepage

@app.route("/mis")
def course():
    return "<h1>資訊管理導論</h1>"

@app.route("/today")
def today():
    now = datetime.now(timezone(timedelta(hours=+8)))
    return render_template("today.html", datetime=str(now))

@app.route("/about")
def me():
    return render_template("about.html")

@app.route("/welcome")
def welcome():
    user = request.values.get("nick")
    w = request.values.get("work")
    return render_template("welcome.html", name=user, work=w)

@app.route("/account", methods=["GET", "POST"])
def account():
    if request.method == "POST":
        user = request.form.get("user", "")
        pwd = request.form.get("pwd", "")
        return f"您輸入的帳號是：{user}; 密碼為：{pwd}"
    return render_template("account.html")

@app.route("/read")
def read():
    result = ""
    try:
        docs = db.collection("靜宜資管").get()
        for doc in docs:
            result += f"文件內容：{doc.to_dict()}<br>"
    except Exception as e:
        result = f"讀取資料錯誤：{e}"
    return result

@app.route("/movie")
def movie():
    url = "http://www.atmovies.com.tw/movie/next/"
    res = requests.get(url)
    res.encoding = "utf-8"
    soup = BeautifulSoup(res.text, "html.parser")
    movies = soup.select(".filmListAllX li")
    count = 0

    for item in movies:
        try:
            img = item.find("img")
            a = item.find("a")
            div = item.find(class_="runtime")

            FilmLen = "無"
            if div and "片長:" in div.text:
                FilmLen = div.text.split("片長:")[-1].strip()

            doc_id = a.get("href").split("/")[-2]
            showDate = div.text[5:15] if div and len(div.text) >= 15 else "未知"

            doc = {
                "title": img.get("alt"),
                "picture": img.get("src"),
                "hyperlink": "http://www.atmovies.com.tw" + a.get("href"),
                "showDate": showDate,
                "showLength": FilmLen
            }

            db.collection("電影").document(doc_id).set(doc)
            count += 1
        except Exception as e:
            print("錯誤電影項目：", e)

    return f"共寫入 {count} 筆電影資料"

@app.route("/searchQ", methods=["GET", "POST"])
def searchQ():
    if request.method == "POST":
        MovieTitle = request.form.get("MovieTitle", "").strip()
        info = ""
        docs = db.collection("電影").order_by("showDate").get()
        for doc in docs:
            movie = doc.to_dict()
            if MovieTitle.lower() in movie.get("title", "").lower():
                info += f'<h3><a href="/movieinfo/{doc.id}">{movie["title"]}</a></h3>'
                info += f'<img src="{movie["picture"]}" width="150"><br>'
                info += f'片長：{movie["showLength"]}<br>'
                info += f'上映日期：{movie["showDate"]}<br><br>'
        return info or "找不到符合的電影"
    return render_template("input.html")

@app.route("/movieinfo/<doc_id>")
def movieinfo(doc_id):
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
    return "找不到這部電影"

@app.route("/searchR", methods=["GET", "POST"])
def max_accidents():
    if request.method == "POST":
        keyword = request.form.get("keyword", "")
        url = "https://datacenter.taichung.gov.tw/swagger/OpenData/1289c779-6efa-4e7c-bac8-aa6cbe84a58c"
        try:
            response = requests.get(url)
            data = response.json()
            result = ""
            for item in data:
                if isinstance(item, dict) and "路口名稱" in item:
                    if keyword.lower() in item["路口名稱"].lower():
                        result += f"{item['路口名稱']}：發生 {item.get('總件數', '未知')} 件，主因是 {item.get('主要肇因', '未知')}<br><br>"
            return result or "查無相關資料"
        except Exception as e:
            return f"發生錯誤：{e}"
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
    res = requests.get(url)
    res.encoding = "utf-8"
    soup = BeautifulSoup(res.text, "html.parser")
    result = soup.select(".filmListAllX li")
    lastUpdate = soup.find(class_="smaller09").text[5:]

    for item in result:
        try:
            picture = item.find("img").get("src").replace(" ", "")
            title = item.find("img").get("alt")
            movie_id = item.find("div", class_="filmtitle").find("a").get("href").replace("/", "").replace("movie", "")
            hyperlink = "http://www.atmovies.com.tw" + item.find("a").get("href")
            t = item.find(class_="runtime").text
            showDate = t[5:15] if len(t) >= 15 else "未知"

            showLength = ""
            if "片長" in t:
                t1 = t.find("片長")
                t2 = t.find("分")
                showLength = t[t1+3:t2]

            rate = "未知"
            r = item.find(class_="runtime").find("img")
            if r:
                rr = r.get("src").replace("/images/cer_", "").replace(".gif", "")
                rate = {
                    "G": "普遍級", "P": "保護級", "F2": "輔12級", "F5": "輔15級"
                }.get(rr, "限制級")

            doc = {
                "title": title,
                "picture": picture,
                "hyperlink": hyperlink,
                "showDate": showDate,
                "showLength": showLength,
                "rate": rate,
                "lastUpdate": lastUpdate
            }

            db.collection("電影含分級").document(movie_id).set(doc)
        except Exception as e:
            print("錯誤電影分級項目：", e)

    return f"電影含分級資料更新完成，更新時間：{lastUpdate}"

@app.route("/webhook3", methods=["POST"])
def webhook3():
    req = request.get_json(force=True)
    action = req.get("queryResult", {}).get("action", "")
    if action == "rateChoice":
        rate = req.get("queryResult", {}).get("parameters", {}).get("rate", "")
        if not rate:
            return make_response(jsonify({"fulfillmentText": "請提供電影分級，例如『普遍級』"}))

        info = f"您選擇的電影分級是：{rate}，相關電影如下：\n"
        docs = db.collection("電影含分級").get()
        matched = ""

        for doc in docs:
            data = doc.to_dict()
            if rate in data.get("rate", ""):
                matched += f"片名：{data['title']}\n介紹：{data['hyperlink']}\n\n"

        return make_response(jsonify({"fulfillmentText": info + (matched or '目前無資料')}))
    return make_response(jsonify({"fulfillmentText": "未定義的動作"}))


if __name__ == "__main__":
    app.run(debug=True)
