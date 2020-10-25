FROM python:3.8.6-alpine

RUN apk update
RUN apk upgrade
RUN apk add bash
RUN pip install multiset
COPY ./main.py /project/main.py
COPY ./wordlist /project/wordlist

CMD cd /project && python main.py
