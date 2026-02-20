#!/bin/bash

# Установите переменную для конечного URL
ENDPOINT_URL="https://s3.twcstorage.ru"
BUCKET="file-storage"


aws s3api create-bucket --bucket $BUCKET --region ru-1 --endpoint-url $ENDPOINT_URL

echo "This is a test file." > test_file.txt
aws s3api put-object --bucket $BUCKET --key test_file.txt --body test_file.txt --endpoint-url $ENDPOINT_URL

#fail
#aws s3api put-bucket-notification --bucket $BUCKET --notification-configuration '{"TopicConfigurations":[{"TopicArn":"arn:aws:sns:ru-1:123456789012:my-sns-topic","Events":["s3:ObjectCreated:*"]}]}' --endpoint-url $ENDPOINT_URL

#fail
#aws s3api put-bucket-notification-configuration --bucket $BUCKET --notification-configuration '{"TopicConfigurations":[{"TopicArn":"arn:aws:sns:ru-1:123456789012:my-sns-topic","Events":["s3:ObjectCreated:*"]}]}' --endpoint-url $ENDPOINT_URL

aws s3api put-bucket-versioning --bucket $BUCKET --versioning-configuration '{"Status":"Enabled"}' --endpoint-url $ENDPOINT_URL

aws s3api put-bucket-acl --bucket $BUCKET --acl public-read --endpoint-url $ENDPOINT_URL

aws s3api put-bucket-cors --bucket $BUCKET --cors-configuration '{"CORSRules":[{"AllowedMethods":["GET","POST"],"AllowedOrigins":["*"],"MaxAgeSeconds":3000}]}' --endpoint-url $ENDPOINT_URL

aws s3api put-bucket-lifecycle-configuration --bucket $BUCKET --lifecycle-configuration '{"Rules":[{"ID":"ExpireOldVersions","Prefix":"","Status":"Enabled","Expiration":{"Days":30}}]}' --endpoint-url $ENDPOINT_URL

#fail
#aws s3api put-bucket-replication --bucket $BUCKET --replication-configuration '{"Role":"arn:aws:iam::123456789012:role/my-replication-role","Rules":[{"Status":"Enabled","Priority":1,"Prefix":"","Destination":{"Bucket":"arn:aws:s3:::my-destination-bucket"}}]}' --endpoint-url $ENDPOINT_URL

aws s3api put-bucket-tagging --bucket $BUCKET --tagging '{"TagSet":[{"Key":"Environment","Value":"Test"},{"Key":"Project","Value":"S3Demo"}]}' --endpoint-url $ENDPOINT_URL

aws s3api put-bucket-encryption --bucket $BUCKET --server-side-encryption-configuration '{"Rules":[{"ApplyServerSideEncryptionByDefault":{"SSEAlgorithm":"AES256"}}]}' --endpoint-url $ENDPOINT_URL

aws s3api put-object-tagging --bucket $BUCKET --key test_file.txt --tagging '{"TagSet":[{"Key":"FileType","Value":"Text"}]}' --endpoint-url $ENDPOINT_URL

#fail
#aws s3api put-bucket-accelerate-configuration --bucket $BUCKET --accelerate-configuration '{"Status":"Enabled"}' --endpoint-url $ENDPOINT_URL

#aws s3api put-bucket-analytics-configuration --bucket $BUCKET --analytics-configuration '{"Id":"my-analytics-id","Filter":{"Prefix":"my-prefix"},"StorageClassAnalysis":{"DataExport":{"OutputSchema":"S3BatchOperations_CSV_20180820","Destination":{"S3BucketDestination":{"Format":"S3BatchOperations_CSV_20180820","BucketArn":"arn:aws:s3:::$BUCKET","BucketAccountId":"123456789012"}}}}}' --endpoint-url $ENDPOINT_URL

