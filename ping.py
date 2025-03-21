import requests
from datetime import datetime, timedelta

# Render 앱 주소
URL = "https://psytest-checker.onrender.com"  # <- 여기를 실제 주소로 바꿔주세요!

# 현재 KST 시간
kst = datetime.utcnow() + timedelta(hours=9)
hour = kst.hour

if 1 <= hour < 7:
    print(f"[{kst}] 새벽 시간이므로 ping 생략")
else:
    try:
        res = requests.get(URL)
        print(f"[{kst}] Ping 전송 완료: 상태 코드 {res.status_code}")
    except Exception as e:
        print(f"[{kst}] Ping 실패: {e}")