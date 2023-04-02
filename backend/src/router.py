import concurrent.futures
import traceback

from fastapi import APIRouter, Request

from .config import MAX_THREADS, CHUNK_SIZE, s3, logger, S3_BUCKET
from .utils import upload_chunk_to_s3

from boto3.s3.transfer import TransferConfig


router = APIRouter()
config = TransferConfig(multipart_chunksize=CHUNK_SIZE, max_concurrency=MAX_THREADS)


@router.post('/initiate-upload')
async def initiate_upload(filename: str):
    try:
        response = s3.create_multipart_upload(Bucket=S3_BUCKET, Key=filename)
        upload_id = response['UploadId']
        return {'upload_id': upload_id}
    except Exception as e:
        logger.error(f"Failed initiating upload to s3: {e}")
        logger.error(traceback.format_exc())


@router.post('/upload-chunk')
async def upload_chunk(request: Request, filename: str, chunk_number: int, upload_id: str, chunks: int):
    try:
        chunk = await request.body()
        with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_THREADS) as executor:
            futures = [
                executor.submit(upload_chunk_to_s3, chunk, S3_BUCKET, filename, upload_id, i)
                for i in range(chunks)
            ]

        for future in concurrent.futures.as_completed(futures):
            result = future.result()

        return {'chunk_number': chunk_number}
    except Exception as e:
        logger.error(f"Failed uploading chunk to s3: {e}")
        logger.error(traceback.format_exc())


@router.post('/complete-upload')
async def complete_upload(filename: str, upload_id: str):
    try:
        parts = []
        response = s3.list_parts(Bucket=S3_BUCKET, Key=filename, UploadId=upload_id)
        parts.extend(response['Parts'])
        parts = [{'ETag': part['ETag'], 'PartNumber': part['PartNumber']} for part in
                 sorted(parts, key=lambda p: p['PartNumber'])]
        sorted_parts = sorted(parts, key=lambda p: p['PartNumber'])
        multipart_upload = {'Parts': sorted_parts}

        s3.complete_multipart_upload(Bucket=S3_BUCKET, Key=filename, UploadId=upload_id,
                                     MultipartUpload=multipart_upload)

        return {'filename': filename}
    except Exception as e:
        logger.error(f"Failed completing upload to s3: {e}")
        logger.error(traceback.format_exc())
