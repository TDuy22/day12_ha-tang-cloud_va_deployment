import redis
import time
from fastapi import HTTPException
from .config import settings

# Xin kết nối vào trạm Redis
try:
    r = redis.from_url(settings.redis_url)
except Exception as e:
    print(f"Lỗi khởi tạo Redis: {e}")

def check_rate_limit(user_id: str):
    """Hàm van chặn: Giới hạn số câu hỏi mỗi phút bằng Redis"""
    
    # Lấy mốc thời gian phút hiện tại làm mã định danh ổ khóa
    current_minute = int(time.time() / 60)
    key = f"rate_limit:{user_id}:{current_minute}"
    
    # Ghi nợ: Tăng số lần gọi lên 1 cho user này
    current_count = r.incr(key)
    
    # Cài bom hẹn giờ: Xóa bộ nhớ sau 60 giây để không rác máy dăm bảy năm sau
    if current_count == 1:
        r.expire(key, 60)
        
    # Nếu số lần gọi cao hơn định mức trong file config -> Đóng cổng
    if current_count > settings.rate_limit_per_minute:
        raise HTTPException(
            status_code=429, 
            detail=f"Lỗi 429: Bạn đã hỏi quá {settings.rate_limit_per_minute} lần/phút! Hãy hít thở vài giây nhé."
        )
