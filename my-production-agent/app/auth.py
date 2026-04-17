from fastapi import Header, HTTPException
from .config import settings

# Hàm lính gác (Dependency)
def verify_api_key(x_api_key: str = Header(..., description="Chìa khoá định danh VIP")):
    # So sánh khóa người ta giơ ra với khóa giấu trong file config
    if x_api_key != settings.agent_api_key:
        raise HTTPException(status_code=401, detail="Lỗi 401: Sai mật khẩu hoặc chưa có chìa khóa!")
    
    # Nếu khóa đúng, trả về id của người dùng (Tạm coi cái mã là định danh luôn)
    return x_api_key
