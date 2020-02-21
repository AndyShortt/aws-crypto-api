## AWS API for Client Encryption or Decryption
This basic serverless application hosts an HTTPS API endpoint backed by a lambda function.  This app takes plaintext (PUT) encrypts it using AWS encryption SDK multi-region keys and then stores the ciphertext in an S3 bucket.  The ciphertext can be retrieved (GET) either encrypted or unencrypted (based on HTTP header value).  The purpose of this application is a simple example of multi-key client-side encryption using the AWS Encryption SDK.

Things it does: 
1. Creates an endpoint via Amazon API Gateway
2. Creates an AWS Lambda function to back the API
3. Creates associated infrastructure resources (KMS Keys, S3 bucket, IAM roles)

This application example was referenced during the breakout session "CLIENT-SIDE ENCRYPTION AND THE CLOUD: PATTERNS AND PRACTICES" at the UNC Charlotte 2019 Cybersecurity Symposium.
Speaker information and abstract [here](https://cybersecuritysymposium.uncc.edu/speaker/andrew-shortt) and [here](https://cybersecuritysymposium.uncc.edu/speaker/kenneth-jackson).


## License Summary
This sample code is made available under the MIT-0 license. See the LICENSE file.  
Amazon Employees, see ticket XXXXXXXX for open source approval.


## Deployment
This application uses AWS SAM for build and deployment, making it much faster to create the infrastructure plumbing that we don't care about for the purpose of this app. For information on AWS SAM, visit the [GitHub page](https://github.com/awslabs/serverless-application-model).

0. You will need the SAM CLI & AWS CLI installed and configured. Then you will need to clone this repo.

1. Navigate to the root of the repo folder. Execute the below command to first setup your KMS Key in us-west-2. We have to execute this seperatly because AWS CloudFormation only allows a stack to operate within one region at a time. 

$ aws cloudformation deploy --template-file west_template.yaml --stack-name crypto-api-westkey --region us-west-2

Go ahead and note the KEY ARN that was created using the following command:

$ aws cloudformation describe-stacks --stack-name crypto-api-westkey --region us-west-2

2. Next we are going to build the SAM package, which means it will review our template and populate additional fields, pull in dependencies located in our requirements file, and pull together our source code. All this is uploaded to S3.

$ sam build

The first time you execute the build, it will ask you a few questions to create a .toml configuration file. Going forward it will pickup defaults from this file. You can name the stack anything you want and I recommend you use your normal default aws region.

3. With your west-coast key ARN handy, we are ready to deploy the package using CloudFormation (via SAM). Execute the following command and make sure to replace the "ParameterValue" value with the ARN returned above.
 
$ sam deploy --parameter-overrides ParameterKey=WestKey,ParameterValue=arn:aws:kms:us-west-2:account-id:key/unique-key-id  

It will first do a change analysis to confirm you intended to change the resources. After you confirm, it will deploy the resources via CloudFormation. The output "API" parameter you should take note of, this is your API endpoint.

## Execution

You should be ready to hit the API with some text and then pull it back either unencrypted or encrypted.

1. Replace the url below with the API from your deployment, then execute the below curl command (feel free to change the data being sent over):

$ curl -i --location --request PUT \  
'https://xyz.execute-api.region-code.amazonaws.com/Prod/encryptdecrypt/' \
--data-raw '{"Secret":"Plaintext"}'

This should result in an HTTP/2 200 response (and a bunch of other headers amzn sends back)

2. You can pull your data back encrypted or unencrypted running the below command. Switch the query string parameter between YES/NO to toggle between plaintext and ciphertext response

$ curl -i --location --request GET 'https://xyz.execute-api.region-code.amazonaws.com/Prod/encryptdecrypt?Decrypt=YES'

The result should be the original data you pushed over (Secret:Plaintext)

## TODO

1. Automate the creation of the west-coast KMS key. Should be single step
2. Improve security hygene, such as adding API authentication
3. Enhance app to dynamically switch between regions based on service availability (regional service failure of API GW, Lambda, S3, or KMS)