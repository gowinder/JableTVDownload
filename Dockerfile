FROM python:3.9.5
WORKDIR /usr/src/app/
COPY requirements.txt .
RUN pip install -r requirements.txt -i https://mirrors.cloud.tencent.com/pypi/simple
ENV LANG=C.UTF-8 LC_ALL=C.UTF-8 PYTHONUNBUFFERED=1 TZ=Asia/Shanghai
ENV TZ Asia/Shanghai
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

FROM python:3.9.5
ENV TZ Asia/Shanghai
RUN apt update && apt install tzdata && cp /usr/share/zoneinfo/${TZ} /etc/localtime && echo ${TZ} > /etc/timezone
WORKDIR /usr/src/app/
COPY --from=base /usr/local /usr/local
COPY . /usr/src/app/
VOLUME [ "/usr/src/app/conf", "/usr/src/app/output" ]
CMD bash