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
    months_since = (target_date.year - visit_date.year) * 12 + (target_date.month - visit_date.month) + 1  # 개월 수 계산

    if months_since <= 6:
        max_exams = 6  # 6개월 차까지는 최대 6개 가능
    else:
        max_exams = 2  # ✅ 7개월 차부터는 매월 2개만 가능

    return months_since, max_exams

def check_exam_availability(visit_date, selected_exams):
    """
    검사 가능 여부를 확인하고 HTML 태그를 포함한 결과 반환
    """
    from datetime import datetime  # ✅ datetime 모듈을 명확히 임포트
    today = datetime.today().date()  # ✅ 오늘 날짜를 먼저 정의
    weeks_since = calculate_weeks_since_initial(visit_date)
    months_since, max_exams = calculate_exam_limit(visit_date, today)   # ✅ 오류 수정 완료

    # ✅ 검사 개수 제한 메시지 추가
    if today == visit_date:
        header_text = "<h3 style='color:green;'>✅ 오늘은 초진일입니다. 12개의 검사까지 가능합니다.</h3><br>"
    elif months_since <= 6:
        header_text = f"<h3 style='color:green;'>✅ 오늘은 {weeks_since}주차입니다. 검사 가능합니다. (2주내에 최대 6개까지 가능)</h3><br>"
    else:
        header_text = f"<h3 style='color:blue;'>🔹 {months_since}개월 차: 이번 달 최대 {max_exams}개 가능합니다.(3개월내에 최대 6개까지 가능)</h3><br>"
  
  #  ✅ 검사 개수 초과 여부 확인
    if len(selected_exams) > max_exams:
        header_text += f"<h3 style='color:red;'>❌ 검사 개수를 초과했습니다! (최대 {max_exams}개 가능, 입력된 검사 개수: {len(selected_exams)})</h3><br>"
    else:
        header_text += f"<h3 style='color:green;'>✅ 검사 개수 조건을 만족합니다. (입력된 검사 개수: {len(selected_exams)} / 최대 {max_exams}개 가능)</h3><br>"
        
    # ✅ 검사 목록 HTML 형식으로 추가
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
                    f"<span style='color:blue; font-weight:bold;'>{category}({exam_type}): {category_count[(category, exam_type)]} & {exam} 중복되어 불가능합니다.</span>"
                )
            else:
                category_count[(category, exam_type)] = exam

    # ✅ HTML 형식으로 결과 조합
    result_text = header_text
    result_text += f"<h4>📌 입력한 검사 목록:</h4><p>{', '.join(exam_info_list)}</p><br>"

    if duplicate_exams:
        result_text += "<h3 style='color:red;'>❌ 중복된 평가 영역이 있습니다:</h3><br>"
        result_text += "<br>".join(duplicate_exams)
    else:
        result_text += "<h3 style='color:blue; font-size:18px;'>✅ 중복되는 검사가 없습니다.</h3>\n"

    print("디버깅: 최종 결과 텍스트 출력")  # 🔍 디버깅
    print(result_text)  # 🔍 결과를 터미널에 출력해서 확인

    return result_text



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

if __name__ == "__main__":
    # ✅ Tkinter GUI 실행 코드가 import 시 자동 실행되지 않도록 수정
    root = tk.Tk()
    root.title("검사 일정 확인 프로그램")
    root.geometry("600x500")  # 창 크기 설정

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

    root.mainloop()  # ✅ GUI 실행 (이제 `import` 시 자동 실행되지 않음)