aws s3api put-bucket-cors --bucket $BUCKET --cors-configuration '{"CORSRules":[{"AllowedMethods":["GET","POST"],"AllowedOrigins":["*"],"MaxAgeSeconds":3000}]}' --endpoint-url $ENDPOINT_URL

aws s3api put-bucket-encryption --bucket $BUCKET --server-side-encryption-configuration '{"Rules":[{"ApplyServerSideEncryptionByDefault":{"SSEAlgorithm":"AES256"}}]}' --endpoint-url $ENDPOINT_URL

#fail
#aws s3api put-bucket-intelligent-tiering-configuration --bucket $BUCKET --intelligent-tiering-configuration '{"Id":"my-configuration-id","Status":"Enabled","Tierings":[{"Days":30,"Tier":"ARCHIVE"}]}' --endpoint-url $ENDPOINT_URL

#fail
#aws s3api put-bucket-inventory-configuration --bucket $BUCKET --id my-inventory-id --inventory-configuration '{"Destination":{"S3BucketDestination":{"BucketArn":"arn:aws:s3:::$BUCKET","Format":"CSV","AccountId":"123456789012"}},"IsEnabled":true,"Schedule":{"Frequency":"Daily"}}' --endpoint-url $ENDPOINT_URL

aws s3api put-bucket-lifecycle --bucket $BUCKET --lifecycle-configuration '{"Rules":[{"ID":"my-rule-id","Prefix":"my-prefix","Status":"Enabled","Expiration":{"Days":30}}]}' --endpoint-url $ENDPOINT_URL

aws s3api put-bucket-lifecycle-configuration --bucket $BUCKET --lifecycle-configuration '{"Rules":[{"ID":"my-rule-id","Prefix":"my-prefix","Status":"Enabled","Expiration":{"Days":30}}]}' --endpoint-url $ENDPOINT_URL

# fail NoneType
#aws s3api put-bucket-logging --bucket $BUCKET --bucket-logging-status '{"LoggingEnabled":{"TargetBucket":"my-log-bucket","TargetPrefix":"logs/"}}' --endpoint-url $ENDPOINT_URL

# fail
#aws s3api put-bucket-metrics-configuration --bucket $BUCKET --metrics-configuration '{"Id":"my-metrics-id","Filter":{"Prefix":"my-prefix"}}' --endpoint-url $ENDPOINT_URL

#aws s3api put-bucket-notification --bucket $BUCKET --notification-configuration '{"TopicConfigurations":[{"TopicArn":"arn:aws:sns:ru-1:123456789012:my-sns-topic","Events":["s3:ObjectCreated:*"]}]}' --endpoint-url $ENDPOINT_URL

#aws s3api put-bucket-notification-configuration --bucket $BUCKET --notification-configuration '{"TopicConfigurations":[{"TopicArn":"arn:aws:sns:ru-1:123456789012:my-sns-topic","Events":["s3:ObjectCreated:*"]}]}' --endpoint-url $ENDPOINT_URL

# fail NoneType
#aws s3api put-bucket-ownership-controls --bucket $BUCKET --ownership-controls '{"Rules":[{"ObjectOwnership":"BucketOwnerPreferred"}]}' --endpoint-url $ENDPOINT_URL

aws s3api put-bucket-policy --bucket $BUCKET --policy '{"Version":"2012-10-17","Statement":[{"Effect":"Allow","Principal":"*","Action":"s3:GetObject","Resource":"arn:aws:s3:::$BUCKET/*"}]}' --endpoint-url $ENDPOINT_URL

# fail NoneType
#aws s3api put-bucket-replication --bucket $BUCKET --replication-configuration '{"Role":"arn:aws:iam::123456789012:role/my-replication-role","Rules":[{"Status":"Enabled","Priority":1,"Prefix":"","Destination":{"Bucket":"arn:aws:s3:::my-destination-bucket"}}]}' --endpoint-url $ENDPOINT_URL

