aws ecr get-login-password --region eu-west-2 | docker login --username AWS --password-stdin 129033205317.dkr.ecr.eu-west-2.amazonaws.com

docker tag batch-pipeline:latest 129033205317.dkr.ecr.eu-west-2.amazonaws.com/c14-ben-ecr-batch:latest

docker push 129033205317.dkr.ecr.eu-west-2.amazonaws.com/c14-ben-ecr-batch:latest