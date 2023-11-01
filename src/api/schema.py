# -*- coding: utf-8 -*-
# @Time : 2023/10/18 11:03
# @Author : ltm
# @Email :
# @Desc :


from typing import List, Optional
from pydantic import BaseModel
from enum import Enum


class Lang(str, Enum):
    en = "en"
    zh = "zh"


class AnalyzeResult(BaseModel):
    entity_type: str
    start: int
    end: int
    score: Optional[float] = 0


class OperatorConf(BaseModel):
    entity_type: str
    operator_name: str
    params: Optional[dict] = None


class AnalyzeModel(BaseModel):
    text: str
    lang: Lang = Lang.zh
    entities: Optional[List[str]] = None
    score_threshold: Optional[float] = 0
    allow_list: Optional[List[str]] = None
    with_anonymize: Optional[bool] = False
    llm_synthesize: Optional[bool] = False
    anonymize_operators: Optional[List[OperatorConf]] = None


class Pattern(BaseModel):
    name: str
    regex: str
    score: Optional[float] = 0.1


class CustomAnalyzeModel(BaseModel):
    entity: str
    deny_list: List[str] = None
    patterns: List[Pattern] = None
    context: Optional[List[str]] = None


class CustomAnalyze(BaseModel):
    text: str
    lang: Lang
    entities: List[CustomAnalyzeModel]
    with_anonymize: Optional[bool] = False
    llm_synthesize: Optional[bool] = False
    anonymize_operators: Optional[List[OperatorConf]] = None
    allow_list: Optional[List[str]] = None


class OpenAIModel(str, Enum):
    gpt3_5_turbo = 'gpt-3.5-turbo'
    gpt4 = 'gpt-4'


class AnonymizeModel(BaseModel):
    text: str
    analyzer_results: List[AnalyzeResult]
    llm_synthesize: Optional[bool] = False
    operators: Optional[List[OperatorConf]] = None
