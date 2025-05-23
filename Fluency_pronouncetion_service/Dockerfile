FROM python:3.9

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY app/ app/
COPY models/ models/

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "7000"]
