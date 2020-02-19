## AWS API for Client Encryption or Decryption
opening.

Things it does: 
1. first
2. second

Things it does not do:
- Thing 1
- Thing 2

reference to talk?


## License Summary
This sample code is made available under the MIT-0 license. See the LICENSE file.  
Amazon Employees, see ticket XXXXXXXX for open source approval.


## Deployment
$ aws cloudformation deploy --template-file west_template.yaml --stack-name crypto-api-westkey-2 --region us-west-2  

(note the key ARN that was created)  
$ aws cloudformation describe-stacks --stack-name crypto-api-westkey-2 --region us-west-2

$ sam build  

(override key ARN below with the output from the result above)  
$ sam deploy --parameter-overrides ParameterKey=WestKey,ParameterValue=arn:aws:kms:us-west-2:313021996969:key/e99c0af6-77f3-4079-b706-90386a77d35e  


## Execution



## TODO
