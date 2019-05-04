FROM python:3.7.1

WORKDIR /server

RUN apt-get update
RUN apt-get install -y libav-tools

ADD requirements.txt /server/

RUN pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple/

EXPOSE 80 8000 443

CMD gunicorn server:app --bind 0.0.0.0:8000 --worker-class sanic.worker.GunicornWorker --chdir /server
# CMD tail -f /server/requirements.txt