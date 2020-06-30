provider "aws" {
  version = "~> 2.0"
  region  = "us-east-1"
}



resource "aws_dynamodb_table" "phrases" {
  name = "party-jams-dot-biz-phrases"
  hash_key = "PhraseHash"

  attribute {
    name = "PhraseHash"
    type = "S"
  }
}