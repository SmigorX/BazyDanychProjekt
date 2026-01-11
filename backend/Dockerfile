FROM python:3.13-slim

WORKDIR /backend

COPY app /backend/app

COPY requirements.txt /backend/requirements.txt

RUN pip install --no-cache-dir -r /backend/requirements.txt

EXPOSE 8000

CMD ["python", "/backend/app/main.py"]

