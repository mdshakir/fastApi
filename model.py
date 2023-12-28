# -*- coding: utf-8 -*-
"""
Created on Thu Dec 28 14:10:15 2023

@author: 91830
"""
from pydantic import BaseModel


class CreateUser(BaseModel):
 username: str

class UserResponse(BaseModel):
    username: str
    user_id: str
    jwt: str