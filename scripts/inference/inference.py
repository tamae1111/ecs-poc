import logging
import os
import random
import torch
import boto3
import numpy as np
import cv2
import sys
import torchvision

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logger.addHandler(logging.StreamHandler(sys.stdout))

SEED = 46

SOURCE_BUCKET = os.environ["SOURCE_BUCKET"]
MODEL_KEY = os.environ["MODEL_KEY"]
TARGET_DATA_KEY = os.environ["TARGET_DATA_KEY"]

DESTINATION_BUCKET = os.environ["DESTINATION_BUCKET"]
DESTINATION_OBJECKT_DIR = os.environ["DESTINATION_OBJECKT_DIR"]
divice = torch.device('cuda') if torch.cuda.is_available() else torch.device('cpu') 

s3 = boto3.resource("s3")

def fix_seed(seed):
    random.seed(seed)
    np.random.seed(seed)

# 汎用メソッド：S3からデータ取得
def download_data_from_s3(target_key, local_file_path):
    source_bucket = s3.Bucket(SOURCE_BUCKET)

    try:
        source_bucket.download_file(target_key, local_file_path)
    except Exception as e:
        logging.error("Downloading failed.")
        logging.error(e)

# 推定結果の保存
def save_result(result):
    np.save('./result', result)


def load_model(path):
    use_model=torch.load(path)
    return use_model


def upload_result_to_s3():
    destination_bucket = s3.Bucket(DESTINATION_BUCKET)
    model_key = os.path.join(DESTINATION_OBJECKT_DIR, "result.npy")
    try:
        destination_bucket.upload_file("./result.npy", model_key)
    except Exception as e:
        logging.error("Result uploading failed.")
        logging.error(e)


def load_data(inputPath:str):
    img = cv2.imread(inputPath)
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    return img

def getDammyResponse(img:np.ndarray,use_model):
    logger.info('START getProcessedImage')
    logger.info(f'type: {type(img)}')
    logger.info(f'type: {type(use_model)}')
    
    # tensor型への変換
    image_tensor = torchvision.transforms.functional.to_tensor(img)

    with torch.no_grad():
        prediction = use_model([image_tensor.to(divice)]) # ここで予測結果がpredictionに格納される

    return img


def main():
    inputPath = "./input.jpg"
    modelPath = "./model.pt"
    fix_seed(SEED)

    # 判別データのダウンロード
    download_data_from_s3(TARGET_DATA_KEY,inputPath)

    # modelのダウンロード
    download_data_from_s3(MODEL_KEY, modelPath)

    # ローカルからデータを判別形式に変換
    target_data = load_data(inputPath)

    # モデルの生成
    model = load_model(modelPath)

    # 推論処理の実行
    result = getDammyResponse(target_data,model)

    # 結果の保存
    save_result(result)

    # s3への送信
    upload_result_to_s3()


if __name__ == "__main__":
    main()