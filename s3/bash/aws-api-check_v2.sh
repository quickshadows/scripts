#!/bin/bash

# Установите переменную для конечного URL
ENDPOINT_URL="https://s3-ceph-dev.timeweb.net"

aws s3api create-bucket --bucket aws-cli-test --region ru-1 --endpoint-url $ENDPOINT_URL

echo "This is a test file." > test_file.txt
aws s3api put-object --bucket 50c17271-multipart --key test_file.txt --body test_file.txt --endpoint-url $ENDPOINT_URL

#fail
#aws s3api put-bucket-notification --bucket 50c17271-aws-cli-2 --notification-configuration '{"TopicConfigurations":[{"TopicArn":"arn:aws:sns:ru-1:123456789012:my-sns-topic","Events":["s3:ObjectCreated:*"]}]}' --endpoint-url $ENDPOINT_URL

#fail
#aws s3api put-bucket-notification-configuration --bucket 50c17271-aws-cli-2 --notification-configuration '{"TopicConfigurations":[{"TopicArn":"arn:aws:sns:ru-1:123456789012:my-sns-topic","Events":["s3:ObjectCreated:*"]}]}' --endpoint-url $ENDPOINT_URL

aws s3api put-bucket-versioning --bucket 50c17271-aws-cli-2 --versioning-configuration '{"Status":"Enabled"}' --endpoint-url $ENDPOINT_URL

aws s3api put-bucket-acl --bucket 50c17271-aws-cli-2 --acl public-read --endpoint-url $ENDPOINT_URL

aws s3api put-bucket-cors --bucket 50c17271-aws-cli-2 --cors-configuration '{"CORSRules":[{"AllowedMethods":["GET","POST"],"AllowedOrigins":["*"],"MaxAgeSeconds":3000}]}' --endpoint-url $ENDPOINT_URL

aws s3api put-bucket-lifecycle-configuration --bucket 50c17271-aws-cli-2 --lifecycle-configuration '{"Rules":[{"ID":"ExpireOldVersions","Prefix":"","Status":"Enabled","Expiration":{"Days":30}}]}' --endpoint-url $ENDPOINT_URL

#fail
#aws s3api put-bucket-replication --bucket 50c17271-aws-cli-2 --replication-configuration '{"Role":"arn:aws:iam::123456789012:role/my-replication-role","Rules":[{"Status":"Enabled","Priority":1,"Prefix":"","Destination":{"Bucket":"arn:aws:s3:::my-destination-bucket"}}]}' --endpoint-url $ENDPOINT_URL

aws s3api put-bucket-tagging --bucket 50c17271-aws-cli-2 --tagging '{"TagSet":[{"Key":"Environment","Value":"Test"},{"Key":"Project","Value":"S3Demo"}]}' --endpoint-url $ENDPOINT_URL

aws s3api put-bucket-encryption --bucket 50c17271-aws-cli-2 --server-side-encryption-configuration '{"Rules":[{"ApplyServerSideEncryptionByDefault":{"SSEAlgorithm":"AES256"}}]}' --endpoint-url $ENDPOINT_URL

aws s3api put-object-tagging --bucket 50c17271-aws-cli-2 --key test_file.txt --tagging '{"TagSet":[{"Key":"FileType","Value":"Text"}]}' --endpoint-url $ENDPOINT_URL

#fail
#aws s3api put-bucket-accelerate-configuration --bucket 50c17271-aws-cli-2 --accelerate-configuration '{"Status":"Enabled"}' --endpoint-url $ENDPOINT_URL

#aws s3api put-bucket-analytics-configuration --bucket 50c17271-aws-cli-2 --analytics-configuration '{"Id":"my-analytics-id","Filter":{"Prefix":"my-prefix"},"StorageClassAnalysis":{"DataExport":{"OutputSchema":"S3BatchOperations_CSV_20180820","Destination":{"S3BucketDestination":{"Format":"S3BatchOperations_CSV_20180820","BucketArn":"arn:aws:s3:::50c17271-aws-cli-2","BucketAccountId":"123456789012"}}}}}' --endpoint-url $ENDPOINT_URL

aws s3api put-bucket-cors --bucket 50c17271-aws-cli-2 --cors-configuration '{"CORSRules":[{"AllowedMethods":["GET","POST"],"AllowedOrigins":["*"],"MaxAgeSeconds":3000}]}' --endpoint-url $ENDPOINT_URL

