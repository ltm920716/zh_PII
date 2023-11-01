# -*- coding: utf-8 -*-
# @Time : 2023/10/18 10:55
# @Author : ltm
# @Email :
# @Desc :

from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from .view import router


app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(router, prefix="/pii")
