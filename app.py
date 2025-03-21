import os
import threading
import time
import requests
from datetime import datetime
from flask import Flask, render_template, request, send_from_directory
from 척도9 import check_exam_availability, exam_categories  # ✅ 검사 로직 및 Google Sheets 데이터 가져오기

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

        # ✅ 검사 목록 쉼표 기준으로 분리
        exam_list = [exam.strip() for exam in exam_list.split(",") if exam.strip()]

        # ✅ Google Sheets에서 유효한 검사 목록 가져오기
        try:
            valid_exams = set(exam_categories.keys())  # ✅ 검사 목록 가져오기
        except Exception as e:
            valid_exams = set()  # 오류 발생 시 빈 세트로 처리
            result_text = f"<h3 style='color:red;'>❌ Google Sheets 로드 오류: {str(e)}</h3><br>"

        # ✅ 인식되지 않은 검사 찾기
        invalid_exams = [exam for exam in exam_list if exam.lower() not in valid_exams]
        valid_exam_list = [exam for exam in exam_list if exam.lower() in valid_exams]  # ✅ 유효한 검사만 남기기

        if visit_date:
            try:
                visit_date_parsed = datetime.strptime(visit_date, "%Y-%m-%d").date()
                result_text = check_exam_availability(visit_date_parsed, valid_exam_list)

                # ✅ 인식되지 않은 검사 목록을 바로 밑에 표시
                if invalid_exams:
                    result_text += f"<h3 style='color:red;'>❌ 인식하지 못한 검사 목록: {', '.join(invalid_exams)} (검사 목록 열람을 확인하세요)</h3><br>"

            except Exception as e:
                result_text = f"<h3 style='color:red;'>❌ 오류 발생: {str(e)}</h3>"

    # ✅ 항상 응답을 반환하도록 보장
    return render_template("index.html", result_text=result_text, visit_date=visit_date, exam_list=",".join(exam_list))
# ✅ Flask 실행 (반드시 이 위치에 있어야 함)
if __name__ == "__main__":
    app.run(debug=True)