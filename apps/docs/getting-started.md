# 🏁 Getting Started with Hiqonis

Hiqonis is an open-source AI-native platform designed for building state-of-the-art Customer Experience (CX) agents. This guide will walk you through setting up Hiqonis for local development.

## Prerequisites

Ensure you have the following installed on your machine:
- **Node.js** (v20 or higher)
- **pnpm** (v9 or higher)
- **Python** (3.12 or higher)
- **uv** (Python package manager)
- **Docker** and **Docker Compose**

## Quick Start (Local Development)

### 1. Clone the repository

```bash
git clone https://github.com/your-username/hiqonis.git
cd hiqonis
```

### 2. Launch Infrastructure Services

Hiqonis requires PostgreSQL, Redis, MinIO, and LiteLLM to run. Start these services using Docker Compose:

```bash
docker compose up -d
```

### 3. Setup Python Backend

Initialize the virtual environment and install backend dependencies using `uv`:

```bash
# Create venv and install dependencies across the workspace
uv sync
```

Activate the virtual environment:

```bash
source .venv/bin/activate
```

Run the FastAPI development server:

```bash
uv run uvicorn apps.api.main:app --reload --port 8000
```

The API docs will be available at [http://localhost:8000/api/v1/docs](http://localhost:8000/api/v1/docs).

### 4. Setup Frontend Dashboard

Install frontend dependencies and start the Next.js development server:

```bash
# Install dependencies in the monorepo root
pnpm install

# Start Next.js dev server
pnpm --filter web dev
```

The dashboard will be available at [http://localhost:3000](http://localhost:3000).

## 💬 Next Steps

Now that you have Hiqonis running locally, learn how to configure your first AI Agent in the [Architecture Guide](architecture.md).
