# -*- coding: utf-8 -*-
# @Time : 2023/10/18 10:57
# @Author : ltm
# @Email :
# @Desc :

from loguru import logger
from fastapi import APIRouter
from fastapi.responses import JSONResponse

from .schema import AnonymizeModel, AnalyzeModel, AnalyzeResult, CustomAnalyze
from ..core.presido import pii_engine

import os

router = APIRouter()


def validate_open_key(llm_synthesize=False):
    if llm_synthesize and not os.getenv('OPENAI_API_KEY'):
        raise ValueError('OPENAI_API_KEY not configured, can not use llm_synthesize')


@router.get('/supported_entities/{language}')
def supported_entities(language: str):
    """Return a list of supported entities."""
    try:
        entities_list = pii_engine.get_supported_entities(language)
    except Exception as e:
        msg = f"get_supported_entities {language} catch error: {e}"
        logger.exception(msg)
        return JSONResponse(content={'status': 500, 'msg': msg, 'data': []})

    return JSONResponse(content={'status': 200, 'msg': 'success', 'data': entities_list})


@router.get('/supported_anonymizers')
def supported_anonymizers():
    try:
        operators = pii_engine.get_supported_anonymizers()
    except Exception as e:
        msg = f"get_supported_anonymizers error: {e}"
        logger.exception(msg)
        return JSONResponse(content={'status': 500, 'msg': msg, 'data': []})

    return JSONResponse(content={'status': 200, 'msg': 'success', 'data': operators})


@router.post('/anonymize')
def anonymize(item: AnonymizeModel):
    try:
        validate_open_key(item.llm_synthesize)
        result = pii_engine.anonymize(item.text, item.analyzer_results, item.llm_synthesize, item.operators)
    except Exception as e:
        msg = f"anonymize error: {e}"
        logger.exception(msg)
        return JSONResponse(content={'status': 500, 'msg': msg, 'data': []})

    return JSONResponse(content={'status': 200, 'msg': 'success', 'data': result})


@router.post('/analyze')
def analyze(item: AnalyzeModel):
    result = {"analyze": [], "anonymize": []}
    try:
        validate_open_key(item.llm_synthesize)
        result_analyze = pii_engine.analyze(item.text, item.lang, item.entities, item.score_threshold, item.allow_list)
        if item.with_anonymize:
            analyzer_results = [[AnalyzeResult(entity_type=r['entity_type'], start=r['start'], end=r['end'], score=r['score'])] for r in result_analyze]
            result_anonymize = pii_engine.anonymize(item.text, analyzer_results, item.llm_synthesize, item.anonymize_operators)
            result["anonymize"] = result_anonymize
        result["analyze"] = result_analyze
    except Exception as e:
        msg = f"analyze error: {e}"
        logger.exception(msg)
        return JSONResponse(content={'status': 500, 'msg': msg, 'data': result})

    return JSONResponse(content={'status': 200, 'msg': 'success', 'data': result})


@router.post('/custom_analyze')
def custom_analyze(item: CustomAnalyze):
    result = {"analyze": [], "anonymize": []}
    try:
        validate_open_key(item.llm_synthesize)
        result_analyze = pii_engine.custom_analyze(item.text, item.lang, item.entities, item.allow_list)
        if item.with_anonymize:
            analyzer_results = [[AnalyzeResult(entity_type=r['entity_type'], start=r['start'], end=r['end'], score=r['score'])] for r in result_analyze]
            result_anonymize = pii_engine.anonymize(item.text, analyzer_results, item.llm_synthesize, item.anonymize_operators)
            result["anonymize"] = result_anonymize
        result["analyze"] = result_analyze
    except Exception as e:
        msg = f"analyze error: {e}"
        logger.exception(msg)
        return JSONResponse(content={'status': 500, 'msg': msg, 'data': result})

    return JSONResponse(content={'status': 200, 'msg': 'success', 'data': result})