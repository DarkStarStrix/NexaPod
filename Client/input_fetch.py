import boto3
import ipfshttpclient
from urllib.parse import urlparse

def fetch_from_s3(uri: str, dest: str):
    parsed = urlparse(uri)
    bucket = parsed.netloc
    key = parsed.path.lstrip('/')
    s3 = boto3.client('s3')
    s3.download_file(bucket, key, dest)

def fetch_from_ipfs(cid: str, dest: str):
    client = ipfshttpclient.connect()
    client.get(cid, target=dest)