aws s3api put-bucket-encryption --bucket 50c17271-aws-cli-2 --server-side-encryption-configuration '{"Rules":[{"ApplyServerSideEncryptionByDefault":{"SSEAlgorithm":"AES256"}}]}' --endpoint-url $ENDPOINT_URL

#fail
#aws s3api put-bucket-intelligent-tiering-configuration --bucket 50c17271-aws-cli-2 --intelligent-tiering-configuration '{"Id":"my-configuration-id","Status":"Enabled","Tierings":[{"Days":30,"Tier":"ARCHIVE"}]}' --endpoint-url $ENDPOINT_URL

#fail
#aws s3api put-bucket-inventory-configuration --bucket 50c17271-aws-cli-2 --id my-inventory-id --inventory-configuration '{"Destination":{"S3BucketDestination":{"BucketArn":"arn:aws:s3:::50c17271-aws-cli-2","Format":"CSV","AccountId":"123456789012"}},"IsEnabled":true,"Schedule":{"Frequency":"Daily"}}' --endpoint-url $ENDPOINT_URL

aws s3api put-bucket-lifecycle --bucket 50c17271-aws-cli-2 --lifecycle-configuration '{"Rules":[{"ID":"my-rule-id","Prefix":"my-prefix","Status":"Enabled","Expiration":{"Days":30}}]}' --endpoint-url $ENDPOINT_URL

aws s3api put-bucket-lifecycle-configuration --bucket 50c17271-aws-cli-2 --lifecycle-configuration '{"Rules":[{"ID":"my-rule-id","Prefix":"my-prefix","Status":"Enabled","Expiration":{"Days":30}}]}' --endpoint-url $ENDPOINT_URL

# fail NoneType
#aws s3api put-bucket-logging --bucket 50c17271-aws-cli-2 --bucket-logging-status '{"LoggingEnabled":{"TargetBucket":"my-log-bucket","TargetPrefix":"logs/"}}' --endpoint-url $ENDPOINT_URL

# fail
#aws s3api put-bucket-metrics-configuration --bucket 50c17271-aws-cli-2 --metrics-configuration '{"Id":"my-metrics-id","Filter":{"Prefix":"my-prefix"}}' --endpoint-url $ENDPOINT_URL

#aws s3api put-bucket-notification --bucket 50c17271-aws-cli-2 --notification-configuration '{"TopicConfigurations":[{"TopicArn":"arn:aws:sns:ru-1:123456789012:my-sns-topic","Events":["s3:ObjectCreated:*"]}]}' --endpoint-url $ENDPOINT_URL

#aws s3api put-bucket-notification-configuration --bucket 50c17271-aws-cli-2 --notification-configuration '{"TopicConfigurations":[{"TopicArn":"arn:aws:sns:ru-1:123456789012:my-sns-topic","Events":["s3:ObjectCreated:*"]}]}' --endpoint-url $ENDPOINT_URL

# fail NoneType
#aws s3api put-bucket-ownership-controls --bucket 50c17271-aws-cli-2 --ownership-controls '{"Rules":[{"ObjectOwnership":"BucketOwnerPreferred"}]}' --endpoint-url $ENDPOINT_URL

aws s3api put-bucket-policy --bucket 50c17271-aws-cli-2 --policy '{"Version":"2012-10-17","Statement":[{"Effect":"Allow","Principal":"*","Action":"s3:GetObject","Resource":"arn:aws:s3:::50c17271-aws-cli-2/*"}]}' --endpoint-url $ENDPOINT_URL

# fail NoneType
#aws s3api put-bucket-replication --bucket 50c17271-aws-cli-2 --replication-configuration '{"Role":"arn:aws:iam::123456789012:role/my-replication-role","Rules":[{"Status":"Enabled","Priority":1,"Prefix":"","Destination":{"Bucket":"arn:aws:s3:::my-destination-bucket"}}]}' --endpoint-url $ENDPOINT_URL

aws s3api put-bucket-request-payment --bucket 50c17271-aws-cli-2 --request-payment-configuration '{"Payer":"BucketOwner"}' --endpoint-url $ENDPOINT_URL

aws s3api get-object --bucket 50c17271-aws-cli-2 --key test_file.txt downloaded_test_file.txt --endpoint-url $ENDPOINT_URL

