import os
import threading
import time
import requests
from datetime import datetime
from flask import Flask, render_template, request, send_from_directory
from 척도9 import check_exam_availability  # ✅ 검사 로직 함수

app = Flask(__name__)

# ✅ ads.txt 라우트
@app.route('/ads.txt')
def serve_ads_txt():
    return send_from_directory(os.path.dirname(os.path.abspath(__file__)), 'ads.txt', mimetype='text/plain')

# ✅ 광고 설정
GITHUB_AD_URL = "https://raw.githubusercontent.com/purunsolnp/sonagi/main/adv_url.txt"
DEFAULT_AD_URL = "https://your-default-ad-url.com"
AD_URL_CACHE = DEFAULT_AD_URL

def get_ad_url():
    global AD_URL_CACHE
    try:
        response = requests.get(GITHUB_AD_URL, timeout=5)
        response.raise_for_status()
        ad_urls = [url.strip() for url in response.text.strip().split("\n") if url.startswith("http")]
        if ad_urls:
            AD_URL_CACHE = ad_urls[0]
    except:
        AD_URL_CACHE = DEFAULT_AD_URL

def update_ad_url():
    while True:
        get_ad_url()
        time.sleep(600)

threading.Thread(target=update_ad_url, daemon=True).start()

@app.route("/get_ad_url")
def get_ad_url_api():
    return AD_URL_CACHE

@app.route("/", methods=["GET", "POST"])
def index():
    result_text = ""
    visit_date = ""
    exam_list = ""

    if request.method == "POST":
        visit_date = request.form.get("visit_date", "")
        exam_list = request.form.get("exam_list", "")
        if visit_date:
            try:
                visit_date_parsed = datetime.strptime(visit_date, "%Y-%m-%d").date()
                exam_list = exam_list.split(",") if exam_list else []
                result_text = check_exam_availability(visit_date_parsed, exam_list)
            except Exception as e:
                result_text = f"<h3 style='color:red;'>❌ 오류 발생: {str(e)}</h3>"

    return render_template("index.html", result_text=result_text, visit_date=visit_date, exam_list=exam_list)

if __name__ == "__main__":
    app.run(debug=True)