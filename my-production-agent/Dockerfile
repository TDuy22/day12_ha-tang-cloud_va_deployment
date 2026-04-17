# ==================================
# BƯỚC 1: XƯỞNG CHẾ TẠO (Builder Stage)
# Nơi chứa các công cụ máy móc nặng nề để build (C language, compilers..)
# ==================================
FROM python:3.11-slim as builder
WORKDIR /app

COPY requirements.txt .
# Đóng gói tất cả thư viện thành định dạng .whl gọn nhẹ
RUN pip wheel --no-cache-dir --no-deps --wheel-dir /app/wheels -r requirements.txt

# ==================================
# BƯỚC 2: XE KHÁCH GIAO HÀNG (Production Stage)
# Chỉ chứa đúng những gì cần để chạy, vứt bỏ công cụ thừa thãi -> Image siêu nhẹ
# ==================================
FROM python:3.11-slim
WORKDIR /app

# Ưu điểm của Multi-stage: Bưng các file .whl sang, không bê theo rác
COPY --from=builder /app/wheels /wheels
COPY --from=builder /app/requirements.txt .
RUN pip install --no-cache /wheels/*

# Mang code logic của chúng ta vào
COPY app/ ./app/

# Mở cổng mặc định 8000
ENV PORT=8000
EXPOSE 8000

# Khởi động server Uvicorn bằng định dạng chuỗi "app.main:app" siêu chuẩn
CMD uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}
