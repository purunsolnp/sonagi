import tkinter as tk
from tkinter import messagebox
from tkcalendar import DateEntry
from datetime import datetime, timedelta
import requests
import webbrowser

# ✅ GitHub의 광고 URL 파일 (사용자 업데이트 필요 없음)
GITHUB_AD_URL = "https://raw.githubusercontent.com/purunsolnp/sonagi/main/adv_url.txt"

# ✅ 기본 광고 URL (광고 URL이 없을 때 표시할 페이지)
DEFAULT_AD_URL = "https://your-default-page.com"  # 네이버 애드포스트 승인 전 기본 URL


# 평가 영역 및 검사 정보 매핑 (최종 88개 검사 포함)
exam_categories = {
    key.lower(): value for key, value in {
    # 우울
        "phq-9": ("우울", "Level 1", "자가"), "ces-d": ("우울", "Level 2", "자가"), "rrs": ("우울", "Level 2", "자가"),
        "bdi": ("우울", "Level 2", "자가"), "gds": ("우울", "Level 2", "자가"), "qids": ("우울", "Level 2", "자가"), 
        "hads": ("기분", "Level 2", "자가"), "ham-d": ("우울", "Level 3", "임상가"), "ids": ("우울", "Level 3", "자가"), 
        "csdd": ("우울", "Level 3", "임상가"), "epds": ("우울", "Level 1", "자가"), "cdi": ("우울", "Level 2", "자가"), 
        "bdrs": ("기분", "Level 3", "임상가"),
        
        # 사회불안
        "sads": ("사회불안", "Level 2", "자가"), "fne": ("사회불안", "Level 2", "자가"), "lsas": ("사회불안", "Level 3", "임상가"),
        
        # 불안 일반
        "stai": ("불안 일반", "Level 2", "자가"), "bai": ("불안 일반", "Level 2", "자가"), "ham-a": ("불안 일반", "Level 3", "임상가"),
        
        # 공황/공포
        "acq": ("공황/공포", "Level 2", "자가"), "appq": ("공황/공포", "Level 2", "자가"), "pdss": ("공황/공포", "Level 3", "자가"),
        
        # 자살위험
        "bhs": ("자살위험", "Level 2", "자가"), "rfl": ("자살위험", "Level 3", "자가"), "c-ssrs": ("자살위험", "Level 4", "임상가"),
        
        # 강박
        "moci": ("강박", "Level 2", "자가"), "pi": ("강박", "Level 2", "자가"), "oci": ("강박", "Level 2", "자가"), "docs": ("강박", "Level 2", "자가"), "ybocs": ("강박", "Level 4", "임상가"),
        
        # 외상
        "lec-5": ("외상", "Level 2", "자가"), "ies": ("외상", "Level 2", "자가"), "pcl-5": ("외상", "Level 2", "자가"), "caps": ("외상", "Level 6", "임상가"),
        
        # ADHD
        "k-asrs": ("ADHD", "Level 2", "자가"), "snap": ("ADHD", "Level 2", "자가"), "k-aars": ("ADHD", "Level 3", "자가"), "diva": ("ADHD", "Level 6", "임상가"), "disc": ("ADHD", "Level 6", "임상가"),
        
        # 신체화
        "phq-15": ("신체", "Level 2", "자가"),
        
        # 스트레스
        "pss": ("스트레스", "Level 1", "자가"), 
        
        # 충동
        "yfas": ("충동", "Level 2", "자가"), "guess": ("충동", "Level 2", "자가"),
        
        # 사고
        "cape-p15": ("사고", "Level 2", "자가"), "bprs": ("사고", "Level 3", "임상가"), "panss": ("사고", "Level 5", "임상가"), "ysq": ("사고", "Level 3", "자가"),
        
        # 행동
        "kprc": ("발달", "Level 3", "자가"), "asr-abcl": ("행동", "Level 3", "자가"), "oasr-oabcl": ("행동", "Level 3", "임상가"), "cbcl": ("행동", "Level 3", "자가"), "basc": ("행동", "Level 3", "자가"), "ysr": ("행동", "Level 3", "자가"),
        
        # 장애
        "whodas": ("장해", "Level 2", "임상가"),
        
        #누락
        "aims": ("기타", "Level 3", "임상가"), "audit": ("물질", "Level 1", "자가"), "apathy scale": ("기분", "Level 2", "자가"), "ciwa-ar": ("물질", "Level 1", "임상가"),
        "dbas": ("수면", "Level 2", "자가"),
        "esrs": ("기타", "Level 3", "임상가"),
        "fft": ("기타", "Level 3", "자가"),
        "hcl-32": ("기분", "Level 2", "자가"),"cbq": ("기분", "Level 3", "자가"),
        "honos": ("장해", "Level 3", "임상가"),
        "ibs": ("발달", "Level 3", "자가"),
        "irls": ("수면", "Level 1", "자가"),
        "mast": ("물질", "Level 2", "자가"),
        "mdq": ("기분", "Level 2", "자가"),
        "nmss": ("전반적 정신문제", "Level 2", "임상가"),"scl-9": ("전반적 정신문제", "Level 3", "자가"),
        "pdq-39": ("장해", "Level 1", "자가"),
        "psqi": ("수면", "Level 2", "자가"),
        "scopa-sleep": ("수면", "Level 1", "자가"),
        "socrates": ("물질", "Level 2", "자가"),
        "staxi": ("분노", "Level 3", "자가"),
        "temperament and atypical behavior scale": ("발달", "Level 3", "자가"),
        "ymrs": ("기분", "Level 3", "임상가"),        
                       
        # 진단 면담
        "scid-5-cv": ("전반적 정신문제", "Level 6", "임상가"), "mini-plus": ("전반적 정신문제", "Level 4", "임상가"),
        
        # 자폐
        "e-clac": ("자폐", "Level 4", "임상가"), "ados": ("자폐", "Level 6", "임상가"), "adi": ("자폐", "Level 6", "임상가"), "scq": ("자폐", "Level 2", "자가"), "cars": ("자폐", "Level 3", "임상가"), 
 }.items()
}


