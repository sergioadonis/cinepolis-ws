FROM python:3.9-slim

ENV PYTHONUNBUFFERED 1

WORKDIR /usr/src

RUN pip install --upgrade pip

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN python manage.py collectstatic --no-input

# CMD [ "python", "manage.py", "runserver", "0.0.0.0:8000" ]