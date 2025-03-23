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

def calculate_seven_months_start(visit_date):
    return (visit_date + relativedelta(months=6)).replace(day=1)

def calculate_weeks_since_initial(visit_date):
    today = datetime.today().date()
    visit_week_start = visit_date - timedelta(days=visit_date.weekday())
    week_number = ((today - visit_week_start).days // 7) + 1
    return week_number

def calculate_exam_limit(visit_date, target_date):
    seven_months_start = calculate_seven_months_start(visit_date)
    months_since = (target_date.year - visit_date.year) * 12 + (target_date.month - visit_date.month)

    if target_date == visit_date:
        max_exams = 12
    elif target_date < seven_months_start:
        max_exams = 6
    else:
        max_exams = 2

    return months_since, max_exams

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

        months_since = (today.year - visit_date.year) * 12 + (today.month - visit_date.month) + 1
        seven_months_start = calculate_seven_months_start(visit_date)

        if (today - visit_date).days == 0:
            max_exams = 12
        elif today < seven_months_start:
            max_exams = 6
        else:
            max_exams = 2

        seven_months_date = calculate_seven_months_start(visit_date)
        result_text = f"""
        <h3 style='color:blue; font-size:16px; line-height:1.4; margin-bottom:5px;'>
            📅 초진일 ({visit_date}) 기준 7개월차는 {seven_months_date.year}년 {seven_months_date.month}월 1일 입니다.
        </h3>
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
            """
        else:
            result_text += f"""
            <h3 style='color:green; font-size:16px; line-height:1.4; margin-bottom:5px;'>
            ✅ 검사 개수 조건을 만족합니다. (인식된 검사 기준: {valid_exam_count} / {max_exams})
            </h3>
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
