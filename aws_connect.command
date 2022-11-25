 #! /bin/bash

echo 'enter public address: '
read ip_address
ssh -i /Users/username/Desktop/quant\ learning/aws_key.pem ec2-user@$ip_address