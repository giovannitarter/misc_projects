FROM python:3

RUN pip install paho-mqtt python-telegram-bot

ADD apriporta.py /
ADD config.py /

CMD [ "python", "/apriporta.py" ]

