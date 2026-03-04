# OverlayForge

A free platform for streamers to create and manage custom overlays and widgets for live streams.

## Features

- Login with Twitch and Kick (OAuth)
- Real-time stream events (chat, follows, subs, donations)
- Visual drag & drop overlay editor
- Digital widget marketplace
- Stripe and PayPal payments

## Quick Start

### Prerequisites

- Python 3.10+
- PostgreSQL (or Supabase account)

### Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/your-user/overlayforge.git
   cd overlayforge
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   ```

3. Install dependencies:
   ```bash
   pip install -r backend/requirements.txt
   ```

4. Configure environment variables:
   ```bash
   cp .env.example .env
   # Edit .env with your API keys
   ```

5. Run the development server:
   ```bash
   uvicorn backend.main:app --reload --port 8000
   ```

6. Open http://localhost:8000 in your browser.

## Project Structure

```
├── backend/
│   ├── main.py              # FastAPI entry point
│   ├── config.py            # Environment variables
│   ├── database.py          # Database connection
│   ├── routers/             # API route handlers
│   ├── services/            # External service integrations
│   └── models/              # Data models
├── frontend/
│   ├── templates/           # Jinja2 HTML templates
│   └── static/              # CSS, JS, widgets
├── .env.example             # Environment variable template
├── docker-compose.yml       # Docker configuration
└── README.md
```

## Deployment

### Render.com (Backend)

- Connect your GitHub repository
- Start command: `uvicorn backend.main:app --host 0.0.0.0 --port $PORT`

### Vercel / Netlify (Frontend)

- Static files served from the `frontend/` directory

## License

MIT
