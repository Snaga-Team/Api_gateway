FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -U pip && pip install --no-cache-dir -r requirements.txt

COPY app /app/app

EXPOSE 8000
ENV PYTHONUNBUFFERED=1

# В разработке удобно с --reload (перезагрузка при изменениях в ./app благодаря volume)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]