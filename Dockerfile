FROM python:3.10

COPY requirements.txt /opt/fdrbot/requirements.txt

WORKDIR /opt/fdrbot

RUN pip install -r requirements.txt

COPY . /opt/fdrbot

EXPOSE 8080

CMD ["python", "-OO", "run.py"]

