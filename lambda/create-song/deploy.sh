#!/usr/bin/env bash

set -euxo pipefail

LAMBDA_NAME="party-jams-dot-biz"

mkdir -p deployable
mkdir -p target
rm -f deployable/function.zip

# why doesn't it work?
#pip install -r requirements.txt --target ./target
cd target/
zip -r9 $OLDPWD/deployable/function.zip .
cd $OLDPWD
zip -g deployable/function.zip lambda_function.py
aws lambda update-function-code --function-name $LAMBDA_NAME --zip-file fileb://deployable/function.zip
