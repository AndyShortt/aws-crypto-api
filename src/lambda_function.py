# Copyright 2019-2020 Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

from __future__ import print_function
import boto3
import json
import os
from crypto_handler import CryptoHandler
from s3_utils import S3Utils

s3_bucket = os.environ.get("S3_BUCKET")
s3_object_key = os.environ.get("S3_OBJECT_KEY")
key_id_east = os.environ.get("KMS_EAST_CMK")
key_id_west = os.environ.get("KMS_WEST_CMK")
encrypt_decrypt = CryptoHandler(key_id_east, key_id_west)
s3_utility = S3Utils()

def lambda_handler(event, context):
    #print(json.dumps(event))
    
    if event['httpMethod'] == 'PUT':
        return respond(None, encrypt_and_put(json.loads(event['body'])))
        
    elif event['httpMethod'] == 'GET':
        return respond(None, decrypt_and_get(event['queryStringParameters']['Decrypt']))
        
    else:
        return respond(ValueError('Unsupported method "{}"'.format(event['httpMethod'])))
        

def encrypt_and_put(plaintext):
    
    ciphertext = encrypt_decrypt.encrypt(plaintext)
    response = s3_utility.s3_put(ciphertext, s3_bucket, s3_object_key)
    return response


def decrypt_and_get(decrypt):

    ciphertext = s3_utility.s3_get(s3_bucket, s3_object_key)
    
    if decrypt == 'YES' and decrypt is not None:
        plaintext = encrypt_decrypt.decrypt(ciphertext)
        returntext = plaintext
    else:
        returntext = ciphertext
    
    return returntext


def respond(err, res=None):
    return {
        'statusCode': '400' if err else '200',
        'body': err.message if err else json.dumps(res),
        'headers': {
            'Content-Type': 'application/json',
        },
    }

