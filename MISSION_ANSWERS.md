# Day 12 Lab - Mission Answers

## Part 1: Localhost vs Production

### Exercise 1.1: Anti-patterns found
1. Hardcode mật khẩu trực tiếp trong code (`OPENAI_API_KEY`).
2. Gắn cố định cổng truy cập (`port=8000`) thay vì lấy từ biến môi trường.
3. Không có cơ chế Health Check (Liveness / Readiness probe) để hệ thống biết app còn sống không.
4. Tắt máy đột ngột không có cơ chế Graceful Shutdown.
5. In log thô bằng `print()` thay vì Structured Logging (JSON) và để lộ API Key lọt ra log.

### Exercise 1.3: Comparison table
| Feature | Develop | Production | Why Important? |
|---------|---------|------------|----------------|
| Config  | Hardcode trong file | Đọc từ file `.env` bằng `os.getenv` | Tránh lộ lọt mật khẩu lên Github và dễ thay đổi trên Cloud |
| Health check| Không có | Có endpoints `/health` / `/ready` | Kubernetes/Loadbalancer biết đường route traffic |
| Logging | `print()` thường | Logging có định dạng chuẩn (Structured) | Giúp Monitor hệ thống phân tán hiệu quả |
| Shutdown | Chặt cụt (Force Kill) | Graceful Shutdown (Bắt tín hiệu `SIGTERM`) | Không làm gián đoạn request đang phục vụ dở dang |

## Part 2: Docker

### Exercise 2.1: Dockerfile questions
1. Base image: `python:3.11-slim` (hoặc image nhẹ tương tự)
2. Working directory: `/app`
3. Tại sao COPY requirements.txt trước? Để tận dụng Docker Layer Cache, tránh phải thao tác lại `pip install` vô ích khi chỉ đổi phần logic code.
4. CMD vs ENTRYPOINT khác nhau thế nào? ENTRYPOINT cố định lệnh gốc sẽ thi hành, CMD cung cấp các tham số mặc định cho ENTRYPOINT (nhưng có thể bị người dùng ghi đè từ bên ngoài dễ dàng).

### Exercise 2.3: Image size comparison
- Develop: ~1GB (Phụ thuộc Base Image gốc)
- Production (Multi-stage): Dưới ~150-300MB
- Difference: Vô cùng lớn, nhờ loại bỏ được các file trung gian (Compiler, dev dependencies)

## Part 3: Cloud Deployment

### Exercise 3.1: Railway deployment
- URL: `https://day11aithucchien-production.up.railway.app`
- Screenshot: Xem thư mục `screenshots/`

## Part 4: API Security

### Exercise 4.1-4.3: Test results

**Test 1 — Health Check (không cần xác thực):**
```
> curl https://day11aithucchien-production.up.railway.app/health

{"status":"ok","uptime_seconds":506.5}
```
→ Kết quả: HTTP 200 OK. App đang chạy bình thường.

**Test 2 — Gọi /ask KHÔNG có API Key:**
```
> curl -X POST https://day11aithucchien-production.up.railway.app/ask \
    -H "Content-Type: application/json" \
    -d '{"question":"Hello"}'

HTTP 422 Unprocessable Entity
{"detail":[{"type":"missing","loc":["header","x-api-key"],"msg":"Field required","input":null}]}
```
→ Kết quả: Server từ chối vì thiếu header `X-API-Key`. FastAPI trả về 422 (validation error) do header bắt buộc chưa được cung cấp.

**Test 3 — Gọi /ask với SAI API Key:**
```
> curl -X POST https://day11aithucchien-production.up.railway.app/ask \
    -H "X-API-Key: wrong-key-hacker" \
    -H "Content-Type: application/json" \
    -d '{"question":"Hello"}'

HTTP 401 Unauthorized
{"detail":"Lỗi 401: Sai mật khẩu hoặc chưa có chìa khóa!"}
```
→ Kết quả: Server trả 401 Unauthorized, từ chối truy cập vì key không đúng.

**Test 4 — Gọi /ask với ĐÚNG API Key:**
```
> curl -X POST https://day11aithucchien-production.up.railway.app/ask \
    -H "X-API-Key: <ĐÚNG_KEY>" \
    -H "Content-Type: application/json" \
    -d '{"question":"Hello, ban la ai?"}'

HTTP 200 OK
{"question":"Hello, ban la ai?","answer":"Cảm ơn <user>. Xin chào! Tôi là trợ lý AI... (Bạn đã bị thụt ví đi $0.05)"}
```
→ Kết quả: HTTP 200, nhận được phản hồi từ OpenAI GPT-3.5-turbo và bị trừ $0.05 qua Cost Guard.

