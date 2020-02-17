# Copyright 2017-2019 Amazon.com, Inc. or its affiliates. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License"). You
# may not use this file except in compliance with the License. A copy of
# the License is located at
#
# http://aws.amazon.com/apache2.0/
#
# or in the "license" file accompanying this file. This file is
# distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF
# ANY KIND, either express or implied. See the License for the specific
# language governing permissions and limitations under the License.

"""Helper class to handle encryption.
"""

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
