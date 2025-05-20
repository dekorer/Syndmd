import win32com.client

try:
    hwp = win32com.client.gencache.EnsureDispatch("HWPFrame.HwpObject")
    print("한글 COM 객체 연결 성공")
except Exception as e:
    print("연결 실패:", e)
