# Copyright 2019-2020 Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

import json
import base64
import boto3

s3 = boto3.client('s3')

class S3Utils(object):
    
    def s3_put(self,payload, bucket, object_key):
        response = s3.put_object(Body=payload, Bucket=bucket, Key=object_key)
        return response['ResponseMetadata']['HTTPStatusCode']

    def s3_get(self,bucket, object_key):
        response = s3.get_object(Bucket=bucket, Key=object_key)
        return (json.dumps(response['Body'].read().decode('utf-8')))
    