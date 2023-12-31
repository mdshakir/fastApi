# -*- coding: utf-8 -*-
"""
Created on Sun Dec 24 14:58:24 2023

@author: 91830
"""

# main.py

from typing import Optional, Dict, Union
from fastapi import (
    FastAPI,
    UploadFile,
    Depends,
    HTTPException,
    Request,
    Header,
    Path,
    Form,
)
import uvicorn
import string
import nltk
from nltk.stem import PorterStemmer
from nltk.tokenize import word_tokenize
from collections import Counter
import sqlite3
from uuid import uuid4
import jwt
import json
from model import UserResponse, CreateUser


nltk.download("punkt")
ALLOWED_TEXT_FILE_EXTENSIONS = {".txt"}

SECRET_KEY = "1234"
ALGORITHM = "HS256"


def create_jwt(data: dict) -> str:
    return jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)


def username_exists(username: str, db_conn):
    cursor = db_conn.cursor()
    cursor.execute("SELECT 1 FROM users WHERE username = ?", (username,))
    return cursor.fetchone() is not None


def create_connection():
    connection = sqlite3.connect("fileUpload.db")
    return connection


def clean_db(connection):
    cursor = connection.cursor()
    cursor.execute(
        """
     Drop Table users
     
     """
    )
    cursor.execute(
        """
     Drop Table files
     
     """
    )


def create_table(connection):
    # print("Creating table")
    # connection = create_connection()
    cursor = connection.cursor()
    cursor.execute(
        """
     CREATE TABLE IF NOT EXISTS users (
     id INTEGER PRIMARY KEY AUTOINCREMENT,
     username TEXT NOT NULL,
     user_id TEXT
     )
     """
    )
    cursor.execute(
        """
                 CREATE TABLE IF NOT EXISTS files (
                    file_id TEXT PRIMARY KEY,
                    user_id TEXT,
                    word_count TEXT,
                    total_words INTEGER,
                    FOREIGN KEY (user_id) REFERENCES users(user_id)
                )
            """
    )
    connection.commit()
    # connection.close()


def create_user(user: UserResponse, connection):
    connection.execute(
        "INSERT INTO users (username, user_id) VALUES (?, ?)",
        (user.username, user.user_id),
    )
    connection.commit()
    connection.close()


# conn = sqlite3.connect('users.db')
# cursor = conn.cursor()


def initialize_db():
    global cursor
    cursor = sqlite3.connect("fileUpload.db")


initialize_db()


def get_db_conn(request: Request):
    db = create_connection()
    return db


def get_user_by_username(username: str, connection):
    # connection = create_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT user_id FROM users WHERE username = ?", (username,))
    user_id = cursor.fetchone()
    return user_id[0] if user_id else None


def get_user_stats(user_id: str, db_conn):
    cursor = db_conn.cursor()

    # Get total number of files uploaded by the user
    cursor.execute("SELECT COUNT(*) FROM files WHERE user_id = ?", (user_id,))
    total_files_uploaded = cursor.fetchone()[0]

    # Get total number of words combining all word counts
    cursor.execute("SELECT SUM(total_words) FROM files WHERE user_id = ?", (user_id,))
    total_words = cursor.fetchone()[0] or 0  # Use 0 if there are no files

    return {"total_files_uploaded": total_files_uploaded, "total_words": total_words}


def get_word_count(file_id: str, user_id: str, db_conn):
    cursor = db_conn.cursor()

    cursor.execute("SELECT file_id FROM files WHERE file_id =?", (file_id,))
    result = cursor.fetchone()

    if not result or result[0] != file_id:
        raise HTTPException(status_code=404, detail="File not found")

    cursor.execute(
        "Select file_id FROM files WHERE file_id= ? and user_id=? ", (file_id, user_id,)
    )

    result = cursor.fetchone()

    if not result or result[0] != file_id:
        raise HTTPException(
            status_code=401, detail="You are not authorized to access this file."
        )

    # Get word count for the specified file
    cursor.execute("SELECT word_count FROM files WHERE file_id = ?", (file_id,))
    result = cursor.fetchone()
    if not result:
        raise HTTPException(status_code=404, detail="File not found")
    word_count_json = result[0]
    # Convert word count JSON to a Python dictionary
    word_count_dict = json.loads(word_count_json)

    return word_count_dict


