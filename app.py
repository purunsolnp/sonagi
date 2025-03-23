import os
import threading
import time
import requests
from datetime import datetime, date
from flask import Flask, render_template, request, send_from_directory, redirect

# ✅ alias_to_name 추가로 불러오기
from 척도9 import check_exam_availability, exam_categories, alias_to_name

app = Flask(__name__)

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

    # ✅ 날짜 기본값 설정 추가
    today_str = date.today().isoformat()
    visit_date = request.form.get("visit_date", "") or today_str
    target_date = request.form.get("target_date", "") or today_str
    exam_list = request.form.get("exam_list", "")

    if request.method == "POST":
        # ✅ 사용자 입력 분리 (원본 보존)
        raw_exams = [exam.strip() for exam in exam_list.split(",") if exam.strip()]

        # ✅ alias 매핑을 통해 정식 검사명으로 변환
        processed_exam_list = []
        for exam in raw_exams:
            key = exam.lower()
            if key in alias_to_name:
                processed_exam_list.append(alias_to_name[key])
            else:
                processed_exam_list.append(exam)

        # ✅ 유효 검사만 추출
        try:
            valid_exams = set(exam_categories.keys())
        except Exception as e:
            valid_exams = set()
            result_text = f"<h3 style='color:red;'>❌ Google Sheets 로드 오류: {str(e)}</h3><br>"

        invalid_exams = [exam for exam in processed_exam_list if exam not in valid_exams]
        valid_exam_list = [exam for exam in processed_exam_list if exam in valid_exams]

        # ✅ 검사 일정 결과 처리
        if visit_date:
            try:
                visit_date_parsed = datetime.strptime(visit_date, "%Y-%m-%d").date()
                target_date_parsed = datetime.strptime(target_date, "%Y-%m-%d").date()

                result_text = check_exam_availability(
                    visit_date_parsed,
                    valid_exam_list,
                    target_date=target_date_parsed
                )

                if invalid_exams:
                    result_text += f"<h3 style='color:red;'>❌ 인식하지 못한 검사 목록: {', '.join(invalid_exams)} (검사 목록 열람을 확인하세요)</h3><br>"

            except Exception as e:
                result_text = f"<h3 style='color:red;'>❌ 오류 발생: {str(e)}</h3>"

        # ✅ 입력창에 검사명 기준 정규화된 목록을 표시
        exam_list = ",".join([alias_to_name.get(exam.lower(), exam) for exam in raw_exams])

    

# ✅ 결과 템플릿 렌더링
    return render_template(
        "index.html",
        result_text=result_text,
        visit_date=visit_date,           # ✅ app.py 상단에서 미리 설정한 값 사용
        target_date=target_date,         # ✅ 위와 동일
        exam_list=exam_list,
        exam_names=exam_categories.keys(),
        mapped_names=[f"{e} → {alias_to_name.get(e.lower(), '❌ 인식 불가')}" for e in raw_exams] if request.method == "POST" else []
    )
# ✅ Flask 실행
if __name__ == "__main__":
    app.run(debug=True)