**Test 5 — Rate Limiting (gửi liên tục >10 request/phút):**
```
> (Gửi liên tục 11 request trong 1 phút)

Request 1-10: HTTP 200 OK
Request 11:   HTTP 429 Too Many Requests
{"detail":"Lỗi 429: Bạn đã hỏi quá 10 lần/phút! Hãy hít thở vài giây nhé."}
```
→ Kết quả: Sau 10 request, server trả 429 đúng như thiết kế chặn spam.

### Exercise 4.4: Cost guard implementation
- Dùng Redis để ghi nợ số tiền của từng `user_id` gán với tháng hiện tại (`YYYY-MM`).
- Sau mỗi câu trả lời, cộng $0.05 USD vào Key Redis (`budget:<user_id>:<YYYY-MM>`).
- Khi tổng nợ của tài khoản này > $10.0 USD, trả về mã lỗi HTTP `402 Payment Required`.
- Key Redis tự hết hạn sau 32 ngày (đầu tháng sau user được "cấp vốn mới").

**Luồng xử lý trong `cost_guard.py`:**
1. Tính `estimated_cost = 0.05` cho mỗi request.
2. Đọc `current_spent` từ Redis key `budget:{user_id}:{YYYY-MM}`.
3. Nếu `current_spent + estimated_cost > monthly_budget_usd` → raise `HTTPException(402)`.
4. Nếu chưa vượt → `r.incrbyfloat(key, 0.05)` để cập nhật số dư.
5. `r.expire(key, 32 * 24 * 3600)` để tự xóa sau 32 ngày.

## Part 5: Scaling & Reliability

### Exercise 5.1: Health Check & Readiness Check

**Health Check (`/health`):**
- Endpoint đơn giản trả về `{"status": "ok", "uptime_seconds": X}`.
- Cloud platform (Railway/Kubernetes) liên tục gọi endpoint này để xác định app còn sống không.
- Nếu không phản hồi → tự động restart container.

**Readiness Check (`/ready`):**
- Kiểm tra kết nối Redis bằng `r.ping()`.
- Nếu Redis chưa sẵn sàng → trả 503 Service Unavailable.
- Load Balancer sẽ không route traffic vào instance chưa ready.

```
> curl https://day11aithucchien-production.up.railway.app/ready

# Nếu Redis đã kết nối:
{"status":"ready"}

# Nếu Redis chưa sẵn sàng:
HTTP 503: {"detail":"Đang khởi động Database, vui lòng đợi (503 Service Unavailable)"}
```

### Exercise 5.2: Graceful Shutdown

Implement trong `main.py` bằng module `signal`:

```python
def shutdown_handler(signum, frame):
    print("Nhận tín hiệu tắt máy (SIGTERM)...")
    sys.exit(0)
signal.signal(signal.SIGTERM, shutdown_handler)
```

**Tại sao quan trọng?**
- Khi Cloud deploy phiên bản mới (rolling update), nó gửi `SIGTERM` tới container cũ.
- Nếu không bắt tín hiệu → request đang xử lý dở sẽ bị cắt ngang → lỗi cho user.
- Graceful shutdown cho phép hoàn thành các request hiện tại trước khi tắt.

### Exercise 5.3: Stateless Design

- **Nguyên tắc:** Tuyệt đối KHÔNG lưu session/state trong RAM của Python process.
- **Thực hiện:** Mọi dữ liệu tạm (rate limit counter, cost tracking) đều lưu vào Redis.
- **Lợi ích:** Khi scale horizontal (chạy nhiều container), tất cả instance chia sẻ chung bộ nhớ Redis → dữ liệu nhất quán.

```
                    ┌─── Container 1 ───┐
User ──→ LB ──────→│   app (stateless)  │──→ Redis (shared state)
                    ├─── Container 2 ───┤        ↑
                    │   app (stateless)  │────────┘
                    └───────────────────┘
```

### Exercise 5.4: Redis là Single Source of Truth

Các key Redis được sử dụng:
- `rate_limit:{user_id}:{minute}` — Đếm số request/phút (TTL: 60s)
- `budget:{user_id}:{YYYY-MM}` — Tổng chi phí tháng (TTL: 32 ngày)

Khi bất kỳ container nào nhận request, nó đều đọc/ghi cùng một Redis → rate limit và cost guard hoạt động chính xác dù có bao nhiêu instance.

### Exercise 5.5: Multi-stage Docker Build

```dockerfile
# Stage 1: Builder — chứa compiler, build tools
FROM python:3.11-slim as builder
RUN pip wheel ... -r requirements.txt

# Stage 2: Production — chỉ copy .whl files, vứt bỏ rác
FROM python:3.11-slim
COPY --from=builder /app/wheels /wheels
RUN pip install /wheels/*
```

**Kết quả:** Image production chỉ ~150-300MB thay vì ~1GB, tiết kiệm bandwidth và thời gian deploy.
