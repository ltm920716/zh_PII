# -*- coding: utf-8 -*-
# @Time : 2023/10/19 10:37
# @Author : ltm
# @Email :
# @Desc :

import dotenv
import os

if os.path.exists('../.env'):
    dotenv.load_dotenv('../.env')

from src.core.presido import pii_engine, AnalyzeResult, OperatorConf, CustomAnalyzeModel


if __name__ == '__main__':
    lang = 'zh'
    supported_entities = pii_engine.get_supported_entities(lang)
    print(supported_entities)

    text = '李雷的电话号码是13122832932'
    # text = "Li Lei's phone number is 13122832932"
    result = pii_engine.analyze(text=text,
                                entities=["PHONE_NUMBER", "PERSON"],
                                language=lang,
                                score_threshold=0.3)
    print(result)

    supported_operaters = pii_engine.get_supported_anonymizers()
    print(supported_operaters)

    analyzer_results = [AnalyzeResult(entity_type="PERSON", start=0, end=2, score=0.2)]
    operators = [OperatorConf(entity_type="PERSON", operator_name="replace", params={"new_value": "韩梅梅"})]
    result = pii_engine.anonymize(text, analyzer_results, False, operators)
    print(result)

    result = pii_engine.anonymize(text, analyzer_results, True, operators)
    print(result)

    custom_entity = [CustomAnalyzeModel(entity='abc', deny_list=['电话', '是'])]
    result = pii_engine.custom_analyze("李雷的电话号码是13122832932", 'zh', custom_entity, [])
    print(result)
