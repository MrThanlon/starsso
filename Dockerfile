FROM registry.stuhome.com/devops/dockerepo/alpine:3.7

COPY . /app
RUN set -xe;\
    sed -i 's/dl-cdn.alpinelinux.org/mirrors.ustc.edu.cn/g' /etc/apk/repositories;\
    apk update;\
    apk add openldap-dev gcc python3 python3-dev alpine-sdk git nodejs-npm --no-cache;\
    cd /app;\
    pip3 install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple;\
    mkdir /build;\
    cd /build;\
    git clone https://gitlab+deploy-token-5:5wntboMbqQzsyz6Zmp5s@git.uestc.cn/starsso/starsso-fe.git --depth 1;\
    cd starsso-fe;\
    git pull origin staging;\
    npm install --registry=https://registry.npm.taobao.org;\
    npm run build;\
    cp -r dist/* /app/starsso/static/;\
    cd /;\
    rm -rf /build;\
    apk del gcc alpine-sdk python3-dev g++ build-base nodejs-npm git;

WORKDIR /app
CMD ["/usr/bin/gunicorn", "-c", "file:./gunicorn.conf.py", "starsso:app"]