# dockerファイル作成のための手順記載、以下流れで打っていくとデバッグできる

## イメージ取得
docker pull python:3.8

## コンテナ起動
docker run -dit --init python:3.8

## execするためのID取得
docker ps

## exec
docker exec -it 3be846feac2e bash