aws s3api get-object-tagging --bucket 50c17271-aws-cli-2 --key test_file.txt --endpoint-url $ENDPOINT_URL

aws s3api get-bucket-accelerate-configuration --bucket 50c17271-aws-cli-2 --endpoint-url $ENDPOINT_URL

aws s3api get-bucket-acl --bucket 50c17271-aws-cli-2 --endpoint-url $ENDPOINT_URL

#fail
#aws s3api get-bucket-analytics-configuration --bucket 50c17271-aws-cli-2 --analytics-configuration-id my-analytics-id --endpoint-url $ENDPOINT_URL

aws s3api get-bucket-cors --bucket 50c17271-aws-cli-2 --endpoint-url $ENDPOINT_URL

aws s3api get-bucket-encryption --bucket 50c17271-aws-cli-2 --endpoint-url $ENDPOINT_URL

aws s3api get-bucket-intelligent-tiering-configuration --bucket 50c17271-aws-cli-2 --id my-configuration-id --endpoint-url $ENDPOINT_URL

aws s3api get-bucket-inventory-configuration --bucket 50c17271-aws-cli-2 --id my-inventory-id --endpoint-url $ENDPOINT_URL

aws s3api get-bucket-lifecycle --bucket 50c17271-aws-cli-2 --endpoint-url $ENDPOINT_URL

aws s3api get-bucket-lifecycle-configuration --bucket 50c17271-aws-cli-2 --endpoint-url $ENDPOINT_URL

aws s3api get-bucket-location --bucket 50c17271-aws-cli-2 --endpoint-url $ENDPOINT_URL

aws s3api get-bucket-logging --bucket 50c17271-aws-cli-2 --endpoint-url $ENDPOINT_URL

#fail
#aws s3api get-bucket-metadata-table-configuration --bucket 50c17271-aws-cli-2 --table-name my-table-name --endpoint-url $ENDPOINT_URL

#aws s3api get-bucket-metrics-configuration --bucket 50c17271-aws-cli-2 --metrics-configuration-id my-metrics-id --endpoint-url $ENDPOINT_URL

aws s3api get-bucket-notification --bucket 50c17271-aws-cli-2 --endpoint-url $ENDPOINT_URL

aws s3api get-bucket-notification-configuration --bucket 50c17271-aws-cli-2 --endpoint-url $ENDPOINT_URL

aws s3api get-bucket-ownership-controls --bucket 50c17271-aws-cli-2 --endpoint-url $ENDPOINT_URL

aws s3api get-bucket-policy --bucket 50c17271-aws-cli-2 --endpoint-url $ENDPOINT_URL

aws s3api get-bucket-policy-status --bucket 50c17271-aws-cli-2 --endpoint-url $ENDPOINT_URL

aws s3api get-bucket-replication --bucket 50c17271-aws-cli-2 --endpoint-url $ENDPOINT_URL

aws s3api get-bucket-request-payment --bucket 50c17271-aws-cli-2 --endpoint-url $ENDPOINT_URL

aws s3api get-bucket-tagging --bucket 50c17271-aws-cli-2 --endpoint-url $ENDPOINT_URL

aws s3api get-bucket-versioning --bucket 50c17271-aws-cli-2 --endpoint-url $ENDPOINT_URL

# fail NoneType
#aws s3api get-bucket-website --bucket 50c17271-aws-cli-2 --endpoint-url $ENDPOINT_URL

aws s3api get-object --bucket 50c17271-aws-cli-2 --key test_file.txt downloaded_test_file.txt --endpoint-url $ENDPOINT_URL

aws s3api get-object-acl --bucket 50c17271-aws-cli-2 --key test_file.txt --endpoint-url $ENDPOINT_URL

#aws s3api get-object-attributes --bucket 50c17271-aws-cli-2 --key test_file.txt --attribute-name my-attribute --endpoint-url $ENDPOINT_URL

#aws s3api get-object-legal-hold --bucket 50c17271-aws-cli-2 --key test_file.txt --endpoint-url $ENDPOINT_URL

aws s3api get-object-lock-configuration --bucket 50c17271-aws-cli-2 --endpoint-url $ENDPOINT_URL

aws s3api get-object-retention --bucket 50c17271-aws-cli-2 --key test_file.txt --endpoint-url $ENDPOINT_URL

