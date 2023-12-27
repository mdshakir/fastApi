# FastAPI Application with Docker

This is a FastAPI application with SQLite database setup.

## Prerequisites
- Docker installed on your machine

## Steps to Replicate Setup

1. **Clone the Repository**
   ```bash
   git clone https://github.com/yourusername/your-fastapi-app.git
   cd your-fastapi-app

   **build the applicaiton Repository**
2. docker build -t your-fastapi-app .

   **Run the application**
3. docker run -p 8000:80 your-fastapi-app

