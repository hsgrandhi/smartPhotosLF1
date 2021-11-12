import json
import boto3
from requests_aws4auth import AWS4Auth
import requests
from elasticsearch import Elasticsearch, RequestsHttpConnection
import time

# To test this function - upload any .jpeg or .png image into the photostoragebucket1 bucket in s3, which triggers the lambda function to be executed

def lambda_handler(event, context):
    # # # # index_photos_debug()
    # get_indices()
    # return 
  
    s3_info = event['Records'][0]['s3']
    bucket = s3_info['bucket']['name']
    key = s3_info['object']['key']
  
    rekognition = boto3.client("rekognition")
    response = rekognition.detect_labels(
        Image={
            "S3Object": {
                "Bucket": bucket,
                "Name": key,
            }
        },
        MaxLabels=10,
        MinConfidence=90,
    )
    labels = []
    for i in range(len(response["Labels"])):
        labels.append(response["Labels"][i]["Name"])
    print(labels)
    timestamp = time.time()
    json_body = {
        "objectKey": key,
        "bucket": bucket,
        "createdTimestamp": timestamp,
        "labels": labels
    }
    index_photos(json_body)


def index_photos(json_body):
    session = boto3.session.Session()
    credentials = session.get_credentials()
    region = 'us-west-2'
    host = "https://search-photos-album-pypi63xmrxee3oxnpftvvc73da.us-west-2.es.amazonaws.com/"
    path = "photoalbum/Photo"
    url = host + path
    service = 'es'
    awsauth = AWS4Auth(credentials.access_key, credentials.secret_key, region, service, session_token=credentials.token)
    headers = {"Content-Type": "application/json"}
    
    r = requests.post(url, auth=awsauth, headers=headers, json=json_body)
    print(r)

def get_custom_labels(bucket, key):
    
    s3_cli = boto3.client("s3")
    object_summary = s3_cli.head_object(
        Bucket=bucket,
        Key=key
        
    )
    print('Custom Labels')
    print('LastModified: {}'.format(object_summary.get('LastModified')))
    print('StorageClass: {}'.format(object_summary.get('StorageClass')))
    print('Metadata: {}'.format(object_summary.get('Metadata')))
    print('ContentLength(KB): {}'.format(object_summary.get('ContentLength')/1024))

def get_indices():
    session = boto3.session.Session()
    credentials = session.get_credentials()
    region = 'us-west-2'
    host = "https://search-photos-album-pypi63xmrxee3oxnpftvvc73da.us-west-2.es.amazonaws.com/"
    # path = "photoalbum/_search?q=labels:cats"
    path = "photoalbum/_search?q=labels:Car"
   
    url = host + path
    #url = "https://search-photos-album-pypi63xmrxee3oxnpftvvc73da.us-west-2.es.amazonaws.com/testphotos/_mapping"
    service = 'es'
    awsauth = AWS4Auth(credentials.access_key, credentials.secret_key, region, service, session_token=credentials.token)
    headers = { "Content-Type": "application/json" }
   
    query_body = {
    "query": {
        "match_all": {}
        },
       "size": "3"
    }
    
    response = requests.get(url, auth=awsauth, headers=headers, data=json.dumps(query_body))
    # print(response.text)
    # print(response.json())
    j = response.json()
    # print(j['hits']['hits'])
    res = j['hits']['hits']
    for r in res:
        print(r['_source'])
    print(res)
    
# def index_photos_debug():
#     timestamp = time.time()
#     key = "image.png"
#     bucket = "testbucket"
#     # labels =['dogs','cats','test']
#     labels =['human']
#     json_body = {
#         "objectKey": key,
#         "bucket": bucket,
#         "createdTimestamp": timestamp,
#         "labels": labels
#     }
#     session = boto3.session.Session()
#     credentials = session.get_credentials()
#     region = 'us-west-2'
#     host = "https://search-photos-album-pypi63xmrxee3oxnpftvvc73da.us-west-2.es.amazonaws.com/"
#     path = "photoalbum/Photo"
#     url = host + path
#     service = 'es'
#     awsauth = AWS4Auth(credentials.access_key, credentials.secret_key, region, service, session_token=credentials.token)
#     headers = {"Content-Type": "application/json"}
    
#     r = requests.post(url, auth=awsauth, headers=headers, json=json_body)
#     print(r)
#     print(r.text)