# FastAPI Application with Docker

This is a FastAPI application with SQLite database setup.

## Prerequisites
- Docker installed on your machine

## How to install docker on your machine
- [Visit this link to install docker.](https://www.google.com/url?sa=t&rct=j&q=&esrc=s&source=web&cd=&cad=rja&uact=8&ved=2ahUKEwj47_Gi37GDAxXg9zgGHbebBM8QFnoECA4QAQ&url=https%3A%2F%2Fdocs.docker.com%2Fdesktop%2Finstall%2Fwindows-install%2F&usg=AOvVaw0gOH_f-GJONTgQiwOHyibD&opi=89978449)


## Steps to Replicate Setup

1. **Clone the Repository**
   ```bash
   git clone https://github.com/yourusername/your-fastapi-app.git
   cd your-fastapi-app

2.   **build the applicaiton Repository**
     ```bash
     docker build -t your-fastapi-app .

3.   **Run the application**
     ```bash
     docker run -p 8000:80 your-fastapi-app

