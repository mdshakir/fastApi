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

- This API provides endpoints for user registration, file uploads, word count analysis, and user statistics retrieval. In this application, SQLite database is used to store user information. There are four endpoints, and here is a description of each:

1.	**User Registration**
	
-	Endpoint: POST /create_user
	
	Input:

	JSON
	{
  		"username": "your_username"
	}

-	Output:
	
		JSON
		{
  			"username": "your_username",
  			"user_id": "unique_user_id",
  			"jwt": "JWT_token"
		}

This endpoints creates a new user and provides a jwt token which will be used further to access the rest of the endpoints. 


2.	**File Upload**
	```bash

	Endpoint: POST /upload_file

	Authorization: Requires a valid JWT token in the Authorization header.

	Input:

	Multipart form data containing a text file.
	Output:

	JSON
	{
  		"file_id": "unique_file_id",
  		"word1": 10,
  		"word2": 5,
  		"word3": 2,  // ... and so on for each word and its count
	}

3. 	**Get User Statistics**
	```bash

	Endpoint: GET /get_user_stats

	Authorization: Requires a valid JWT token in the Authorization header.

	Output:

	JSON
	{
  		"total_files_uploaded": 5,
  		"total_words": 1000
	}

4.	**Get Word Count for a File**
	```bash

	Endpoint: GET /get_count/{file_id}

	Authorization: Requires a valid JWT token in the Authorization header.

	Output:

	JSON
	{
  	"word1": 10,
  	"word2": 5,
  	"word3": 2,  // ... and so on for each word and its count
	}

## 	Additional Information
-	Dependencies: FastAPI, uvicorn, python-multipart, JWT, SQLite, uuid, nltk
-	Database: SQLite (fileUpload.db)
-	Error Handling: HTTPException for various error scenarios



