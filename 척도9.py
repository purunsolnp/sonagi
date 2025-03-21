
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import requests
import webbrowser
import pandas as pd

def load_exam_data_from_gsheet(sheet_url):
    try:
        df = pd.read_csv(sheet_url)
        exam_dict = {
            row["검사명"].strip().lower(): (
                row["카테고리"],
                row["레벨"],
                row["검사방식"]
            )
            for _, row in df.iterrows()
        }
        return exam_dict
    except Exception as e:
        print(f"[오류] Google Sheets 불러오기 실패: {e}")
        return {}

# ✅ 여기에 변환된 URL 넣기
GSHEET_URL = "https://docs.google.com/spreadsheets/d/1NUwlaPgSy2Jmc8eBlQ875tgxrwQVYylaB2ys8QSZzVc/export?format=csv&gid=0"
exam_categories = load_exam_data_from_gsheet(GSHEET_URL)
# ✅ GitHub의 광고 URL 파일 (사용자 업데이트 필요 없음)
GITHUB_AD_URL = "https://raw.githubusercontent.com/purunsolnp/sonagi/main/adv_url.txt"

# ✅ 기본 광고 URL (광고 URL이 없을 때 표시할 페이지)
DEFAULT_AD_URL = "https://your-default-page.com"  # 네이버 애드포스트 승인 전 기본 URL





# ✅ 7개월차 시작일 계산 함수
def calculate_seven_months_start(visit_date):
    """
    초진일 기준으로 6개월 후의 1일을 7개월차 시작일로 계산
    """
    seven_months_start = (visit_date + relativedelta(months=6)).replace(day=1)
    return seven_months_start

# ✅ 테스트 (초진일: 2024-09-30)
visit_date_test = datetime.strptime("2024-09-30", "%Y-%m-%d").date()
seven_months_start_test = calculate_seven_months_start(visit_date_test)
seven_months_start_test

