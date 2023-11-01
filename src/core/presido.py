# -*- coding: utf-8 -*-
# @Time : 2023/10/18 11:22
# @Author : ltm
# @Email :
# @Desc : https://github.com/microsoft/presidio
# https://huggingface.co/spaces/presidio/presidio_demo/tree/main
import json
import os

from presidio_analyzer import AnalyzerEngine, RecognizerRegistry
from presidio_analyzer.nlp_engine import NlpEngineProvider, NlpArtifacts

from presidio_anonymizer import AnonymizerEngine, DeanonymizeEngine
from presidio_anonymizer.entities import RecognizerResult, OperatorConfig, OperatorResult

from .presidio_zh_patch import OptimizeRecognizerRegistry, ZhNlpArtifacts, ZhPatternRecognizer
from .openai_fake_data_generator import create_messages, openai_chat, get_text_token

from .schema_copy import AnalyzeResult, OperatorConf, CustomAnalyzeModel

from typing import List, Optional, Dict

import math
import spacy


configuration = {
    "nlp_engine_name": "spacy",
    "models": [
        {"lang_code": "zh", "model_name": "zh_core_web_sm"},
        {"lang_code": "en", "model_name": "en_core_web_lg"}
    ]
}

USED_TOEKN = get_text_token(str(create_messages('')))

mul_lang_model = "xx_sent_ud_sm"
try:
    nlp = spacy.load(mul_lang_model)
except:
    spacy.cli.download(mul_lang_model)
    nlp = spacy.load(mul_lang_model)


class PresidioEngine:
    def __init__(self):
        lang = ["zh", "en"]
        provider = NlpEngineProvider(nlp_configuration=configuration)
        self.nlp_engine_with_zh = provider.create_engine()

        registry = OptimizeRecognizerRegistry()
        registry.load_predefined_recognizers(nlp_engine=self.nlp_engine_with_zh, languages=lang)

        self.analyzer = AnalyzerEngine(
            registry=registry,
            nlp_engine=self.nlp_engine_with_zh,
            supported_languages=lang
        )

        self.anonymizer = AnonymizerEngine()
        self.deanoymizer = DeanonymizeEngine()

    def get_supported_entities(self, language='zh'):
        """
        get all entities' name the language supported
        Args:
            language:

        Returns:

        """
        # recognizers_list = self.analyzer.get_recognizers(language)
        # names = [o.name for o in recognizers_list]
        entity_list = self.analyzer.get_supported_entities(language)

        return entity_list

    def analyze(self,
                text: str,
                language='zh',
                entities: Optional[List[str]] = None,
                score_threshold: Optional[float] = None,
                allow_list: Optional[List[str]] = None):
        """
        Analyze text by fixed language and entities
        Args:
            text:
            language:
            entities: default is all entities
            score_threshold:
            allow_list:
            deny_list:

        Returns:

        """
        nlp_artifacts = None
        if language == 'zh':
            nlp_artifacts = self.zh_doc_to_nlp_artifact(text, language)
        result = self.analyzer.analyze(text,
                                       language=language,
                                       entities=entities,
                                       score_threshold=score_threshold,
                                       allow_list=allow_list,
                                       nlp_artifacts=nlp_artifacts)
        return [{'entity_type': r.entity_type, 'start': r.start, 'end': r.end, 'score': r.score} for r in result]

    def custom_analyze(self, text: str, lang: str, entities: List[CustomAnalyzeModel], allow_list: List[str]):
        """
        custom detect key-words and pattern
        Args:
            text:
            lang:
            entities: entity name
            allow_list:

        Returns:

        """
        entities_ = []
        new_registry = RecognizerRegistry()
        for custom_entity in entities:
            custom_recognizer = ZhPatternRecognizer(
                supported_entity=custom_entity.entity,
                supported_language=lang,
                deny_list=custom_entity.deny_list,
                patterns=custom_entity.patterns,
                context=custom_entity.context
            )
            # custom_recognizer.analyze(text=text, entities=[entity])
            new_registry.add_recognizer(custom_recognizer)
            entities_.append(custom_entity.entity)
        analyzer = AnalyzerEngine(registry=new_registry, supported_languages=[lang])

        nlp_artifacts = None
        if lang == 'zh':
            nlp_artifacts = self.zh_doc_to_nlp_artifact(text, lang)
        results = analyzer.analyze(text, language=lang, entities=entities_, allow_list=allow_list, nlp_artifacts=nlp_artifacts)

        return [{'entity_type': r.entity_type, 'start': r.start, 'end': r.end, 'score': r.score} for r in results]

    def zh_doc_to_nlp_artifact(self, text: str, language: str) -> NlpArtifacts:
        doc = self.analyzer.nlp_engine.nlp[language](text)
        lemmas = [token for token in doc]
        tokens_indices = [token.idx for token in doc]
        entities = doc.ents

        return ZhNlpArtifacts(
            entities=entities,
            tokens=doc,
            tokens_indices=tokens_indices,
            lemmas=lemmas,
            nlp_engine=self.analyzer.nlp_engine,
            language=language
        )

    def anonymize(self,
                  text: str,
                  analyzer_results: List[AnalyzeResult],
                  llm_synthesize: Optional[bool] = False,
                  operators: Optional[List[OperatorConf]] = None):
        analyzer_results_build = [RecognizerResult(entity_type=r.entity_type, start=r.start, end=r.end, score=r.score)
                                  for r in analyzer_results]

        if llm_synthesize:
            operators_build = {"DEFAULT": OperatorConfig("replace", None)}
        else:
            operators_build = None
            if operators:
                operators_build = {}
                for o in operators:
                    operators_build[o.entity_type] = OperatorConfig(o.operator_name, o.params)

        result = self.anonymizer.anonymize(
            text=text,
            analyzer_results=analyzer_results_build,
            operators=operators_build
        )

        response = json.loads(result.to_json())

        if llm_synthesize:
            splited_text = []
            max_step_len = (4096 - USED_TOEKN - 100) // 2
            doc = nlp(result.text)
            tmp_len = 0
            tmp_text = ''
            for sent in doc.sents:
                current_len = get_text_token(sent.text)
                if tmp_len + current_len < max_step_len:
                    tmp_text += sent.text
                    tmp_len += current_len
                else:
                    if tmp_text:
                        splited_text.append(tmp_text)

                    if current_len > max_step_len:
                        text_step = math.ceil(current_len / math.ceil(current_len / max_step_len))
                        i = 0
                        while text_step*i < current_len:
                            splited_text.append(sent.text[i*text_step: min((i+1)*text_step, current_len-1)])
                            i += 1

                        tmp_text = ''
                        tmp_len = 0
                    else:
                        tmp_text = sent.text
                        tmp_len = current_len
            if tmp_text:
                splited_text.append(tmp_text)

            fake = ''
            for split_text in splited_text:
                messages = create_messages(split_text)
                fake += openai_chat(messages, temperature=0.3)
            response['text'] = fake
            response['items'] = []

        return response

    def deanoymize(self,
                   text: str,
                   entities: List[OperatorResult],
                   operators: Dict[str, OperatorConfig]):
        result = self.deanoymizer.deanonymize(
            text=text,
            entities=entities,
            operators=operators
        )

        return result

    @staticmethod
    def get_supported_anonymizers():
        return ['replace', 'redact', 'hash', 'mask', 'encrypt']


pii_engine = PresidioEngine()
