FROM selenium/node-chrome:4.8.1-20230221
USER root
# install nodejs
RUN curl -fsSL https://deb.nodesource.com/setup_18.x | bash -
RUN apt-get update  -qq && \
    apt-get -y install nodejs  python3-pip 
# 設定時區
ENV TZ=Asia/Taipei 
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone
# RUN node --version
# install sideex runner
RUN npm i -g @sideex/runner

# 复制Selenium 環境變數
EXPOSE 5900
ENV SE_EVENT_BUS_PUBLISH_PORT=4442
ENV SE_EVENT_BUS_SUBSCRIBE_PORT=4443

# 工作目錄
COPY ./src /app
COPY ./start.sh /app/
RUN chmod +x /app/start.sh

WORKDIR /app
ENV PATH="${PATH}:/usr/src/app/node_modules/"
CMD  ./start.sh 