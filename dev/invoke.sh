rm -f ./response.json
aws lambda invoke --function-name $1 --cli-binary-format raw-in-base64-out --payload file://payloads/$1.json response.json
jq . ./response.json