def get_current_user_authorization(token: str = Header(...)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload["sub"]
        return user_id
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")


def save_file_details(
    file_id: str, user_id: str, word_count_dict: dict, total_words: int, connection
):
    # connection = create_connection()
    cursor = connection.cursor()
    cursor.execute(
        "INSERT INTO files (file_id,user_id, word_count, total_words) VALUES (?, ?, ?,?)",
        (file_id, user_id, json.dumps(word_count_dict), total_words),
    )
    connection.commit()


def clean_and_count_words(text: str) -> Dict[str, int]:
    # Tokenize the text
    words = word_tokenize(text)

    # Remove punctuation and convert to lowercase
    words = [
        word.lower().translate(str.maketrans("", "", string.punctuation))
        for word in words
    ]

    # Perform stemming using Porter Stemmer
    stemmer = PorterStemmer()
    words = [stemmer.stem(word) for word in words]

    # Count the occurrences of each word
    word_counts = Counter(words)
    total_words = len(words)
    return word_counts, total_words


app = FastAPI()
db = create_connection()
clean_db(db)
create_table(db)


@app.post("/create_user", response_model=UserResponse)
def createUser(user: CreateUser, db=Depends(get_db_conn)):
    """
    Endpoint to create a new user and generate a JWT.

    Args:
        user (CreateUser): The user details provided in the request.
        db: Database connection dependency.

    Returns:
        UserResponse: The response model containing user details(Username,user_id and JWT.
                                                                 
    This endpoint checks if user already exists if not then returns  the UserResponse.
        """
    if username_exists(user.username, db):
        raise HTTPException(status_code=400, detail="Username already exists")
    user_id = str(uuid4())
    # Create a JSON Web Token
    jwt_payload = {"sub": user_id}
    jwt_token = create_jwt(jwt_payload)
    create_user(
        UserResponse(username=user.username, user_id=user_id, jwt=jwt_token), db
    )
    return UserResponse(username=user.username, user_id=user_id, jwt=jwt_token)


@app.post("/upload_file", response_model=Dict[str, Union[str, int]])
def create_upload_file(
    file: UploadFile,
    user: str = Depends(get_current_user_authorization),
    conn=Depends(get_db_conn),
):
    """
        Endpoint to upload a text file, analyze word count, and save file details.

    Args:
        file (UploadFile): The uploaded file.
        user (str): The user's JWT token obtained from the Authorization header.
        conn: Database connection dependency.

    Returns:
        Dict[str, Union[str, int]]: Response containing file_id and word counts.

    Raises:
        HTTPException: If there are issues with file upload, content type, or file content.
        
        This endpoints validates the jwt and let user upload a text file and validates the extension
        of uploaded file. 
    """
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    if not (
        file.content_type.startswith("text/")
        or any(file.filename.endswith(ext) for ext in ALLOWED_TEXT_FILE_EXTENSIONS)
    ):
        raise HTTPException(
            status_code=415,
            detail="Unsupported Media Type: Only text files are allowed",
        )

    contents = ""
    try:
        contents = file.file.read()
        contents = contents.decode("utf-8")
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="File not found.")
    except PermissionError:
        raise HTTPException(
            status_code=401, detail="You do not have permission to access this file."
        )
    except OSError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except UnicodeDecodeError:
        raise HTTPException(
            status_code=400, detail="Error in decoding the text file contents."
        )

    if len(contents) == 0:
        raise HTTPException(
            status_code=422, detail="The uploaded text file contains no data."
        )

    word_counts, total_words = clean_and_count_words(contents)

    # Generate a unique file ID
    file_id = str(uuid4())

    # Return the response
    response_data = {"file_id": file_id, **word_counts}
    save_file_details(file_id, user, word_counts, total_words, conn)
    print(response_data)
    return response_data


@app.get("/get_user_stats", response_model=dict)
def get_user_stats_endpoint(
    current_user: str = Depends(get_current_user_authorization),
    conn=Depends(get_db_conn),
):
    """
    Endpoint to retrieve statistics for the authenticated user.

    Args:
        current_user (str): The user's JWT token obtained from the Authorization header.
        conn: Database connection dependency.

    Returns:
        dict: User statistics containing the total number of files uploaded and total words.

    Raises:
        HTTPException: If there are issues with user authentication or accessing database.
    """
    if current_user is None:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    user_id = current_user
    user_stats = get_user_stats(user_id, conn)

    return user_stats


@app.get("/get_count/{file_id}", response_model=dict)
def get_word_count_endpoint(
    file_id: str = Path(..., description="File ID"),
    current_user: str = Depends(get_current_user_authorization),
    conn=Depends(get_db_conn),
):
    """
 Endpoint to retrieve word count for a specific file associated with the authenticated user.

    Args:
        file_id (str): The unique identifier for the file.
        current_user (str): The user's JWT token obtained from the Authorization header.
        conn: Database connection dependency.

    Returns:
        dict: Word count for each word in the specified file.

    Raises:
        HTTPException: If the file is not found, the user is not authorized, or other database access issues.
        
 This endpoint verifies the user and check if the file belongs to the authenticated user.
    """
    word_count = get_word_count(file_id, current_user, conn)

    return word_count


if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, log_level="info", reload=True)
