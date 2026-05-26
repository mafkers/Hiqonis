# Hiqonis Backend API

This is the FastAPI backend API for the Hiqonis platform.

## Structure
Following Domain-Driven Design (DDD) and Clean Architecture:
- `api/`: Presentation layer containing HTTP routes and WebSocket handlers.
- `config/`: Application configuration.
- Shared domain models and core business logic reside in `libs/core`.
- Infrastructure integrations reside in `libs/infrastructure`.
- Shared utilities reside in `libs/common`.
