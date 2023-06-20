import logging


import sys

"""import numpy as np
import cv2
import torchvision
import os
import random
import torch
import boto3
"""


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logger.addHandler(logging.StreamHandler(sys.stdout))

logger.info("logger set")

def main():
    print("hello this is docker")
    print("test 2")
    logger.info("in main")

if __name__ == "__main__":
    main()