FROM python:3.8.2-slim

WORKDIR /code

COPY requirements.txt .

RUN python -m pip install --upgrade pip && pip install -r /code/requirements.txt --no-cache-dir

COPY . .

CMD ["gunicorn", "foodgram.wsgi:application", "--bind", "0:8000" ] 