aws s3api get-object-tagging --bucket 50c17271-aws-cli-2 --key test_file.txt --endpoint-url $ENDPOINT_URL

aws s3api get-object-torrent --bucket 50c17271-aws-cli-2 --key test_file.txt --endpoint-url $ENDPOINT_URL

aws s3api get-public-access-block --bucket 50c17271-aws-cli-2 --endpoint-url $ENDPOINT_URL

aws s3api delete-object --bucket 50c17271-aws-cli-2 --key test_file.txt --endpoint-url $ENDPOINT_URL

aws s3api delete-bucket-analytics-configuration --bucket 50c17271-aws-cli --analytics-configuration-id my-analytics-id --endpoint-url $ENDPOINT_URL

aws s3api delete-bucket-cors --bucket 50c17271-aws-cli-2 --endpoint-url $ENDPOINT_URL

aws s3api delete-bucket-encryption --bucket 50c17271-aws-cli-2 --endpoint-url $ENDPOINT_URL

aws s3api delete-bucket-intelligent-tiering-configuration --bucket 50c17271-aws-cli-2 --id my-configuration-id --endpoint-url $ENDPOINT_URL

aws s3api delete-bucket-inventory-configuration --bucket 50c17271-aws-cli-2 --id my-inventory-id --endpoint-url $ENDPOINT_URL

aws s3api delete-bucket-lifecycle --bucket 50c17271-aws-cli-2 --endpoint-url $ENDPOINT_URL

aws s3api delete-bucket-metadata-configuration --bucket 50c17271-aws-cli-2 --endpoint-url $ENDPOINT_URL

aws s3api delete-bucket-metadata-table-configuration --bucket 50c17271-aws-cli-2 --table-name my-table-name --endpoint-url $ENDPOINT_URL

aws s3api delete-bucket-metrics-configuration --bucket 50c17271-aws-cli-2 --metrics-configuration-id my-metrics-id --endpoint-url $ENDPOINT_URL

aws s3api delete-bucket-ownership-controls --bucket 50c17271-aws-cli-2 --endpoint-url $ENDPOINT_URL

aws s3api delete-bucket-policy --bucket 50c17271-aws-cli-2 --endpoint-url $ENDPOINT_URL

aws s3api delete-bucket-replication --bucket 50c17271-aws-cli-2 --endpoint-url $ENDPOINT_URL

aws s3api delete-bucket-tagging --bucket 50c17271-aws-cli-2 --endpoint-url $ENDPOINT_URL

aws s3api delete-bucket-website --bucket 50c17271-aws-cli-2 --endpoint-url $ENDPOINT_URL

aws s3api delete-object --bucket 50c17271-aws-cli-2 --key test_file.txt --endpoint-url $ENDPOINT_URL

aws s3api delete-object-tagging --bucket 50c17271-aws-cli-2 --key test_file.txt --endpoint-url $ENDPOINT_URL

aws s3api delete-objects --bucket 50c17271-aws-cli-2 --delete '{"Objects":[{"Key":"object-key-1"},{"Key":"object-key-2"}]}' --endpoint-url $ENDPOINT_URL

aws s3api delete-public-access-block --bucket 50c17271-aws-cli-2 --endpoint-url $ENDPOINT_URL

aws s3api copy-object --bucket 50c17271-aws-cli-2 --copy-source 50c17271-aws-cli-2/test_file.txt --key test_file2.txt --endpoint-url $ENDPOINT_URL

aws s3api restore-object --bucket 50c17271-aws-cli-2 --key my-archived-object --restore-request '{"Days":7,"GlacierJobParameters":{"Tier":"Standard"}}' --endpoint-url $ENDPOINT_URL

aws s3api select-object-content --bucket 50c17271-aws-cli-2 --key test_file.txt --expression "SELECT * FROM S3Object" --expression-type SQL --input-serialization '{"CSV":{"FileHeaderInfo":"USE"}}' --output-serialization '{"CSV":{}}' --endpoint-url $ENDPOINT_URL

aws s3api delete-object --bucket 50c17271-aws-cli-2 --key old-object-key --endpoint-url $ENDPOINT_URL


#aws s3api delete-bucket --bucket 50c17271-aws-cli --endpoint-url $ENDPOINT_URL


## не забыть скрипт загрузки мультипартов.