aws s3api put-bucket-request-payment --bucket $BUCKET --request-payment-configuration '{"Payer":"BucketOwner"}' --endpoint-url $ENDPOINT_URL

aws s3api get-object --bucket $BUCKET --key test_file.txt downloaded_test_file.txt --endpoint-url $ENDPOINT_URL

aws s3api get-object-tagging --bucket $BUCKET --key test_file.txt --endpoint-url $ENDPOINT_URL

aws s3api get-bucket-accelerate-configuration --bucket $BUCKET --endpoint-url $ENDPOINT_URL

aws s3api get-bucket-acl --bucket $BUCKET --endpoint-url $ENDPOINT_URL

#fail
#aws s3api get-bucket-analytics-configuration --bucket $BUCKET --analytics-configuration-id my-analytics-id --endpoint-url $ENDPOINT_URL

aws s3api get-bucket-cors --bucket $BUCKET --endpoint-url $ENDPOINT_URL

aws s3api get-bucket-encryption --bucket $BUCKET --endpoint-url $ENDPOINT_URL

aws s3api get-bucket-intelligent-tiering-configuration --bucket $BUCKET --id my-configuration-id --endpoint-url $ENDPOINT_URL

aws s3api get-bucket-inventory-configuration --bucket $BUCKET --id my-inventory-id --endpoint-url $ENDPOINT_URL

aws s3api get-bucket-lifecycle --bucket $BUCKET --endpoint-url $ENDPOINT_URL

aws s3api get-bucket-lifecycle-configuration --bucket $BUCKET --endpoint-url $ENDPOINT_URL

aws s3api get-bucket-location --bucket $BUCKET --endpoint-url $ENDPOINT_URL

aws s3api get-bucket-logging --bucket $BUCKET --endpoint-url $ENDPOINT_URL

#fail
#aws s3api get-bucket-metadata-table-configuration --bucket $BUCKET --table-name my-table-name --endpoint-url $ENDPOINT_URL

#aws s3api get-bucket-metrics-configuration --bucket $BUCKET --metrics-configuration-id my-metrics-id --endpoint-url $ENDPOINT_URL

aws s3api get-bucket-notification --bucket $BUCKET --endpoint-url $ENDPOINT_URL

aws s3api get-bucket-notification-configuration --bucket $BUCKET --endpoint-url $ENDPOINT_URL

aws s3api get-bucket-ownership-controls --bucket $BUCKET --endpoint-url $ENDPOINT_URL

aws s3api get-bucket-policy --bucket $BUCKET --endpoint-url $ENDPOINT_URL

aws s3api get-bucket-policy-status --bucket $BUCKET --endpoint-url $ENDPOINT_URL

aws s3api get-bucket-replication --bucket $BUCKET --endpoint-url $ENDPOINT_URL

aws s3api get-bucket-request-payment --bucket $BUCKET --endpoint-url $ENDPOINT_URL

aws s3api get-bucket-tagging --bucket $BUCKET --endpoint-url $ENDPOINT_URL

aws s3api get-bucket-versioning --bucket $BUCKET --endpoint-url $ENDPOINT_URL

# fail NoneType
#aws s3api get-bucket-website --bucket $BUCKET --endpoint-url $ENDPOINT_URL

aws s3api get-object --bucket $BUCKET --key test_file.txt downloaded_test_file.txt --endpoint-url $ENDPOINT_URL

aws s3api get-object-acl --bucket $BUCKET --key test_file.txt --endpoint-url $ENDPOINT_URL

#aws s3api get-object-attributes --bucket $BUCKET --key test_file.txt --attribute-name my-attribute --endpoint-url $ENDPOINT_URL

#aws s3api get-object-legal-hold --bucket $BUCKET --key test_file.txt --endpoint-url $ENDPOINT_URL

aws s3api get-object-lock-configuration --bucket $BUCKET --endpoint-url $ENDPOINT_URL

