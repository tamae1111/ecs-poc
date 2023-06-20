FROM python:3.8

WORKDIR /usr/src/app

# COPY状態の表示
RUN ls

# dockerコンテナにスクリプトの移動
COPY scripts/simple_server/ ./

# COPY状態の表示
RUN ls

RUN pip install -r ./requirements.txt --no-cache-dir

CMD ["python3", "simple_server.py"]