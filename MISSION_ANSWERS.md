# Day 12 Lab - Mission Answers

> **Student Name:** Mã Vĩnh Lộc  
> **Student ID:** 2A202600975  
> **Date:** 2026-06-12

---

## Part 1: Localhost vs Production

### Exercise 1.1: Anti-patterns found

Đọc `01-localhost-vs-production/develop/app.py`, tìm được 6 vấn đề:

1. **API key hardcode** — `OPENAI_API_KEY = "sk-abc123..."` nằm trực tiếp trong code, ai đọc source đều thấy
2. **Port cố định** — `port=8000` hardcode, không thể thay đổi khi deploy lên platform khác
3. **Debug mode luôn bật** — `debug=True` expose stack trace ra ngoài, lộ thông tin nội bộ
4. **Không có health check** — Platform không biết app còn sống không để restart khi cần
5. **Không xử lý graceful shutdown** — Khi nhận SIGTERM, app chết đột ngột, request đang xử lý bị mất
6. **Logging bằng print()** — Không có structured logging, khó filter và monitor trên cloud

### Exercise 1.3: Comparison table

| Feature | Basic (develop) | Advanced (production) | Tại sao quan trọng? |
|---------|----------------|----------------------|---------------------|
| Config | Hardcode trong code | Từ environment variables | Không lộ secret, thay đổi config không cần redeploy |
| Health check | Không có | `GET /health` + `GET /ready` | Platform tự restart khi app crash, load balancer biết route traffic |
| Logging | `print()` | JSON structured logging | Dễ filter, search, aggregate trên cloud log systems |
| Shutdown | Đột ngột (mất request) | Graceful (SIGTERM handler) | Hoàn thành request đang xử lý trước khi tắt, không mất data |
| Secrets | Hardcode | `.env` + `.gitignore` | Bảo mật, không commit secret lên git |
| Error handling | Không có | Try/catch + 4xx/5xx proper | Client biết lỗi gì xảy ra, dễ debug |

---

## Part 2: Docker

### Exercise 2.1: Dockerfile questions

1. **Base image là gì?** `python:3.11-slim` — phiên bản slim giảm size ~60% so với full image
2. **Working directory là gì?** `/build` (stage builder), `/app` (stage runtime)
3. **Tại sao COPY requirements.txt trước?** Docker layer caching — nếu requirements không đổi, layer pip install được cache lại, rebuild nhanh hơn nhiều
4. **CMD vs ENTRYPOINT khác nhau thế nào?**
   - `ENTRYPOINT`: lệnh cố định, không override được khi `docker run`
   - `CMD`: default command, có thể override — `docker run image python other.py`
   - Dùng cả hai: `ENTRYPOINT ["python"]` + `CMD ["app.py"]` → linh hoạt nhất

### Exercise 2.3: Image size comparison

```
my-agent:develop   ~450 MB   (single stage, full build tools còn trong image)
my-agent:advanced  ~210 MB   (multi-stage, chỉ copy packages đã build, không có gcc/build tools)
Difference: -53%
```

Multi-stage build loại bỏ toàn bộ build dependencies (gcc, libpq-dev) khỏi final image — chỉ giữ lại Python packages đã compile.

---

## Part 3: Cloud Deployment

### Exercise 3.1: Railway / Render deployment

- **Platform:** Railway
- **URL:** https://day12ha-tang-cloudvadeployment-production-14f9.up.railway.app/
- **Screenshot:** [screenshots/railway-dashboard.png](screenshots/railway-dashboard.png)

Test commands:
```bash
curl https://day12ha-tang-cloudvadeployment-production-14f9.up.railway.app/health
# {"status":"ok","version":"1.0.0","environment":"production",...}

curl -X POST https://day12ha-tang-cloudvadeployment-production-14f9.up.railway.app/ask \
  -H "X-API-Key: $AGENT_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"question": "What is deployment?"}'
# {"question":"...","answer":"Deployment là quá trình...","model":"gpt-4o-mini",...}
```

### Exercise 3.2: render.yaml vs railway.toml

| | render.yaml | railway.toml |
|---|---|---|
| Format | YAML (verbose, nhiều options) | TOML (ngắn gọn) |
| Health check | `healthCheckPath: /health` | `healthcheckPath = "/health"` |
| Runtime | Chỉ định `runtime: docker` | Auto-detect từ Dockerfile |
| Env vars | Khai báo trong file luôn | Set qua CLI `railway variables set` |
| Region | Chọn được region cụ thể | Tự động |

---

## Part 4: API Security

### Exercise 4.1: API Key authentication

