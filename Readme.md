# API Gateway

A lightweight asynchronous API Gateway built with **FastAPI** and **httpx**, designed to proxy requests to multiple backend microservices such as `lobby`, `tracker`, and others.

---

## 🚀 Features

- ✅ Asynchronous proxying with `httpx`
- ✅ Automatic routing based on path keywords (e.g. `/lobby/...`)
- ✅ Minimal and fast, ideal for microservice architectures
- ✅ Supports all HTTP methods (GET, POST, PUT, DELETE, etc.)
- ✅ Hot-reload during development with mounted volume

---

## 🗂️ Project Structure

```
app/
├── main.py           # FastAPI app entry point
├── proxy_router.py   # Request routing and proxy logic
└── services.py       # Microservice configuration
```

---

## ⚙️ Configuration

All service route prefixes are defined in `app/services.py`:

```python
SERVICE_ROUTES = {
    "lobby": "http://lobby_ip:8000",
    "tracker": "http://tracker_ip:8001",
}
```

---

## 🐳 Running with Docker

### Development

```bash
docker-compose up --build
```

- The app runs on [http://localhost:8080](http://localhost:8080)
- Code changes are automatically reloaded (`uvicorn --reload`)
- Mounted volumes ensure instant updates without rebuilding

---

## 📦 Requirements (if running locally without Docker)

```bash
pip install -r requirements.txt
uvicorn app.main:app --reload
```

---

## 🔀 Example Requests

| Request Path                  | Proxies To                           |
|------------------------------|--------------------------------------|
| `GET /lobby/users`           | `http://lobby:8000/lobby/users`      |
| `POST /tracker/logs`         | `http://tracker:8001/tracker/logs`   |

---

## 📌 Planned Features

- [ ] JWT header validation
- [ ] Logging of incoming and outgoing requests
- [ ] Rate limiting per IP/service
- [ ] OpenAPI documentation for gateway config

---

## 📄 License

MIT License
