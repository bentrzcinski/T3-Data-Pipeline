variable "task_execution_role_arn" {
    description = "The Amazon Resource Name (ARN) of the IAM role that ECS is using to access our ECR image."
    type = string
}

variable "ecr_image_uri" {
    description = "The URI of our Dockerized pipeline image uploaded to ECR."
    type = string
}

variable "aws_access_key_id" {
    description = "The access key ID for the S3 bucket containing the raw truck data."
    type = string
}

variable "aws_secret_access_key" {
    description = "The secret access key for the S3 bucket containing the raw truck data."
    type = string
}

variable "db_name" {
    description = "The name of our Redshift database."
    type = string
}

variable "db_username" {
    description = "The username for our Redshift database."
    type = string
}

variable "db_password" {
    description = "The password for our Redshift database."
    type = string
}

variable "db_host" {
    description = "The IP address of our Redshift database hosted on AWS."
    type = string
}

variable "db_port" {
    description = "The port we connect to our Redshift database on."
    type = string
}

variable "db_schema" {
    description = "The name of the schema we connect to within the Redshift database."
    type = string
}

variable "ecs_cluster_arn" {
    description = "The arn of the c14 ECS cluster."
    type = string
}
