import os
import threading
import time
import requests
from datetime import datetime, date, timedelta
from flask import Flask, render_template, request, send_from_directory, redirect
from dateutil.relativedelta import relativedelta

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

            # --- 급성기/만성기 정보 추가 (중복 안내 통합) ---
            from dateutil.relativedelta import relativedelta
            from datetime import timedelta
            acute_end_date = visit_date_parsed + relativedelta(months=6)
            today_or_target = target_date_parsed
            # 1. 급성기 종료일 및 상태 안내 통합
            acute_info = f"""
            <h3>📅 급성기 종료일: {acute_end_date.strftime('%Y-%m-%d')} (초진일 {visit_date_parsed.strftime('%Y-%m-%d')} 기준 6개월 후)</h3>
            <p>{'<b style=\'color:blue;\'>급성기 진행 중</b>' if today_or_target < acute_end_date else '<b style=\'color:green;\'>급성기 종료됨 현재 만성기 입니다.</b>'}</p>
            """
            # 2. 만성기 관리 구간 (이전, 현재, 다음 구간)
            followup_start = acute_end_date + timedelta(days=1)
            periods = []
            cur_start = followup_start
            idx = 0
            found_idx = None
            while True:
                cur_end = cur_start + relativedelta(months=3) - timedelta(days=1)
                periods.append((cur_start, cur_end))
                if cur_start <= today_or_target <= cur_end:
                    found_idx = idx
                    break
                cur_start = cur_end + timedelta(days=1)
                idx += 1
            prev_period = periods[found_idx-1] if found_idx-1 >= 0 else None
            cur_period = periods[found_idx]
            next_period = (cur_period[1] + timedelta(days=1), cur_period[1] + relativedelta(months=3))
            chronic_info = f"""
            <h3>🩺 만성기 관리 구간</h3>
            """
            if prev_period:
                chronic_info += f"이전 구간: {prev_period[0].strftime('%Y-%m-%d')} ~ {prev_period[1].strftime('%Y-%m-%d')}<br>"
            chronic_info += f"<b>현재 구간: {cur_period[0].strftime('%Y-%m-%d')} ~ {cur_period[1].strftime('%Y-%m-%d')}</b><br>"
            chronic_info += f"다음 구간: {next_period[0].strftime('%Y-%m-%d')} ~ {next_period[1].strftime('%Y-%m-%d')}<br>"
            result_text += acute_info + chronic_info
            # --- 끝 ---

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

@app.route("/acute_phase", methods=["GET", "POST"])
def acute_phase():
    result_text = ""
    today = date.today()
    visit_date_str = request.form.get("visit_date", "")
    visit_date = None
    error = None
    if request.method == "POST":
        try:
            if not visit_date_str:
                raise ValueError("초진일자를 입력해 주세요.")
            # 날짜 위젯 또는 yyyy-mm-dd 형식 모두 허용
            visit_date = datetime.strptime(visit_date_str, "%Y-%m-%d").date()
        except Exception as e:
            error = f"<span style='color:red;'>날짜 형식 오류: {str(e)}</span>"
    if visit_date:
        # 1. 급성기 종료 여부
        acute_end_date = visit_date + relativedelta(months=6)
        if today < acute_end_date:
            acute_status = f"<b style='color:blue;'>급성기 진행 중</b>"
        else:
            acute_status = f"<b style='color:green;'>급성기 종료됨</b>"
        result_text += f"<h3>1. 급성기 종료 여부</h3>"
        result_text += f"{acute_status} (급성기 종료일: <b>{acute_end_date.strftime('%Y-%m-%d')}</b>)<br><br>"
        # 2. 후속 관리 구간 계산
        followup_start = acute_end_date + timedelta(days=1)
        periods = []
        cur_start = followup_start
        while True:
            cur_end = cur_start + relativedelta(months=3) - timedelta(days=1)
            periods.append((cur_start, cur_end))
            if today <= cur_end:
                break
            cur_start = cur_end + timedelta(days=1)
        # 이전, 현재, 다음 구간만 추출
        idx = len(periods) - 1
        prev_period = periods[idx-1] if idx-1 >= 0 else None
        cur_period = periods[idx]
        next_period = (cur_period[1] + timedelta(days=1), cur_period[1] + relativedelta(months=3))
        result_text += f"<h3>2. 오늘 날짜가 포함된 후속 관리 구간</h3>"
        if prev_period:
            result_text += f"이전 구간: {prev_period[0].strftime('%Y-%m-%d')} ~ {prev_period[1].strftime('%Y-%m-%d')}<br>"
        # 현재 구간은 굵게
        result_text += f"<b>오늘은 {cur_period[0].strftime('%Y-%m-%d')} ~ {cur_period[1].strftime('%Y-%m-%d')} 구간에 해당합니다.</b><br>"
        result_text += f"다음 구간: {next_period[0].strftime('%Y-%m-%d')} ~ {next_period[1].strftime('%Y-%m-%d')}<br>"
    elif error:
        result_text = error
    return render_template(
        "acute_phase.html",
        result_text=result_text,
        visit_date=visit_date_str or ""
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