aws s3api get-object-retention --bucket $BUCKET --key test_file.txt --endpoint-url $ENDPOINT_URL

aws s3api get-object-tagging --bucket $BUCKET --key test_file.txt --endpoint-url $ENDPOINT_URL

aws s3api get-object-torrent --bucket $BUCKET --key test_file.txt --endpoint-url $ENDPOINT_URL

aws s3api get-public-access-block --bucket $BUCKET --endpoint-url $ENDPOINT_URL

aws s3api delete-object --bucket $BUCKET --key test_file.txt --endpoint-url $ENDPOINT_URL

aws s3api delete-bucket-analytics-configuration --bucket 50c17271-aws-cli --analytics-configuration-id my-analytics-id --endpoint-url $ENDPOINT_URL

aws s3api delete-bucket-cors --bucket $BUCKET --endpoint-url $ENDPOINT_URL

aws s3api delete-bucket-encryption --bucket $BUCKET --endpoint-url $ENDPOINT_URL

aws s3api delete-bucket-intelligent-tiering-configuration --bucket $BUCKET --id my-configuration-id --endpoint-url $ENDPOINT_URL

aws s3api delete-bucket-inventory-configuration --bucket $BUCKET --id my-inventory-id --endpoint-url $ENDPOINT_URL

aws s3api delete-bucket-lifecycle --bucket $BUCKET --endpoint-url $ENDPOINT_URL

aws s3api delete-bucket-metadata-configuration --bucket $BUCKET --endpoint-url $ENDPOINT_URL

aws s3api delete-bucket-metadata-table-configuration --bucket $BUCKET --table-name my-table-name --endpoint-url $ENDPOINT_URL

aws s3api delete-bucket-metrics-configuration --bucket $BUCKET --metrics-configuration-id my-metrics-id --endpoint-url $ENDPOINT_URL

aws s3api delete-bucket-ownership-controls --bucket $BUCKET --endpoint-url $ENDPOINT_URL

aws s3api delete-bucket-policy --bucket $BUCKET --endpoint-url $ENDPOINT_URL

aws s3api delete-bucket-replication --bucket $BUCKET --endpoint-url $ENDPOINT_URL

aws s3api delete-bucket-tagging --bucket $BUCKET --endpoint-url $ENDPOINT_URL

aws s3api delete-bucket-website --bucket $BUCKET --endpoint-url $ENDPOINT_URL

aws s3api delete-object --bucket $BUCKET --key test_file.txt --endpoint-url $ENDPOINT_URL

aws s3api delete-object-tagging --bucket $BUCKET --key test_file.txt --endpoint-url $ENDPOINT_URL

aws s3api delete-objects --bucket $BUCKET --delete '{"Objects":[{"Key":"object-key-1"},{"Key":"object-key-2"}]}' --endpoint-url $ENDPOINT_URL

aws s3api delete-public-access-block --bucket $BUCKET --endpoint-url $ENDPOINT_URL

aws s3api copy-object --bucket $BUCKET --copy-source $BUCKET/test_file.txt --key test_file2.txt --endpoint-url $ENDPOINT_URL

aws s3api restore-object --bucket $BUCKET --key my-archived-object --restore-request '{"Days":7,"GlacierJobParameters":{"Tier":"Standard"}}' --endpoint-url $ENDPOINT_URL

aws s3api select-object-content --bucket $BUCKET --key test_file.txt --expression "SELECT * FROM S3Object" --expression-type SQL --input-serialization '{"CSV":{"FileHeaderInfo":"USE"}}' --output-serialization '{"CSV":{}}' --endpoint-url $ENDPOINT_URL

aws s3api delete-object --bucket $BUCKET --key old-object-key --endpoint-url $ENDPOINT_URL


#aws s3api delete-bucket --bucket 50c17271-aws-cli --endpoint-url $ENDPOINT_URL


## не забыть скрипт загрузки мультипартов.

