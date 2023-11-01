# -*- coding: utf-8 -*-
# @Time : 2023/10/19 18:42
# @Author : ltm
# @Email :
# @Desc :

from presidio_analyzer import RecognizerRegistry, PatternRecognizer, Pattern
from presidio_analyzer.predefined_recognizers import (
    CreditCardRecognizer,
    CryptoRecognizer,
    DateRecognizer,
    EmailRecognizer,
    IbanRecognizer,
    IpRecognizer,
    MedicalLicenseRecognizer,
    NhsRecognizer,
    PhoneRecognizer,
    UrlRecognizer,
    UsBankRecognizer,
    UsLicenseRecognizer,
    UsItinRecognizer,
    UsPassportRecognizer,
    UsSsnRecognizer,
    SgFinRecognizer,
    AuAbnRecognizer,
    AuAcnRecognizer,
    AuTfnRecognizer,
    AuMedicareRecognizer
)

from presidio_analyzer.nlp_engine import NlpEngine, NlpArtifacts

from typing import List, Optional

import regex as re

from .new_recognizer import IDCardRecognizer


class OptimizeRecognizerRegistry(RecognizerRegistry):
    def load_predefined_recognizers(
        self, languages: Optional[List[str]] = None, nlp_engine: NlpEngine = None
    ) -> None:
        """
        Load the existing recognizers into memory.

        :param languages: List of languages for which to load recognizers
        :param nlp_engine: The NLP engine to use.
        :return: None
        """
        if not languages:
            languages = ["en"]

        nlp_recognizer = self._get_nlp_recognizer(nlp_engine)
        recognizers_map = {
            "en": [
                UsBankRecognizer,
                UsLicenseRecognizer,
                UsItinRecognizer,
                UsPassportRecognizer,
                UsSsnRecognizer,
                NhsRecognizer,
                SgFinRecognizer,
                AuAbnRecognizer,
                AuAcnRecognizer,
                AuTfnRecognizer,
                AuMedicareRecognizer,
                PhoneRecognizer
            ],
            "ALL": [
                CreditCardRecognizer,
                CryptoRecognizer,
                DateRecognizer,
                EmailRecognizer,
                IbanRecognizer,
                IpRecognizer,
                MedicalLicenseRecognizer,
                nlp_recognizer,
                UrlRecognizer
            ],
        }
        for lang in languages:
            lang_recognizers = [rc() for rc in recognizers_map.get(lang, [])]
            self.recognizers.extend(lang_recognizers)
            all_recognizers = [
                rc(supported_language=lang) for rc in recognizers_map.get("ALL", [])
            ]
            self.recognizers.extend(all_recognizers)

        if 'zh' in languages:
            phone_recognizer_zh = PhoneRecognizer(supported_language="zh", context=["电话", "号码", "手机"],
                                                  supported_regions=('CN',))
            self.recognizers.append(phone_recognizer_zh)
            self.recognizers.append(IDCardRecognizer())


class ZhNlpArtifacts(NlpArtifacts):
    def set_keywords(
            self, nlp_engine, lemmas: List[str], language: str  # noqa ANN001
    ) -> List[str]:
        """
        Return keywords fpr text.

        Extracts lemmas with certain conditions as keywords.
        """
        if not nlp_engine:
            return []
        keywords = [
            k
            for k in lemmas
            if not k.is_punct
            and not k.is_stop
            and k.pos_ not in ['VERB', 'PRON']
        ]

        # best effort, try even further to break tokens into sub tokens,
        # this can result in reducing false negatives
        keywords = [str(i).lower().split(":") for i in keywords]

        # splitting the list can, if happened, will result in list of lists,
        # we flatten the list
        keywords = [item for sublist in keywords for item in sublist]

        self.lemmas = [str(token) for token in lemmas]
        return keywords


class ZhPatternRecognizer(PatternRecognizer):
    def _deny_list_to_regex(self, deny_list: List[str]) -> Pattern:
        """
        Convert a list of words to a matching regex.

        To be analyzed by the analyze method as any other regex patterns.

        :param deny_list: the list of words to detect
        :return:the regex of the words for detection
        """

        # Escape deny list elements as preparation for regex
        escaped_deny_list = [re.escape(element) for element in deny_list]
        if self.supported_language == 'zh':
            regex = r"(" + "|".join(escaped_deny_list) + r")"
        else:
            regex = r"(?:^|(?<=\W))(" + "|".join(escaped_deny_list) + r")(?:(?=\W)|$)"
        return Pattern(name="deny_list", regex=regex, score=self.deny_list_score)
