# Copyright 2019-2020 Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

import json
import base64
import boto3
import aws_encryption_sdk


class CryptoHandler(object):

    def __init__(self, key_id_east, key_id_west):

        self.master_key_provider = self.construct_multiregion_kms_master_key_provider(key_id_east, key_id_west)
    
    
    def construct_multiregion_kms_master_key_provider(self, key_id_east, key_id_west):

        kms_master_key_provider = aws_encryption_sdk.KMSMasterKeyProvider()
        kms_master_key_provider.add_master_key(key_id_west)
        kms_master_key_provider.add_master_key(key_id_east)
        
        return kms_master_key_provider

    def encrypt(self, data):

        ciphertext, _header = aws_encryption_sdk.encrypt(
         source=json.dumps(data),
         key_provider=self.master_key_provider)
        
        return base64.b64encode(ciphertext).decode("utf-8")
        

    def decrypt(self, data):

        ciphertext = base64.b64decode(data)
        plaintext, header = aws_encryption_sdk.decrypt(
         source=ciphertext,
         key_provider=self.master_key_provider)
        
        return json.loads(plaintext)
