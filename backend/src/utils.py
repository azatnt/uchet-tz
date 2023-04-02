from .config import s3


def upload_chunk_to_s3(chunk: bytes, bucket: str, filename: str, upload_id: str, chunk_number: int):
    s3.upload_part(
        Body=chunk,
        Bucket=bucket,
        Key=filename,
        UploadId=upload_id,
        PartNumber=chunk_number + 1,
    )
