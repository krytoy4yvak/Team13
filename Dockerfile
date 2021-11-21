FROM python:3.9-slim-buster
COPY . .
RUN pip3 install -r requirements.txt
ENV FLASK_ENV=production
CMD ["python3", "main.py"]
