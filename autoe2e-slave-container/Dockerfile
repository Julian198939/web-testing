FROM selenium/node-chrome:4.18.1-20240224

USER root

ENV BUCKET="e2e-testing-sideex"
ENV SRC_TC_CONF="gs://${BUCKET}/config/config0.json"
ENV CT_ID="0"
ENV DEBUG="0"
ENV PLATFORM="web"
# ENV PAGE="index_page"
ENV GITHUB_REPO="github.com/PChome24h/sqa_web_testing"
ENV STAGE="0"
ENV RUN_BRANCH="main"

# install nodejs
RUN curl -fsSL https://deb.nodesource.com/setup_20.x | bash -

# add gsutil source
RUN echo "deb [signed-by=/usr/share/keyrings/cloud.google.gpg] http://packages.cloud.google.com/apt cloud-sdk main" | tee -a /etc/apt/sources.list.d/google-cloud-sdk.list && \
    curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | sudo apt-key --keyring /usr/share/keyrings/cloud.google.gpg add - && \
    apt-get update -qq && \
    apt-get -y install nodejs google-cloud-cli git && \
    apt-get -y install fonts-ipafont-gothic fonts-wqy-zenhei fonts-thai-tlwg fonts-kacst fonts-freefont-ttf && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# 設定時區
ENV TZ=Asia/Taipei
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# Selenium 環境變數
EXPOSE 5900
ENV SE_EVENT_BUS_PUBLISH_PORT=4442
ENV SE_EVENT_BUS_SUBSCRIBE_PORT=4443

# 工作目錄
COPY ./src /app
COPY ./start.sh /app/
COPY ./env/ /app/
RUN chmod +x /app/start.sh

WORKDIR /app
ENV PATH="${PATH}:/usr/src/app/node_modules/"
CMD ./start.sh
