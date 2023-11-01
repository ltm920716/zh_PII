# -*- coding: utf-8 -*-
# @Time : 2023/10/25 16:39
# @Author : ltm
# @Email :
# @Desc :https://github.com/dongrixinyu/JioNLP/blob/3c0c2558ea91a4e39743d80e778b3f65db9304cb/jionlp/rule/extractor.py

from presidio_analyzer import PatternRecognizer, Pattern, RecognizerResult, EntityRecognizer
import regex as re
from typing import List, Optional
import datetime
import logging

from presidio_analyzer.nlp_engine import NlpArtifacts
logger = logging.getLogger("presidio-analyzer-patch")


class PatchPatternRecognizer(PatternRecognizer):
    def analyze(
        self,
        text: str,
        entities: List[str],
        nlp_artifacts: NlpArtifacts = None,
        regex_flags: int = None,
    ) -> List[RecognizerResult]:
        """
        Analyzes text to detect PII using regular expressions or deny-lists.

        :param text: Text to be analyzed
        :param entities: Entities this recognizer can detect
        :param nlp_artifacts: Output values from the NLP engine
        :param regex_flags:
        :return:
        """
        results = []
        if self.patterns:
            print('here')
            pattern_result = self._analyze_patterns(text, regex_flags)
            results.extend(pattern_result)

        return results

    def _analyze_patterns(
        self, text: str, flags: int = None
    ) -> List[RecognizerResult]:
        """
        Evaluate all patterns in the provided text.

        Including words in the provided deny-list

        :param text: text to analyze
        :param flags: regex flags
        :return: A list of RecognizerResult
        """
        flags = flags if flags else re.DOTALL | re.MULTILINE
        results = []
        text = ''.join(['#', text, '#'])
        for pattern in self.patterns:
            match_start_time = datetime.datetime.now()
            matches = re.finditer(pattern.regex, text, flags=flags)
            match_time = datetime.datetime.now() - match_start_time
            logger.debug(
                "--- match_time[%s]: %s.%s seconds",
                pattern.name,
                match_time.seconds,
                match_time.microseconds,
            )

            for match in matches:
                start, end = match.span()
                current_match = text[start:end]

                # Skip empty results
                if current_match == "":
                    continue

                score = pattern.score

                validation_result = self.validate_result(current_match)
                description = self.build_regex_explanation(
                    self.name, pattern.name, pattern.regex, score, validation_result
                )
                pattern_result = RecognizerResult(
                    entity_type=self.supported_entities[0],
                    start=start-1,
                    end=end-1,
                    score=score,
                    analysis_explanation=description,
                    recognition_metadata={
                        RecognizerResult.RECOGNIZER_NAME_KEY: self.name,
                        RecognizerResult.RECOGNIZER_IDENTIFIER_KEY: self.id,
                    },
                )

                if validation_result is not None:
                    if validation_result:
                        pattern_result.score = EntityRecognizer.MAX_SCORE
                    else:
                        pattern_result.score = EntityRecognizer.MIN_SCORE

                invalidation_result = self.invalidate_result(current_match)
                if invalidation_result is not None and invalidation_result:
                    pattern_result.score = EntityRecognizer.MIN_SCORE

                if pattern_result.score > EntityRecognizer.MIN_SCORE:
                    results.append(pattern_result)

                # Update analysis explanation score following validation or invalidation
                description.score = pattern_result.score

        results = EntityRecognizer.remove_duplicates(results)
        return results


class IDCardRecognizer(PatchPatternRecognizer):
    ID_CARD_PATTERN = r'(?<=[^0-9a-zA-Z])' \
                      r'((1[1-5]|2[1-3]|3[1-7]|4[1-6]|5[0-4]|6[1-5]|71|81|82|91)' \
                      r'(0[0-9]|1[0-9]|2[0-9]|3[0-4]|4[0-3]|5[1-3]|90)' \
                      r'(0[0-9]|1[0-9]|2[0-9]|3[0-9]|4[0-3]|5[1-7]|6[1-4]|7[1-4]|8[1-7])' \
                      r'(18|19|20)\d{2}(0[1-9]|1[0-2])(0[1-9]|[12][0-9]|3[01])' \
                      r'\d{3}[0-9xX])' \
                      r'(?=[^0-9a-zA-Z])'

    ID_CARD_CHECK_PATTERN = r'^(1[1-5]|2[1-3]|3[1-7]|4[1-6]|5[0-4]|6[1-5]|71|81|82|91)' \
                            r'(0[0-9]|1[0-9]|2[0-9]|3[0-4]|4[0-3]|5[1-3]|90)' \
                            r'(0[0-9]|1[0-9]|2[0-9]|3[0-9]|4[0-3]|5[1-7]|6[1-4]|7[1-4]|8[1-7])' \
                            r'(19|20)\d{2}(0[1-9]|1[0-2])(0[1-9]|[12][0-9]|3[01])\d{3}[0-9xX]$'

    PATTERNS = [
        Pattern(
            "IDCard",
            ID_CARD_PATTERN,
            0.5,
        ),
    ]

    CONTEXT = ["身份证号", "身份证"]

    def __init__(
        self,
        patterns: Optional[List[Pattern]] = None,
        context: Optional[List[str]] = None,
        supported_language: str = "zh",
        supported_entity: str = "ID_CARD",
    ):
        patterns = patterns if patterns else self.PATTERNS
        context = context if context else self.CONTEXT
        super().__init__(
            supported_entity=supported_entity,
            patterns=patterns,
            context=context,
            supported_language=supported_language,
        )
        self.id_card_check_pattern = re.compile(self.ID_CARD_CHECK_PATTERN)

    def invalidate_result(self, pattern_text: str) -> bool:
        """
        :param pattern_text: Text detected as pattern by regex
        :return: True if invalidated
        """
        match_flag = self.id_card_check_pattern.match(pattern_text)
        if match_flag is None:
            return True
        else:
            return False
