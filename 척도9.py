
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
    초진일 기준으로 6개월 경과 후 다음 달 1일 (7개월차 시작일)을 계산
    """
    six_months_later = visit_date.replace(day=1) + timedelta(days=31 * 6)
    seven_months_start = six_months_later.replace(day=1) + timedelta(days=31)
    return seven_months_start.replace(day=1)

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
   # ✅ visit_date가 datetime.date인지 확인하고 변환을 건너뛰도록 수정
    if isinstance(visit_date_str, str):
        visit_date = datetime.strptime(visit_date_str, "%Y-%m-%d").date()
    else:
        visit_date = visit_date_str  # 이미 datetime.date이면 그대로 사용
    today = datetime.today().date()
    weeks_since = (today - visit_date).days // 7
    months_since = (today.year - visit_date.year) * 12 + (today.month - visit_date.month)

    seven_months_start = calculate_seven_months_start(visit_date)

    # ✅ 검사 가능 개수 설정
    if today == visit_date:
        max_exams = 12
    elif today < seven_months_start:
        max_exams = 6
    else:
        max_exams = 2

    # ✅ 7개월차 날짜 계산
    seven_months_date = calculate_seven_months_start(visit_date) 

    # ✅ 검사 목록이 비어 있는 경우 처리 (새로운 조건 추가)
    if not selected_exams or len(selected_exams) == 0:
        result_text = "<h3 style='color:red; font-size:16px;'>❌ 입력한 검사가 없습니다.</h3><br>"

    # ✅ 7개월차 안내 메시지 추가
        if months_since < 7:
            result_text += f"<h3 style='color:blue; font-size:16px;'>📅 초진일 ({visit_date}) 기준 7개월차는 {seven_months_date.year}년 {seven_months_date.month}월 {seven_months_date.day}일 입니다.</h3><br>"
        else:
            result_text += f"<h3 style='color:blue; font-size:16px;'>📅 초진일 ({visit_date}) 기준 7개월차를 경과하였습니다.</h3><br>"

        return result_text  # ✅ 검사 목록이 없으면 여기서 결과 반환
    

      
    # ✅ 1️⃣ 입력한 검사 목록 (검사 목록이 있을 때만 실행)
    exam_info_list = []
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
                    f"<span style='color:blue; font-weight:bold; font-size:16px; line-height:1.5;'>{category}({exam_type}): "
                    f"<strong style='color:red;'>{category_count[(category, exam_type)]}</strong> & "
                    f"<strong style='color:red;'>{exam}</strong> 중복되어 불가능합니다.</span>"
                )
            else:
                category_count[(category, exam_type)] = exam

    result_text = f"<h4 style='font-size:16px; line-height:1.5;'>📌 입력한 검사 목록:</h4><p style='font-size:16px; line-height:1.5;'>{', '.join(exam_info_list)}</p><br>"

    # # ✅ 검사 가능 여부 메시지
    if today == visit_date:
        result_text += f"<h3 style='color:green;'>✅ 오늘은 초진일입니다. 최대 12개까지 가능합니다.</h3><br>"
    elif today < seven_months_start:
        result_text += f"<h3 style='color:green;'>✅ {weeks_since}주차입니다. 2주내에 최대 6개 검사가 가능합니다.</h3><br>"
    else:
        result_text += f"<h3 style='color:blue;'>🔹 {months_since}개월차: 7개월차 이후로 매월 최대 2개(3개월간 6개) 가능합니다.</h3><br>"

    
    # ✅ 3️⃣ 중복 검사 여부
    if duplicate_exams:
        result_text += "<h3 style='color:red; font-size:16px; line-height:1.3; margin:0; padding:0;'>❌ 중복된 평가 영역이 있습니다:</h3><br>"
        result_text += "<br>".join(duplicate_exams)
    else:
        result_text += "<h3 style='color:blue; font-size:16px; line-height:1.3; margin:0; padding:0;'>✅ 중복되는 검사가 없습니다.</h3>\n"

     # ✅ 검사 개수 제한 확인
    if len(selected_exams) > max_exams:
        result_text += f"<h3 style='color:red;'>❌ 검사 개수를 초과했습니다! (최대 {max_exams}개)</h3><br>"
    else:
        result_text += f"<h3 style='color:green;'>✅ 검사 개수 조건을 만족합니다. ({len(selected_exams)} / {max_exams})</h3><br>"

    return result_text

    
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



