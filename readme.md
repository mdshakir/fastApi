# FastAPI Application with Docker

This is a FastAPI application with SQLite database setup.

## Prerequisites
- Docker installed on your machine

## How to install docker on your machine
- [Visit this link to install docker.](https://www.google.com/url?sa=t&rct=j&q=&esrc=s&source=web&cd=&cad=rja&uact=8&ved=2ahUKEwj47_Gi37GDAxXg9zgGHbebBM8QFnoECA4QAQ&url=https%3A%2F%2Fdocs.docker.com%2Fdesktop%2Finstall%2Fwindows-install%2F&usg=AOvVaw0gOH_f-GJONTgQiwOHyibD&opi=89978449)


## Steps to Replicate Setup

1. **Clone the Repository**
   ```bash
   git clone https://github.com/mdshakir/fastApi.git
   cd fastApi

2.   **build the applicaiton Repository**
     ```bash
     docker build -t fastApi .

3.   **Run the application**
     ```bash
     docker run -p 8000:80 fastApi

## About the Application

- This API provides endpoints for user registration, file uploads, word count analysis, and user statistics retrieval. In this application I have used sqlite database to store the user information. In this application there are four endpoints. The description of each endpoints are as follows: 

1.User Registration
	
	Endpoint: POST /create_user

Input:

	JSON
	{
  		"username": "your_username"
	}

Output:

JSON
{
  "username": "your_username",
  "user_id": "unique_user_id",
  "jwt": "JWT_token"
}

This endpoints creates a new user and provides a jwt token which will be used further to access the rest of the endpoints. 




