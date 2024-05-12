FROM ubuntu:latest

RUN apt-get update

ARG DEBIAN_FRONTEND=noninteractive

RUN ln -s /usr/share/zoneinfo/Europe/Moscow /etc/localtime && apt-get install tzdata -y

RUN apt install -yq python3 python3-pip git

ENV TZ="Europe/Moscow"

RUN git clone https://github.com/vahtovik/ANSARA-test-task.git /app

WORKDIR /app
RUN pip install -r requirements.txt

EXPOSE 8000
CMD ["python3", "manage.py", "runserver", "0.0.0.0:8000"]
