provider "aws" {
  access_key = "mock"
  secret_key = "mock"
  region     = "us-east-1"
  s3_use_path_style = true
  
  # Skip credential validation for LocalStack
  skip_credentials_validation = true
  skip_metadata_api_check     = true
  skip_region_validation      = true
  skip_requesting_account_id  = true
  
  endpoints {
    s3 = "http://localhost:4566"
  }
}