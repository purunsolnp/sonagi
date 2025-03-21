from flask import Flask, render_template, request
import requests
import 척도9  # ✅ 검사 로직을 포함한 파일
from 척도9 import check_exam_availability 
from datetime import datetime  # ✅ datetime 모듈 추가 (오류 해결)

app = Flask(__name__)

# ✅ GitHub 광고 URL
GITHUB_AD_URL = "https://raw.githubusercontent.com/purunsolnp/sonagi/main/adv_url.txt"

# ✅ 광고 URL 불러오기 함수
def get_ad_url():
    try:
        response = requests.get(GITHUB_AD_URL, timeout=5)
        ad_url = response.text.strip()
        if not ad_url or "http" not in ad_url:
            return "https://your-default-ad-url.com"
        return ad_url
    except:
        return "https://your-default-ad-url.com"

# ✅ Flask 웹 페이지 라우트
@app.route("/", methods=["GET", "POST"])
def index():
    result_text = ""  # 결과 초기화
    visit_date = ""
    exam_list = ""

    if request.method == "POST":
        visit_date = request.form.get("visit_date", "")
        exam_list = request.form.get("exam_list", "")

        if visit_date and exam_list:
            try:
                visit_date_parsed = datetime.strptime(visit_date, "%Y-%m-%d").date()
                result_text = check_exam_availability(visit_date_parsed, exam_list.split(","))
            except Exception as e:
                result_text = f"<h3 style='color:red;'>❌ 오류 발생: {str(e)}</h3>"

    return render_template("index.html", result_text=result_text, visit_date=visit_date, exam_list=exam_list)

if __name__ == "__main__":
    app.run(debug=True)