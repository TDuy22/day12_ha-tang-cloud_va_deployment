import redis
import time
from datetime import datetime
from fastapi import HTTPException
from .config import settings

# Kết nối Redis
try:
    r = redis.from_url(settings.redis_url)
except Exception as e:
    print("Redis không khả dụng", e)

def check_budget(user_id: str):
    """
    Trạm thu phí: 
    Giả lập mỗi câu hỏi tốn 0.05$. Cho phép tối đa $10 mỗi tháng.
    """
    estimated_cost = 0.05
    
    # Tạo biến chìa khoá theo Tháng hiện tại, ví dụ: budget:vip_user_1:2026-04
    month_key = datetime.now().strftime("%Y-%m")
    key = f"budget:{user_id}:{month_key}"
    
    # Kéo sổ nợ hiện tại trong bộ nhớ Redis xuống
    current_spent = float(r.get(key) or 0)
    
    # Nếu tiền nợ + tiền tốn câu này > $10 => Tuýt còi chặn ngay!
    if current_spent + estimated_cost > settings.monthly_budget_usd:
        raise HTTPException(
            status_code=402, 
            detail="Lỗi 402 (Payment Required): Bạn đã hết sạch 10 USD tiền Quỹ tháng này."
        )
    
    # Cập nhật số tiền nợ lên Redis
    r.incrbyfloat(key, estimated_cost)
    
    # Set thời hạn hóa đơn chỉ lưu 32 ngày (đầu tháng sau tự mất -> user được cấp vốn mới)
    r.expire(key, 32 * 24 * 3600)
    
    return True
