# -*- coding: utf-8 -*-
# @Time : 2023/10/18 10:49
# @Author : ltm
# @Email :
# @Desc :

import dotenv
import os

if os.path.exists('.env'):
    dotenv.load_dotenv()

import uvicorn


if __name__ == "__main__":
    # 启动服务
    uvicorn.run(app="src.api:app", host="0.0.0.0", port=8080, log_level="info", reload=True)