def calculate_weeks_since_initial(visit_date):
    """
    초진일이 포함된 주를 1주차로 설정하고, 한 주의 끝을 일요일로 잡아 주차를 계산
    """
    today = datetime.today().date()

    # ✅ 초진일이 포함된 주의 월요일 찾기
    visit_week_start = visit_date - timedelta(days=visit_date.weekday())

    # ✅ 현재 날짜가 몇 주차인지 계산
    week_number = ((today - visit_week_start).days // 7) + 1

    return week_number

def calculate_exam_limit(visit_date, target_date):
    """
    초진일 기준으로 6개월 차까지는 최대 6개 가능,
    7개월 차부터는 매월 2개씩만 가능하도록 계산
    """
    # ✅ 정확한 7개월차 시작일 계산 (6개월 후 + 다음 달 1일)
    seven_months_start = calculate_seven_months_start(visit_date)
    
    # ✅ 초진일부터 target_date까지 몇 개월이 지났는지 계산
    months_since = (target_date.year - visit_date.year) * 12 + (target_date.month - visit_date.month)

    # ✅ 검사 개수 제한 설정 (7개월차 시작일 기준으로 변경)
    if target_date == visit_date:
        max_exams = 12  # 초진일은 12개 가능
    elif target_date < seven_months_start:
        max_exams = 6  # 7개월차 시작일 이전까지는 6개 가능
    else:
        max_exams = 2  # 7개월차 시작일부터는 2개 가능

    return months_since, max_exams

def check_exam_availability(visit_date_str, selected_exams):
    """
    검사 가능 여부를 확인하고 HTML 메시지로 반환
    - visit_date_str: 'YYYY-MM-DD' 형식의 문자열
    - selected_exams: 리스트(str) 형태의 검사 이름들
    """
    try:
        if isinstance(visit_date_str, str):
            visit_date = datetime.strptime(visit_date_str, "%Y-%m-%d").date()
        else:
            visit_date = visit_date_str  # 이미 datetime.date이면 그대로 사용

        today = datetime.today().date()
        months_since = (today.year - visit_date.year) * 12 + (today.month - visit_date.month) + 1
        seven_months_start = calculate_seven_months_start(visit_date)

        # ✅ 검사 가능 개수 설정
        if today == visit_date:
            max_exams = 12
        elif today < seven_months_start:
            max_exams = 6
        else:
            max_exams = 2  # 7개월차 이후

        # ✅ 7개월차 날짜 계산 (항상 출력)
        seven_months_date = calculate_seven_months_start(visit_date)

        # ✅ 1️⃣ 결과 텍스트 시작
        result_text = ""

        # ✅ 7개월차 날짜 항상 출력 (📅 파란색)
        result_text += f"""
        <h3 style='color:blue; font-size:16px; line-height:1.4; margin-bottom:5px;'>
            📅 초진일 ({visit_date}) 기준 7개월차는 {seven_months_date.year}년 {seven_months_date.month}월 1일 입니다.
        </h3>
        """

        # ✅ 2️⃣ 입력한 검사 목록
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

                # ✅ 중복 검사 확인
                if (category, exam_type) in category_count:
                    duplicate_exams.append(
                        f"<p style='color:red; font-size:16px; line-height:1.4; margin-bottom:5px;'>"
                        f"❌ {category}({exam_type}): {category_count[(category, exam_type)]} & {exam} 중복되어 불가능합니다."
                        f"</p>"
                    )
                else:
                    category_count[(category, exam_type)] = exam
            else:
                invalid_exams.append(exam)  # ✅ 인식되지 않은 검사 추가

        result_text += f"""
        <h4 style='font-size:16px; line-height:1.4; margin-bottom:5px;'>📌 입력한 검사 목록:</h4>
        <p style='font-size:16px; line-height:1.4; margin-bottom:10px;'>{', '.join(exam_info_list)}</p>
        """

        # ✅ 3️⃣ 인식하지 못한 검사 목록 표시
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

        # ✅ 4️⃣ 중복 검사 여부
        if duplicate_exams:
            result_text += "<h3 style='color:red; font-size:16px; line-height:1.4; margin-bottom:5px;'>❌ 중복된 평가 영역이 있습니다:</h3>"
            result_text += "".join(duplicate_exams)  # 중복 검사 목록 추가
        else:
            result_text += """
            <h3 style='color:green; font-size:16px; line-height:1.4; margin-bottom:5px;'>
                ✅ 중복되는 검사가 없습니다.
            </h3>
            """

        # ✅ 5️⃣ 검사 개수 제한 메시지 (초과 여부 확인 후 출력)
        valid_exam_count = len(selected_exams)

        if valid_exam_count > max_exams:
            result_text += f"""
            <h3 style='color:red; font-size:16px; line-height:1.4; margin-bottom:5px;'>
                ❌ 검사 개수를 초과했습니다! (최대 {max_exams}개)
            </h3>
            """
        else:
            result_text += f"""
            <h3 style='color:green; font-size:16px; line-height:1.4; margin-bottom:5px;'>
                ✅ 검사 개수 조건을 만족합니다. ({valid_exam_count} / {max_exams})
            </h3>
            """

        return result_text

    except Exception as e:
        return f"<h3 style='color:red; font-size:16px; line-height:1.4;'>❌ 내부 오류 발생: {str(e)}</h3>"

    
# ✅ 광고 URL 불러오기 함수
def get_ad_url():
    try:
        response = requests.get(GITHUB_AD_URL, timeout=5)  # 5초 이내 응답이 없으면 기본 URL 사용
        ad_url = response.text.strip()
        if not ad_url or "http" not in ad_url:  # 광고 URL이 비어있거나 잘못된 경우
            return DEFAULT_AD_URL
        return ad_url
    except:
        return DEFAULT_AD_URL  # 오류 발생 시 기본 URL 반환



