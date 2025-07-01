from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import requests
import pandas as pd

def load_exam_data_from_gsheet(sheet_url):
    try:
        df = pd.read_csv(sheet_url)
        exam_dict = {}
        alias_to_name = {}

        for _, row in df.iterrows():
            name = str(row["검사명"]).strip().lower()
            exam_dict[name] = (
                row["카테고리"],
                row["레벨"],
                row["검사방식"]
            )
            alias_to_name[name] = name
            for key in ["한글명", "청구코드"]:
                alias = str(row.get(key, "")).strip().lower()
                if alias:
                    alias_to_name[alias] = name

        return exam_dict, alias_to_name
    except Exception as e:
        print(f"[오류] Google Sheets 불러오기 실패: {e}")
        return {}, {}

# ✅ 구글 시트 주소
GSHEET_URL = "https://docs.google.com/spreadsheets/d/1NUwlaPgSy2Jmc8eBlQ875tgxrwQVYylaB2ys8QSZzVc/export?format=csv&gid=0"
exam_categories, alias_to_name = load_exam_data_from_gsheet(GSHEET_URL)

GITHUB_AD_URL = "https://raw.githubusercontent.com/purunsolnp/sonagi/main/adv_url.txt"
DEFAULT_AD_URL = "https://your-default-page.com"

def calculate_six_months_date(visit_date):
    """초진일로부터 정확히 6개월(180일) 후 날짜를 계산"""
    return visit_date + timedelta(days=180)

def calculate_days_since_visit(visit_date, target_date):
    """초진일로부터 경과된 일수를 계산"""
    return (target_date - visit_date).days

def calculate_exam_limit(visit_date, target_date):
    days_since = calculate_days_since_visit(visit_date, target_date)
    
    if target_date == visit_date:
        max_exams = 12
    elif days_since < 180:  # 6개월(180일) 미만
        max_exams = 6
    else:  # 6개월(180일) 이상
        max_exams = 2

    return days_since, max_exams

def check_exam_availability(visit_date_str, selected_exams, target_date=None):
    try:
        if isinstance(visit_date_str, str):
            visit_date = datetime.strptime(visit_date_str, "%Y-%m-%d").date()
        else:
            visit_date = visit_date_str

        if target_date is None:
            today = datetime.today().date()
        else:
            today = target_date

        # ✅ 진료일이 초진일보다 과거일 경우 경고 출력
        if today < visit_date:
            return f"""
            <h3 style='color:red; font-size:16px; line-height:1.4; margin-bottom:5px;'>
            ❌ 진료일({today})이 초진일({visit_date})보다 이전입니다. 날짜를 다시 설정해주세요.
            </h3>
            """

        days_since = calculate_days_since_visit(visit_date, today)
        six_months_date = calculate_six_months_date(visit_date)

        if (today - visit_date).days == 0:
            max_exams = 12
        elif days_since < 180:  # 6개월(180일) 미만
            max_exams = 6
        else:  # 6개월(180일) 이상
            max_exams = 2

        result_text = f"""
        <h3 style='color:blue; font-size:16px; line-height:1.4; margin-bottom:5px;'>
            📅 초진일 ({visit_date}) 기준 6개월 후는 {six_months_date.year}년 {six_months_date.month}월 {six_months_date.day}일 입니다.
        </h3>
        <h4 style='color:blue; font-size:14px; line-height:1.4; margin-bottom:5px;'>
            📊 현재까지 경과일: {days_since}일
        </h4>
        """

        exam_info_list = []
        invalid_exams = []
        category_count = {}
        duplicate_exams = []

        for exam in selected_exams:
            info = exam_categories.get(exam.strip().lower())
            if info:
                category, level, exam_type = info
                exam_display = f'<strong>{exam} ({category}, {level}, {exam_type})</strong>'
                exam_info_list.append(exam_display)

                if (category, exam_type) in category_count:
                    duplicate_exams.append(
                        f"<p style='color:red; font-size:16px; line-height:1.4; margin-bottom:5px;'>"
                        f"❌ {category}({exam_type}): {category_count[(category, exam_type)]} & {exam} 중복되어 불가능합니다."
                        f"</p>"
                    )
                else:
                    category_count[(category, exam_type)] = exam
            else:
                invalid_exams.append(exam)

        result_text += f"""
        <h4 style='font-size:16px; line-height:1.4; margin-bottom:5px;'>📌 입력한 검사 목록:</h4>
        <p style='font-size:16px; line-height:1.4; margin-bottom:10px;'>{', '.join(exam_info_list)}</p>
        """

        if invalid_exams:
            result_text += f"""
            <h3 style='color:red; font-size:16px; line-height:1.4; margin-bottom:5px;'>
                ❌ 인식하지 못한 검사 목록: {', '.join(invalid_exams)} (검사 목록 열람을 확인하세요)
            </h3>
            """
        else:
            result_text += """
            <h3 style='color:green; font-size:16px; line-height:1.4; margin-bottom:5px;'>
                ✅ 모든 검사가 정상적으로 인식되었습니다.
            </h3>
            """

        if duplicate_exams:
            result_text += "<h3 style='color:red; font-size:16px; line-height:1.4; margin-bottom:5px;'>❌ 중복된 평가 영역이 있습니다:</h3>"
            result_text += "".join(duplicate_exams)
        else:
            result_text += """
            <h3 style='color:green; font-size:16px; line-height:1.4; margin-bottom:5px;'>
                ✅ 중복되는 검사가 없습니다.
            </h3>
            """

        valid_exam_count = len(exam_info_list)
        if valid_exam_count > max_exams:
            result_text += f"""
            <h3 style='color:red; font-size:16px; line-height:1.4; margin-bottom:5px;'>
             ❌ 검사 개수를 초과했습니다! (인식된 검사 기준: {valid_exam_count} / 최대 {max_exams}개)
            </h3>
            <p style='color:blue; font-size:14px; line-height:1.4; margin-bottom:5px;'>
             💡 현재 {days_since}일 경과로 {'6개월 미만' if days_since < 180 else '6개월 이상'} 구간입니다.
            </p>
            """
        else:
            result_text += f"""
            <h3 style='color:green; font-size:16px; line-height:1.4; margin-bottom:5px;'>
            ✅ 검사 개수 조건을 만족합니다. (인식된 검사 기준: {valid_exam_count} / {max_exams})
            </h3>
            <p style='color:blue; font-size:14px; line-height:1.4; margin-bottom:5px;'>
             💡 현재 {days_since}일 경과로 {'6개월 미만' if days_since < 180 else '6개월 이상'} 구간입니다.
            </p>
            """

        return result_text

    except Exception as e:
        return f"<h3 style='color:red; font-size:16px; line-height:1.4;'>❌ 내부 오류 발생: {str(e)}</h3>"

def get_ad_url():
    try:
        response = requests.get(GITHUB_AD_URL, timeout=5)
        ad_url = response.text.strip()
        if not ad_url or "http" not in ad_url:
            return DEFAULT_AD_URL
        return ad_url
    except:
        return DEFAULT_AD_URL
