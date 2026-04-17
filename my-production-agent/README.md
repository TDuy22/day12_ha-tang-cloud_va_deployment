# 🤖 Production Boss Agent

> AI Agent production-ready được deploy trên Railway, trang bị đầy đủ bảo mật, giới hạn chi phí, và thiết kế phi trạng thái.

## 🏗️ Kiến Trúc

```
app/
├── main.py           # FastAPI app + Health Check + Graceful Shutdown
├── config.py         # Pydantic Settings (đọc từ .env)
├── auth.py           # Xác thực API Key (Header X-API-Key)
├── rate_limiter.py   # Giới hạn 10 request/phút (Redis-backed)
└── cost_guard.py     # Giới hạn $10 USD/tháng (Redis-backed)
```

## 🚀 Cài Đặt & Chạy

### 1. Clone và cấu hình

```bash
# Copy file cấu hình mẫu
cp .env.example .env

# Sửa file .env: điền API key thật vào OPENAI_API_KEY và AGENT_API_KEY
```

### 2. Chạy bằng Docker Compose (Khuyến nghị)

```bash
# Khởi động cả Agent + Redis cùng lúc
docker compose up --build

# Truy cập tại: http://localhost:8000
```

### 3. Chạy thủ công (không Docker)

```bash
# Cài dependencies
pip install -r requirements.txt

# Cần có Redis chạy sẵn tại localhost:6379
# Khởi động server
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## 🧪 Test API

```bash
# Health Check
curl http://localhost:8000/health
# → {"status": "ok", "uptime_seconds": 123.4}

# Readiness Check (kiểm tra kết nối Redis)
curl http://localhost:8000/ready
# → {"status": "ready"}

# Gửi câu hỏi (cần API Key)
curl -X POST http://localhost:8000/ask \
  -H "X-API-Key: super-vip-key-123" \
  -H "Content-Type: application/json" \
  -d '{"question": "Hello"}'
```

## 🔒 Các Tính Năng Production

| Tính năng | Mô tả |
|-----------|-------|
| **API Key Auth** | Header `X-API-Key` bắt buộc, trả 401 nếu sai |
| **Rate Limiting** | Tối đa 10 request/phút/user, trả 429 nếu vượt |
| **Cost Guard** | Tối đa $10 USD/tháng/user, trả 402 nếu hết ngân sách |
| **Health Check** | `GET /health` — kiểm tra app sống |
| **Readiness Check** | `GET /ready` — kiểm tra kết nối Redis |
| **Graceful Shutdown** | Bắt `SIGTERM`, xử lý nốt request trước khi tắt |
| **Stateless** | Mọi state lưu Redis, hỗ trợ scale nhiều instance |

## 🌐 Deployment

- **Platform:** Railway
- **URL:** https://day11aithucchien-production.up.railway.app
- **Chi tiết:** Xem [DEPLOYMENT.md](../DEPLOYMENT.md)

## ⚙️ Biến Môi Trường

| Biến | Mô tả | Mặc định |
|------|-------|---------|
| `PORT` | Cổng server | `8000` |
| `REDIS_URL` | URL kết nối Redis | `redis://localhost:6379` |
| `AGENT_API_KEY` | Khóa xác thực API | `default-secret-key` |
| `OPENAI_API_KEY` | API Key OpenAI | *(bắt buộc)* |
| `RATE_LIMIT_PER_MINUTE` | Số request tối đa/phút | `10` |
| `MONTHLY_BUDGET_USD` | Ngân sách tối đa/tháng | `10.0` |
| `LOG_LEVEL` | Mức log | `INFO` |
