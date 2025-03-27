import os
import threading
import time
import requests
from datetime import datetime, date
from flask import Flask, render_template, request, send_from_directory, redirect

from 척도9 import check_exam_availability, exam_categories, alias_to_name

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/check", methods=["GET", "POST"])
def check():
    result_text = ""
    today_str = date.today().isoformat()
    visit_date = request.form.get("visit_date", "") or today_str
    target_date = request.form.get("target_date", "") or today_str
    exam_list = request.form.get("exam_list", "")

    if request.method == "POST":
        raw_exams = [exam.strip() for exam in exam_list.split(",") if exam.strip()]
        processed_exam_list = [alias_to_name.get(e.lower(), e) for e in raw_exams]

        valid_exams = set(exam_categories.keys())
        invalid_exams = [e for e in processed_exam_list if e not in valid_exams]
        valid_exam_list = [e for e in processed_exam_list if e in valid_exams]

        try:
            visit_date_parsed = datetime.strptime(visit_date, "%Y-%m-%d").date()
            target_date_parsed = datetime.strptime(target_date, "%Y-%m-%d").date()

            result_text = check_exam_availability(
                visit_date_parsed,
                valid_exam_list,
                target_date=target_date_parsed
            )

            if invalid_exams:
                result_text += f"<h3 style='color:red;'>❌ 인식하지 못한 검사 목록: {', '.join(invalid_exams)}</h3><br>"

        except Exception as e:
            result_text = f"<h3 style='color:red;'>❌ 오류 발생: {str(e)}</h3>"

        exam_list = ",".join(processed_exam_list)

    return render_template(
        "index.html",
        result_text=result_text,
        visit_date=visit_date,
        target_date=target_date,
        exam_list=exam_list,
        exam_names=exam_categories.keys(),
        mapped_names=[
            f"{e} → {alias_to_name.get(e.lower(), '❌ 인식 불가')}" for e in raw_exams
        ] if request.method == "POST" else []
    )

@app.route("/contact")
def contact():
    return render_template("contact.html")

@app.route("/help")
def help():
    return render_template("help.html")

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/privacy")
def privacy():
    return render_template("privacy.html")

@app.route("/terms")
def terms():
    return render_template("terms.html")

# ✅ 자동 리디렉션 (onrender → 도메인)
@app.before_request
def redirect_to_custom_domain():
    if "psytest-checker.onrender.com" in request.host:
        return redirect("https://psytestchecker.com" + request.path, code=301)

# ✅ ads.txt 라우트
@app.route('/ads.txt')
def serve_ads_txt():
    return send_from_directory(os.path.dirname(os.path.abspath(__file__)), 'ads.txt', mimetype='text/plain')

# ✅ 광고 관련 설정
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

if __name__ == "__main__":
    app.run(debug=True)
