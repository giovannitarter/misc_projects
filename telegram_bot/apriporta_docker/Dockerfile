FROM python:3

ADD apriporta.py /
ADD config.py /

RUN pip install paho-mqtt python-telegram-bot

CMD [ "python", "/apriporta.py" ]

