# -*- coding: utf-8 -*-
"""
Created on Wed Dec 27 11:29:18 2023

@author: 91830
"""

from fastapi.testclient import TestClient
from main import app,create_table
from uuid import uuid4
import sqlite3
import pytest
from unittest.mock import patch
import main

#client = TestClient(app)

@pytest.fixture
def test_db():
    """Creates a test database in memory and clears it after each test."""
    with sqlite3.connect(":memory:") as db:
        create_table(db)
        yield db

@pytest.fixture
def client_with_db(test_db):
    """Creates a FastAPI TestClient with the test database connection."""
    #create_table(test_db)
    client = TestClient(app)
    yield client, test_db
    
    

def test_create_user(monkeypatch,client_with_db):
    client, test_db = client_with_db
    
    with monkeypatch.context() as m:
        m.setattr(main, "get_db_conn", test_db)  
    #client, test_db = client_with_db
    response = client.post("/create_user",json= {"username":"test_users75"})
    assert response.status_code == 200
    assert "username" in response.json()
    assert "user_id" in response.json()
    assert "jwt" in response.json()
    
    

def test_create_user_exists(monkeypatch,client_with_db):
    client, test_db = client_with_db
    with monkeypatch.context() as m:
        m.setattr(main, "get_db_conn", test_db)
    response = client.post("/create_user",json= {"username":"test_users75"})
    assert response.status_code == 400
    assert response.json()["detail"] == "Username already exists"

# @pytest.fixture
# def authorized_client(test_db):
#     client = TestClient(app)
#     with patch("main.get_current_user_authorization", return_value="test_user199"):  # Mock authorization
#         yield client
        
# def test_upload_file_successful(authorized_client, test_db):
#     #file_path = "test_file.txt"  # Replace with a valid text file path
#     file_content = "This is a test file content."   
#     print(authorized_client)
#     response = authorized_client.post("/upload_file", files={"file": ("test_file.txt", file_content)})
#     print(response.content)
#     assert response.status_code == 200
#     assert "file_id" in response.json()
#     assert isinstance(response.json()["file_id"], str)
#     assert "word_counts" in response.json()
#     assert isinstance(response.json()["word_counts"], dict)

def test_upload_file(monkeypatch,client_with_db):
    client, test_db = client_with_db
    # Create a test user
    with monkeypatch.context() as m:
        m.setattr(main, "get_db_conn", test_db)
    user_response = client.post("/create_user", json={"username": "test_user74"})
    assert user_response.status_code == 200
    jwt_token = user_response.json()["jwt"]
    #Upload a text file
    file_content = "This is a test file content."
    response_upload = client.post(
        "/upload_file",
        headers={"token": jwt_token},
        files={"file": ("test_file.txt", file_content)},
    )
    assert response_upload.status_code == 200
    assert "file_id" in response_upload.json()
    

def test_upload_file_unsupported_file_type(monkeypatch,client_with_db):
    client, test_db = client_with_db
    # Create a test user
    with monkeypatch.context() as m:
        m.setattr(main, "get_db_conn", test_db)
    user_response = client.post("/create_user", json={"username": "test_user799"})
    jwt_token = user_response.json()["jwt"]
    assert user_response.status_code == 200
    file_path = "Take Home Assignment.pdf"
    with open(file_path, "rb") as file:
         response_upload = client.post(
        "/upload_file",
        headers={"token": jwt_token},
        files={"file": file},
    )

    assert response_upload.status_code == 415
    assert response_upload.json() == {"detail": "Unsupported Media Type: Only text files are allowed"}
    

def test_upload_file_emppty_file(monkeypatch,client_with_db):
    client, test_db = client_with_db
    # Create a test user
    with monkeypatch.context() as m:
        m.setattr(main, "get_db_conn", test_db)
    user_response = client.post("/create_user", json={"username": "test_user72"})
    assert user_response.status_code == 200
    jwt_token = user_response.json()["jwt"]
    #Upload a text file
    file_content = ""
    response_upload = client.post(
        "/upload_file",
        headers={"token": jwt_token},
        files={"file": ("test_file.txt", file_content)},
    )
    assert response_upload.status_code == 422
    assert response_upload.json() == {"detail": "The uploaded text file contains no data."}
    
    

def test_get_user_stats_successful(monkeypatch,client_with_db):
    # Generate a valid JWT token
    client, test_db = client_with_db
    # Create a test user
    with monkeypatch.context() as m:
        m.setattr(main, "get_db_conn", test_db)
    user_response = client.post("/create_user", json={"username": "test_user71"})
    assert user_response.status_code == 200
    jwt_token = user_response.json()["jwt"]
    #Upload a text file
    file_content = "This is a test file content."
    response_upload = client.post(
        "/upload_file",
        headers={"token": jwt_token},
        files={"file": ("test_file.txt", file_content)},
    )
    assert response_upload.status_code == 200
    assert "file_id" in response_upload.json()

    response = client.get("/get_user_stats", headers={"token": jwt_token})

    assert response.status_code == 200
    assert isinstance(response.json(), dict)  # Assuming user stats are returned as a dictionary
    assert "total_files_uploaded" in response.json()
    assert "total_words" in response.json()

def test_get_user_stats_unsuccessful(monkeypatch,client_with_db):
    # Generate a valid JWT token
    client, test_db = client_with_db
    response = client.get("/get_user_stats", headers={"token": "invalid_token"})
    assert response.status_code == 401
    assert response.json() == {"detail": "Invalid token"}
    
    

    
def test_get_word_count(monkeypatch,client_with_db):
    # Create a test user
    client, test_db = client_with_db
    user_response = client.post("/create_user", json={"username": "test_user80"})
    assert user_response.status_code == 200

    # Upload a test file
    file_content = "This is a test file content."
    files = {"file": ("test_file.txt", file_content)}
    upload_response = client.post("/upload_file", files=files, headers={"token": user_response.json()["jwt"]})
    
    assert upload_response.status_code == 200
    file_id = upload_response.json()["file_id"]

    # Get word count for the uploaded file
    response = client.get(f"/get_count/{file_id}", headers={"token": user_response.json()["jwt"]})
    
    assert response.status_code == 200
    assert isinstance(response.json(), dict)
    

def test_get_word_count_invalid_file(monkeypatch,client_with_db):
    client, test_db = client_with_db
    user_response = client.post("/create_user", json={"username": "test_user85"})
    assert user_response.status_code == 200
    file_id="invalid_file"
    response = client.get(f"/get_count/{file_id}", headers={"token": user_response.json()["jwt"]})
    
    assert  response.status_code == 404
    assert  response.json() == {"detail": "File not found"}
