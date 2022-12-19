FROM python:latest

RUN pip install aiogram==2.19

ADD main.py /bot/
ADD utils.py /bot/
ADD commands.py /bot/
ADD secret.py /bot/
ADD db_filling.py /bot/
ADD db_creation.py /bot/
ADD data.db /bot/

WORKDIR /bot/