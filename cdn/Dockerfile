FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

EXPOSE 5000

# CMD ["python", "main.py"]
CMD ["uvicorn", "app:app", "--reload", "--port", "5000", "--host", "0.0.0.0"]
