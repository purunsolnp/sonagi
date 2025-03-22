import os
import threading
import time
import requests
from datetime import datetime
from flask import Flask, render_template, request, send_from_directory, redirect

# ✅ alias_to_name 추가로 불러오기
from 척도9 import check_exam_availability, exam_categories, alias_to_name

app = Flask(__name__)

# ✅ 자동 리디렉션 설정 (onrender.com → psytestchecker.com)
@app.before_request
def redirect_to_custom_domain():
    if "psytest-checker.onrender.com" in request.host:
        return redirect("https://psytestchecker.com" + request.path, code=301)

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

        # ✅ 사용자 입력 분리
        raw_exams = [exam.strip() for exam in exam_list.split(",") if exam.strip()]

        # ✅ alias 매핑을 통해 검사명으로 변환
        processed_exam_list = []
        for exam in raw_exams:
            key = exam.lower()
            if key in alias_to_name:
                processed_exam_list.append(alias_to_name[key])
            else:
                processed_exam_list.append(exam)

        # ✅ 유효 검사 분리
        try:
            valid_exams = set(exam_categories.keys())
        except Exception as e:
            valid_exams = set()
            result_text = f"<h3 style='color:red;'>❌ Google Sheets 로드 오류: {str(e)}</h3><br>"

        invalid_exams = [exam for exam in processed_exam_list if exam not in valid_exams]
        valid_exam_list = [exam for exam in processed_exam_list if exam in valid_exams]

        if visit_date:
            try:
                visit_date_parsed = datetime.strptime(visit_date, "%Y-%m-%d").date()
                result_text = check_exam_availability(visit_date_parsed, valid_exam_list)

                # ✅ 인식 실패 검사 따로 출력
                if invalid_exams:
                    result_text += f"<h3 style='color:red;'>❌ 인식하지 못한 검사 목록: {', '.join(invalid_exams)} (검사 목록 열람을 확인하세요)</h3><br>"

            except Exception as e:
                result_text = f"<h3 style='color:red;'>❌ 오류 발생: {str(e)}</h3>"

    return render_template("index.html", result_text=result_text, visit_date=visit_date, exam_list=",".join(exam_list))

# ✅ Flask 실행
if __name__ == "__main__":
    app.run(debug=True)