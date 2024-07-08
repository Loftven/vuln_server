FROM python:3
WORKDIR /app
LABEL authors="loftven"
COPY requirement.txt /app
RUN pip3 install -r requirement.txt
COPY . .
ENTRYPOINT ["python", "/app/./main.py"]