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
- Screenshot: (Đã kiểm chứng thông qua thao tác PowerShell thành công)

## Part 4: API Security

### Exercise 4.1-4.3: Test results
- Unauthorized (Thiếu Key): API ném về báo lỗi HTTP `401 Unauthorized`. 
- Quá Rate Limit: API ném về thông báo lỗi HTTP `429 Too Many Requests`.

### Exercise 4.4: Cost guard implementation
- Dùng Redis để ghi nợ số tiền của từng `user_id` gán với tháng hiện tại (`YYYY-MM`). 
- Sau mỗi câu trả lời, cộng $0.05 USD vào Key Redis.
- Khi tổng nợ của tài khoản này > $10.0 USD, trả về mã lỗi HTTP `402 Payment Required`.

## Part 5: Scaling & Reliability

### Exercise 5.1-5.5: Implementation notes
- Thiết kế **Stateless**: Tuyệt đối không lưu danh sách hội thoại trong RAM của python app. Tất cả state đẩy ra ngoài trung tâm (Redis Cache) để khi tách nhiều docker containers, chúng chia sẻ chung bộ não bộ nhớ gốc.
- **Graceful Shutdown**: Dùng module `signal` để bắt tín hiệu `signal.SIGTERM` từ Cloud -> Dừng nhận thêm khách, giữ nguyên nguồn điện để xử lý nốt các hàm API cho xong rồi mới tắt.
