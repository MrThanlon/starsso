FROM registry.stuhome.com/devops/dockerepo/alpine:3.7

COPY . /app
RUN set -xe;\
    sed -i 's/dl-cdn.alpinelinux.org/mirrors.ustc.edu.cn/g' /etc/apk/repositories;\
    apk add openldap-dev nginx gcc python3 python3-dev alpine-sdk --no-cache;\
    cd /app;\
    pip3 install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple;\
    cp /app/nginx.conf /etc/nginx/conf.d/default.conf;\
    mkdir /run/nginx;\
    apk del gcc alpine-sdk openldap-dev python3-dev g++ build-base;

WORKDIR /app
CMD ["/usr/bin/gunicorn", "-c", "file:./gunicorn.conf.py", "starsso:app"]