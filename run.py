import uvicorn
import webbrowser
import threading
import time

def open_browser():
    # Đợi một chút để server khởi động xong
    time.sleep(2)
    # Mở trình duyệt tại Swagger UI
    webbrowser.open("http://localhost:8000/docs")

if __name__ == "__main__":
    # Mở trình duyệt trong một thread riêng để không chặn Uvicorn
    threading.Thread(target=open_browser, daemon=True).start()
    # Khởi động Uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )