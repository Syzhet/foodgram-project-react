FROM python:3.8.2-slim

WORKDIR /code

COPY . .

RUN python -m pip install --upgrade pip && pip install -r /code/requirements.txt --no-cache-dir

CMD ["gunicorn", "foodgram.wsgi:application", "--bind", "0:8000" ] 