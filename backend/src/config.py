import sys
import os
import boto3
import logging
from concurrent.futures import ThreadPoolExecutor
from boto3.s3.transfer import S3Transfer, TransferConfig
from dotenv import load_dotenv

load_dotenv()

S3_BUCKET = os.environ["BUCKET_NAME"]

s3 = boto3.client('s3', aws_access_key_id=os.environ["ACCESS_KEY"],
                  aws_secret_access_key=os.environ["SECRET_KEY"],
                  region_name=os.environ["REGION_NAME"])
transfer_config = TransferConfig(multipart_threshold=10 * 1024 * 1024, multipart_chunksize=80 * 1024 * 1024)
transfer = S3Transfer(s3, config=transfer_config)
CHUNK_SIZE = 80 * 1024 * 1024  # 80MB
MAX_THREADS = 20

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

executor = ThreadPoolExecutor()
