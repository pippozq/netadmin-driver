FROM python:3-onbuild
COPY requirements.txt /usr/src/app/

RUN echo "StrictHostKeyChecking no" >> /etc/ssh/ssh_config

ENV TZ=Asia/Shanghai
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone


EXPOSE 8080

ENTRYPOINT  python3 main.py -conf=dev