def calculate_weeks_since_initial(visit_date):
    """
    초진일부터 오늘까지 몇 주차인지 계산
    """
    today = datetime.today().date()
    weeks_since = (today - visit_date).days // 7
    return weeks_since

def calculate_six_months_date(visit_date):
    """
    초진일 기준으로 6개월차 시작일(해당 월의 첫째 날)을 계산
    """
    six_months_later = (visit_date.month + 6 - 1) % 12 + 1
    six_months_year = visit_date.year + (1 if visit_date.month + 6 > 12 else 0)
    return datetime(six_months_year, six_months_later, 1).date()

def check_exam_availability(visit_date, selected_exams):
    """
    검사 가능 여부를 확인하고 결과 메시지를 반환
    """
    weeks_since = calculate_weeks_since_initial(visit_date)
    six_months_date = calculate_six_months_date(visit_date)
    today = datetime.today().date()

    # 중복 검사 체크
    category_count = {}
    duplicate_exams = []
    exam_info_list = []  # ✅ 검사 정보 저장 리스트

    for exam in selected_exams:
        info = exam_categories.get(exam.strip().lower())  # ✅ 대소문자 구분 제거
        if info:
            category, level, exam_type = info
            exam_info_list.append(f"{exam}({category}, {level}, {exam_type})")

            # 같은 평가 영역이더라도 '임상가'와 '자가'가 다르면 허용
            if (category, exam_type) in category_count:
                duplicate_exams.append(f"{category}({exam_type}): {category_count[(category, exam_type)]} & {exam}")
            else:
                category_count[(category, exam_type)] = exam  # (평가 영역, 임상가/자가) 조합 저장

    # ✅ 검사 가능 여부 메시지 추가 (검사 개수 제한 안내 포함)
    if today == visit_date:
        header_text = "오늘은 초진일입니다. 12개의 검사까지 가능합니다.\n\n"  # ✅ 초진일 12개 가능 안내 추가
    elif today < six_months_date:
        header_text = f"오늘은 {weeks_since}주차입니다. 검사 가능합니다. (최대 6개까지 가능)\n\n"  # ✅ 6개월 내 6개 가능 안내 추가
    else:
        header_text = f"오늘은 {weeks_since}주차입니다. (6개월차 이후) 매월 2개의 검사만 가능합니다.\n\n"

    # ✅ 기존 검사 목록 유지 (덮어쓰기 방지)
    result_text = header_text  # 검사 가능 여부 메시지를 최상단에 추가
    result_text += f"입력한 검사 목록:\n{', '.join(exam_info_list)}\n\n"  # 검사 목록 추가

    # ✅ 중복 검사 메시지 추가
    if duplicate_exams:
        result_text += "중복된 평가 영역이 있습니다:\n"
        for dup in duplicate_exams:
            result_text += f"{dup} 중복되어 불가능합니다.\n"  # ✅ 중복 검사 메시지 개별 라인 처리

    return result_text  # ✅ 함수 마지막에서 한 번만 return



