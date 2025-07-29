FROM python:3.8

WORKDIR /app

COPY requirements.txt .

RUN pip install -r requirements.txt

ENV FLASK_APP=website.py

COPY . /app

CMD ["python", "website.py"]
