# Daftar

> **AI-Powered Manufacturing Report Analyzer** -- Upload handwritten manufacturing reports (Foam, Sewing, Packing, Shoes), and get instant data extraction into a structured format.

---

## Key Features

### Manufacturing Report Extraction (OCR to AI)

- **Multi-provider OCR**: Supports Gemini Vision, OpenAI Vision, EasyOCR, and LlamaParse
- **Image preprocessing**: Automatic denoising, binarization, and deskew via OpenCV before OCR
- **Intelligent data extraction**: LLM-based extraction tailored for different manufacturing sections (Foam, Sewing, Packing, Shoes)
- **Real-time progress**: Server-Sent Events (SSE) stream each pipeline step to the UI
- **End-to-end pipeline**: OCR > Extraction > Structured Formatting

### Security & Auth

- **JWT authentication**: Secure login/register with token-based access control
- **Email verification**: Integration for account verification
- **Rate limiting**: Per-user rate limiting via SlowAPI (falls back to per-IP)
- **Daily usage quotas**: Configurable per-user daily limits for uploads and queries

### Monitoring & Observability

- **Prometheus metrics**: Custom application metrics with auto-instrumented endpoints
- **Health endpoint**: `GET /api/health` for uptime monitoring

---

## Architecture

Everything runs via a robust backend (FastAPI) and a modern frontend (React/Vite). Databases (PostgreSQL, Qdrant) and the reverse proxy (Nginx) run inside Docker.

---

## Getting Started

### Prerequisites

| Tool | Version | Purpose |
|------|---------|---------|
| Python | 3.11+ | Backend runtime |
| Node.js | 18+ | Frontend build |
| pnpm | latest | Frontend package manager |
| Docker | 20+ | Database containers |
| uv | latest | Python dependency management (recommended) |

### Development Setup

1. **Configure Environment**

```bash
cd SRC
cp .env.example .env
```
Update API keys and configurations as needed.

2. **Start Everything with One Command**

```bash
bash dev.sh
```

This will start Docker containers for databases and proxy, plus the backend on port `8101` and frontend on port `5877`.

3. **Access the Application**
- **Application (via Nginx)**: `http://localhost:8999`
- **Frontend**: `http://localhost:5877`
- **API Docs**: `http://localhost:8101/docs`

**To stop everything:**
```bash
bash dev-stop.sh
```

---

## System Workflow

### 1. User Registration & Login
```
Register -> Email Verification -> Login -> JWT Token -> Access Protected Routes
```

### 2. Report Analysis Pipeline
```
Upload Image -> Preprocess (OpenCV) -> OCR (Vision AI) -> Extract Data -> Return Structured Output
```

---

## License

See [LICENCE](LICENCE) for details.
