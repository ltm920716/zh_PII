FROM python:3.9-slim

ENV name zh_pii

WORKDIR /app

RUN apt-get update

COPY requirements.txt /app

RUN pip3 install --upgrade pip -i https://mirrors.cloud.tencent.com/pypi/simple && \
    pip3 install -r requirements.txt -i https://mirrors.cloud.tencent.com/pypi/simple && \
    python3 -m spacy download zh_core_web_sm && \
    python3 -m spacy download en_core_web_lg && \
    python3 -m spacy download xx_ent_wiki_sm

COPY . /app/

CMD python3 start_app.py
