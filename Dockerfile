FROM python:3.7-rc-alpine

RUN pip3 install --upgrade pip
RUN pip3 install aiogram==2.19

#ADD main/main.py /main/
#ADD main/utils.py /main/
#ADD main/commands.py /main/
#ADD main/secret.py /main/
#ADD main/data.db /main/
#ADD main/db_creation.py /main/
#ADD main/db_filling.py /main/
#
#WORKDIR /main/

EXPOSE 1234
CMD ["python", "main.py"]