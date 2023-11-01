import openai
import tiktoken

import os

openai.api_key = os.getenv('OPENAI_API_KEY')


def openai_chat(messages: list, model="gpt-3.5-turbo", temperature=0) -> str:
    return openai.ChatCompletion.create(
        model=model,
        messages=messages,
        temperature=temperature
    ).choices[0].message.content


def create_messages(anonymized_text: str) -> list:
    """
    Create the prompt with instructions to GPT-3.

    :param anonymized_text: Text with placeholders instead of PII values, e.g. My name is <PERSON>.
    """

    prompt = f"""Your role is to create synthetic text based on de-identified text with placeholders instead of Personally Identifiable Information (PII).

## Rules:
    1. Only replace the PII placeholders (e.g. ,<PERSON>, <DATE>, <ip_address>) with fake values in the output.
    2. If there are no placeholders, return the source input directly.
    3. Notice: the output text format and language MUST same as the input text!

EXAMPLE:
```
    input: How do I change the limit on my credit card <credit_card_number>?
    output: How do I change the limit on my credit card 2539 3519 2345 1555?
    
    input: 如何更改信用卡<credit_card_number>的限额？
    output: 如何更改信用卡3519-2539-9045-2634的限额？
    
    input: <PERSON>是<ORGANIZATION>的首席科学家。
    output: 王哲是飞鸥集团的首席科学家。
    
    input: Cameroon lives in <LOCATION>.
    output: Cameroon lives in Moscow.
```

Start!

input: {anonymized_text}
output: """

    messages = [{"role": "user", "content": prompt}]

    return messages


# https://tiktoken.aigc2d.com/
def get_text_token(text: str, model='gpt-3.5-turbo'):
    encoder = tiktoken.encoding_for_model(model)
    return len(encoder.encode(text))