API key được check tại FastAPI `Security` dependency:
```python
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

def verify_api_key(api_key: str = Security(api_key_header)) -> str:
    if not api_key or api_key != settings.agent_api_key:
        raise HTTPException(401, "Invalid or missing API key")
    return api_key
```

- **Nếu sai key:** trả về `401 Unauthorized`
- **Rotate key:** đổi `AGENT_API_KEY` trong env → redeploy, client cập nhật key mới

### Exercise 4.2-4.3: Test results

```bash
# Không có key → 401
curl http://localhost:8000/ask -X POST -d '{"question":"Hi"}'
# {"detail":"Not authenticated"}  ← 401

# Có key → 200
curl http://localhost:8000/ask -X POST \
  -H "X-API-Key: test-key-123" \
  -H "Content-Type: application/json" \
  -d '{"question":"What is Docker?"}'
# {"question":"...","answer":"Container là...","model":"gpt-4o-mini",...}  ← 200

# Rate limit test (gọi >20 req/min)
# Lần 21+: {"detail":"Rate limit exceeded: 20 req/min"}  ← 429
```

**Rate limiting algorithm:** Sliding window — dùng `collections.deque` lưu timestamps trong 60 giây qua. Mỗi request kiểm tra số lượng timestamps còn trong window.

### Exercise 4.4: Cost guard implementation

```python
# Trong app/main.py — in-memory cost tracking (reset theo ngày)
_daily_cost = 0.0
_cost_reset_day = time.strftime("%Y-%m-%d")

def check_and_record_cost(input_tokens: int, output_tokens: int):
    global _daily_cost, _cost_reset_day
    today = time.strftime("%Y-%m-%d")
    if today != _cost_reset_day:        # reset đầu ngày
        _daily_cost = 0.0
        _cost_reset_day = today
    if _daily_cost >= settings.daily_budget_usd:
        raise HTTPException(503, "Daily budget exhausted. Try tomorrow.")
    # gpt-4o-mini pricing: $0.15/1M input, $0.60/1M output
    cost = (input_tokens / 1_000_000) * 0.15 + (output_tokens / 1_000_000) * 0.60
    _daily_cost += cost
```

Với production Redis, dùng `INCRBYFLOAT` + `EXPIRE` để persist qua nhiều instances.

---

## Part 5: Scaling & Reliability

### Exercise 5.1: Health checks

```python
@app.get("/health")   # Liveness — container còn sống không?
def health():
    return {"status": "ok", "uptime_seconds": round(time.time() - START_TIME, 1)}

@app.get("/ready")    # Readiness — sẵn sàng nhận traffic không?
def ready():
    if not _is_ready:   # False trong khi startup
        raise HTTPException(503, "Not ready")
    return {"ready": True}
```

- **Liveness** → platform restart container nếu fail
- **Readiness** → load balancer không route traffic vào đây nếu fail

### Exercise 5.2: Graceful shutdown

```python
def _handle_signal(signum, _frame):
    logger.info(json.dumps({"event": "signal", "signum": signum}))
    # uvicorn timeout_graceful_shutdown=30 đợi requests hoàn thành

signal.signal(signal.SIGTERM, _handle_signal)

# Trong uvicorn.run():
uvicorn.run(..., timeout_graceful_shutdown=30)
```

Test: gửi request dài → kill process với SIGTERM → request vẫn hoàn thành trong 30s.

### Exercise 5.3: Stateless design

**Anti-pattern** (không dùng):
```python
conversation_history = {}   # mất khi restart, không share giữa instances
```

**Đúng** — state trong Redis:
```python
# Lưu history
r.lpush(f"history:{user_id}", json.dumps(message))
r.expire(f"history:{user_id}", 86400)  # TTL 24h

# Đọc history
history = [json.loads(m) for m in r.lrange(f"history:{user_id}", 0, 19)]
```

Kết quả: 3 instances đều đọc cùng history → scale horizontally được.

### Exercise 5.4: Load balancing

```bash
docker compose up --scale agent=3
```

Output quan sát:
```
agent_1  | INFO: 172.20.0.4:54821 - "POST /ask" 200
agent_2  | INFO: 172.20.0.4:54823 - "POST /ask" 200  
agent_3  | INFO: 172.20.0.4:54825 - "POST /ask" 200
```

Nginx round-robin phân đều traffic. Khi 1 instance die → Nginx retry sang instance khác.

### Exercise 5.5: Test stateless

```bash
python test_stateless.py
# [1] Gửi request lần 1 → agent_1 xử lý → lưu vào Redis
# [2] Kill agent_1 container
# [3] Gửi request lần 2 → agent_2 xử lý → đọc từ Redis → ✅ conversation còn
```

Kết quả: conversation history không mất khi instance die.
