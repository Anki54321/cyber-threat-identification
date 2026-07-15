FROM python:3.8

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY Requirement.txt .

RUN pip install --upgrade pip setuptools wheel
RUN pip install -r Requirement.txt

COPY . .

EXPOSE 8000
CMD sh -c "python manage.py migrate && python manage.py runserver 0.0.0.0:8000"
