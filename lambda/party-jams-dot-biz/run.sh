mkdir -p log
aws lambda invoke --function-name party-jams-dot-biz --log-type Tail log/output.txt
cat log/output.txt