def submit():
    """
    검사 일정을 확인하는 함수
    """
    visit_date = cal_visit.get_date()
    selected_exams = [exam.strip().lower() for exam in exam_entry.get().split(",") if exam.strip()]
    exam_categories_lower = {key.lower(): value for key, value in exam_categories.items()}  # 모든 키를 소문자로 변환

    for exam in selected_exams:
        if exam in exam_categories_lower:
            pass  # ✅ 현재는 사용되지 않음. 필요하면 이후 로직 추가

    if not selected_exams:
        messagebox.showerror("오류", "검사를 최소 1개 이상 입력해주세요.")
        return

    result_text = check_exam_availability(visit_date, selected_exams)

    # 결과창 초기화
    result_display.config(state=tk.NORMAL)
    result_display.delete(1.0, tk.END)

    # 중복 검사 메시지 파란색 적용
    if "중복된 평가 영역이 있습니다:" in result_text:
        parts = result_text.split("중복된 평가 영역이 있습니다:")
        result_display.insert(tk.END, parts[0])  # 일반 메시지 출력
        result_display.insert(tk.END, "중복된 평가 영역이 있습니다:" + parts[1], "blue_text")  # 파란색 부분 적용

        # 파란색 태그 적용
        result_display.tag_configure("blue_text", foreground="blue")
    else:
        result_display.insert(tk.END, result_text)

    result_display.config(state=tk.DISABLED)
    
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

# ✅ 광고 열기 함수
def open_ad():
    webbrowser.open(get_ad_url())  # 최신 광고 URL 자동 적용

# GUI 설정
root = tk.Tk()
root.title("검사 일정 확인 프로그램")
root.geometry("600x500")  # 창 크기 확대

# 위젯 배치
tk.Label(root, text="초진 날짜를 선택하세요:").pack(pady=5)
cal_visit = DateEntry(root, width=12, background='darkblue', foreground='white', borderwidth=2, date_pattern='yyyy-mm-dd', locale='ko_KR')
cal_visit.pack(pady=5)

tk.Label(root, text="검사할 목록을 입력하세요 (쉼표로 구분):").pack(pady=5)
exam_entry = tk.Entry(root, width=60)
exam_entry.pack(pady=5)

tk.Button(root, text="검사 일정 확인", command=submit).pack(pady=10)

# ✅ 광고 버튼 추가
ad_banner = tk.Button(root, text="📢 광고 보기 (수익 지원)", command=open_ad, fg="blue", cursor="hand2")
ad_banner.pack(pady=5)

# 결과창 크기 및 폰트 조정
result_display = tk.Text(root, height=10, width=70, font=("Arial", 12))
result_display.pack(pady=10)
result_display.config(state=tk.DISABLED)  # 결과창 수정 불가능하도록 설정

# 제작자 명시
footer = tk.Label(root, text="소나기 제작", font=("Helvetica", 12, "bold"))
footer.pack(side=tk.BOTTOM, pady=10)

# GUI 실행
root.mainloop()