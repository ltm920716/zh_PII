# -*- coding: utf-8 -*-
# @Time : 2023/10/18 11:03
# @Author : ltm
# @Email :
# @Desc :


from typing import List, Optional
from pydantic import BaseModel


class AnalyzeResult(BaseModel):
    entity_type: str
    start: int
    end: int
    score: Optional[float] = 0


class OperatorConf(BaseModel):
    entity_type: str
    operator_name: str
    params: Optional[dict] = None


class Pattern(BaseModel):
    name: str
    regex: str
    score: Optional[float] = 0.1


class CustomAnalyzeModel(BaseModel):
    entity: str
    deny_list: List[str] = None
    patterns: List[Pattern] = None
    context: Optional[List[str]] = None
