FROM ubuntu:latest

RUN apt update && \
    apt install -y python3 python3-pip git && \
    apt clean

RUN git clone https://github.com/vahtovik/ANSARA-test-task.git /app

WORKDIR /app
RUN pip install -r requirements.txt

EXPOSE 8000
CMD ["python3", "manage.py", "runserver", "0.0.0.0:8000"]
