# ECS Task Definition
resource "aws_ecs_task_definition" "c14-ben-task-definition-batch" {
  family                   = "c14-ben-task-definition-batch"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = "256"
  memory                   = "512"
  execution_role_arn       = var.task_execution_role_arn

  container_definitions = jsonencode([
    {
      name      = "c14-ben-truck-etl-batch"
      image     = var.ecr_image_uri
      cpu       = 256
      memory    = 512
      essential = true
      environment = [
        {
          name  = "AWS_ACCESS_KEY_ID"
          value = var.aws_access_key_id
        },
        {
          name  = "AWS_SECRET_ACCESS_KEY"
          value = var.aws_secret_access_key
        },
        {
          name  = "DATABASE_USERNAME"
          value = var.db_username
        },
        {
          name  = "DATABASE_PASSWORD"
          value = var.db_password
        },
        {
          name  = "DATABASE_IP"
          value = var.db_host
        },
        {
          name  = "DATABASE_PORT"
          value = var.db_port
        },
        {
          name  = "DATABASE_NAME"
          value = var.db_name
        },
        {
          name  = "DATABASE_SCHEMA"
          value = var.db_schema
        }
      ]
      logConfiguration = {
        logDriver = "awslogs"
        options = {
          awslogs-create-group = "true"
          awslogs-group         = "/ecs/c14-ben-truck-etl-batch"
          awslogs-region        = "eu-west-2"
          awslogs-stream-prefix = "ecs"
        }
      }
    }
  ])
}

# EventBridge Schedule
resource "aws_scheduler_schedule" "c14-ben-etl_schedule" {
  name                = "c14-ben-etl-schedule"
  description         = "Scheduler to run ECS ETL task every 3 hours at half past the hour"
  schedule_expression = "cron(30 9/3 * * ? *)"
  flexible_time_window {
    mode = "OFF"
  }

  target {
    arn      = var.ecs_cluster_arn
    role_arn = aws_iam_role.c14-ben-eventbridge-role.arn

    ecs_parameters {
      task_definition_arn = aws_ecs_task_definition.c14-ben-task-definition-batch.arn
      launch_type         = "FARGATE"
      network_configuration {
        subnets = ["subnet-0497831b67192adc2", "subnet-0acda1bd2efbf3922", "subnet-0465f224c7432a02e"]
        security_groups  = ["sg-09cfa7d5cc78a795a"]
        assign_public_ip = true
      }
    }
  }
}

resource "aws_iam_role" "c14-ben-eventbridge-role" {
  name = "c14-ben-eventbridge-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "scheduler.amazonaws.com"
        }
      }
    ]
  })
}

resource "aws_iam_role_policy" "c14-ben-eventbridge-scheduler-policy" {
  name = "c14-ben-eventbridge-scheduler-policy"
  role = aws_iam_role.c14-ben-eventbridge-role.id

  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Effect = "Allow",
        Action = ["ecs:RunTask"],
        Resource = [
          aws_ecs_task_definition.c14-ben-task-definition-batch.arn
        ]
        },
      {
        Effect = "Allow",
        Action = [
          "iam:PassRole"
        ],
        Resource = "*"
      }
    ]
  })
}

# Lambda Function
data "aws_ecr_repository" "c14-ben-report-ecr" {
  name = "c14-ben-report-ecr"
}

resource "aws_lambda_function" "c14-ben-report-lambda" {
  function_name = "c14-ben-report-lambda"
  package_type  = "Image"
  architectures = ["x86_64"]

  image_uri     = "129033205317.dkr.ecr.eu-west-2.amazonaws.com/c14-ben-report-ecr@sha256:05ffd41752a6b205e69c178ecf57bf1ba17092b5e301865d656bb8e89ad68f70"

  memory_size = 512
  timeout     = 300

  role = aws_iam_role.c14-ben-lambda-execution-role.arn

  environment {  
    variables = {
      DATABASE_USERNAME = var.db_username
      DATABASE_PASSWORD = var.db_password
      DATABASE_IP = var.db_host
      DATABASE_PORT = var.db_port
      DATABASE_NAME = var.db_name
      DATABASE_SCHEMA = var.db_schema
  }
  }
}

resource "aws_iam_role" "c14-ben-lambda-execution-role" {
  name = "c14-ben-lambda-execution-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Principal = {
          Service = "lambda.amazonaws.com"
        }
        Effect   = "Allow"
        Sid      = ""
      }
    ]
  })
}

resource "aws_iam_role_policy" "c14-ben-lambda_policy" {
  name = "c14-ben-lambda_policy"
  role = aws_iam_role.c14-ben-lambda-execution-role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = [
          "logs:*",
          "ecr:GetAuthorizationToken",
          "ecr:BatchCheckLayerAvailability",
          "ecr:GetDownloadUrlForLayer"
        ]
        Effect   = "Allow"
        Resource = "*"
      }
    ]
  })
}
