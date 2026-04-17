import sys
import os
import signal
import time
import redis
from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel

# Import 4 file bộ phận ta vừa xây
from .config import settings
from .auth import verify_api_key
from .rate_limiter import check_rate_limit
from .cost_guard import check_budget
from openai import OpenAI

# Khởi tạo OpenAI Client
openai_client = OpenAI(api_key=settings.openai_api_key)

def ask_llm(question: str) -> str:
    try:
        response = openai_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Bạn là một trợ lý AI thông minh đến từ VinUniversity. Hãy trả lời ngắn gọn và súc tích."},
                {"role": "user", "content": question}
            ]
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Lỗi gọi OpenAI: {str(e)}"

app = FastAPI(title="Production Boss Agent")
START_TIME = time.time()

# 1. Cơ chế lo hậu sự (Graceful Shutdown)
def shutdown_handler(signum, frame):
    print("Nhận tín hiệu tắt máy (SIGTERM) từ Cloud. Đang ráng xử lý nốt cho khách cuối rồi mới tắt...")
    sys.exit(0)
signal.signal(signal.SIGTERM, shutdown_handler)

# 2. Đầu dò Nhịp tim (Health Check)
@app.get("/health")
def health():
    """Hệ thống Cloud sẽ liên tục gõ cửa link này để xem App có bị sập/treo không"""
    return {
        "status": "ok", 
        "uptime_seconds": round(time.time() - START_TIME, 1)
    }

# 3. Đầu dò Sẵn sàng (Readiness Check)
@app.get("/ready")
def ready():
    """Báo cho Load Balancer biết: Tui đã cắm dây cơ sở dữ liệu Redis xong, hẵng xả khách vào!"""
    try:
        r = redis.from_url(settings.redis_url)
        r.ping()
        return {"status": "ready"}
    except Exception:
        raise HTTPException(503, "Đang khởi động Database, vui lòng đợi (503 Service Unavailable)")

class AskRequest(BaseModel):
    question: str

# 4. Trái tim của Ứng dụng (Lắp ráp 3 lớp phòng ngự)
@app.post("/ask")
def ask(
    req: AskRequest,
    user_id: str = Depends(verify_api_key) # Lớp khiên 1: Nhận dạng
):
    # Lớp khiên 2 và 3 gọi ở đây
    check_rate_limit(user_id)
    check_budget(user_id)
    
    # 5. Thiết kế Phi Trạng Thái (Stateless)
    # Tại đây gọi lên OpenAI thay vì mock.
    llm_response = ask_llm(req.question)
    
    answer = f"Cảm ơn {user_id}. {llm_response} (Bạn đã bị thụt ví đi $0.05)"
    
    return {
        "question": req.question,
        "answer": answer
    }
