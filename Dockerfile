FROM python:3.10

COPY requirements.txt /opt/fdrbot/requirements.txt

WORKDIR /opt/fdrbot

RUN pip install -r requirements.txt

COPY . /opt/fdrbot

CMD ["python", "run.py"]
