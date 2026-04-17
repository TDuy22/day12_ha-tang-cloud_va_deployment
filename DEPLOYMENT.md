# Deployment Information

## Public URL
https://day11aithucchien-production.up.railway.app

## Platform
Railway

## Test Commands

### Health Check (PowerShell)
```powershell
Invoke-RestMethod -Uri "https://day11aithucchien-production.up.railway.app/health"
# Expected Result: {"status": "ok", "uptime_seconds": 245.0}
```

### API Test (with authentication)
```powershell
Invoke-RestMethod -Uri "https://day11aithucchien-production.up.railway.app/ask" -Method Post -ContentType "application/json; charset=utf-8" -Headers @{"X-API-Key"="super-vip-key-123"} -Body '{"question": "Bạn có thu phí tôi không đó?"}'
# Expected Result: Nhận câu trả lời từ bot và thực hiện luồng trừ tiền trong Cost Guard.
```

## Environment Variables Set
- PORT: 8080 (Tự động cấp phát bởi Railway)
- REDIS_URL: (Từ Redis Service đính kèm trên Railway)
- AGENT_API_KEY: super-vip-key-123
- LOG_LEVEL: INFO

## Screenshots
- [Deployment dashboard](./screenshots/dashboard.png)
- [Service running](./screenshots/running.png)
- [Test results](./screenshots/test.png)
