# Tasty Truck Treats (T3) Data Pipeline Project

<img src="https://everydaybest.com/wp-content/uploads/2013/04/food-truckin.jpg" style="width: 400px;" />

## Project Overview

Tasty Truck Treats (T3) operates a fleet of food trucks throughout Lichfield and surrounding areas, offering a variety of culinary options, from gourmet sandwiches to desserts. Each truck has a unique menu and operates semi-independently, allowing T3 to cater to diverse tastes across multiple high-traffic locations. Historically, T3 gathered only monthly sales summaries from each truck, which limited the company’s ability to make timely, data-informed decisions. This project seeks to implement an automated, transaction-level data pipeline to support real-time analytics and enhance T3's ability to optimize its operations, marketing, and menu offerings.

## Stakeholders

1. **Hiram Boulie (Chief Financial Officer)**  
   Hiram’s primary responsibilities include overseeing T3’s financial health and supporting acquisition discussions. His focus is on:
   - Reducing operational costs
   - Increasing overall profitability

2. **Miranda Courcelle (Head of Culinary Experience)**  
   Miranda manages truck menus and locations, aiming to ensure T3’s offerings remain appealing, affordable, and aligned with customer preferences. Her role involves leveraging data to understand customer demand by location and menu type, which is essential for her strategic planning.


## Problem  
- No centralised system to track financial performance and cost efficiency.  
- No data-driven insights into which cuisines and price points perform best at different locations.  
- Reporting was manual, making it difficult to analyze trends effectively.  

## Solution  
- **Automated ETL Pipeline**:  
  - **EventBridge (Every 3 hours)** → Triggers an **ECS task** running the ETL pipeline.  
  - Extracts data from **S3**, cleans it, and loads it into **Redshift**.  
- **Data Visualisation**:  
  - **Streamlit dashboard (24/7 via ECS service)** for real-time insights on truck performance and customer demand.  
- **Automated Financial Reports**:  
  - **EventBridge (Every 24 hours)** → Triggers a **Step Function**.  
  - **Lambda** queries **Redshift** to generate reports.  
  - Reports are emailed to the CEO using **SES**.

## Setup Instructions

### 1. Clone the Repository

```zsh
git clone <repository-url>
cd T3-Data-Pipeline
```

### 2. Create a Virtual Environment

Create a virtual environment to manage dependencies:

```zsh
python -m venv .venv
source .venv/bin/activate
```

### 3. Install Dependencies

Install the required Python packages:

```zsh
pip3 install -r requirements.txt
```

### 4. Setup Environment Variables

Create a .env file in the root directory with the following content:

```markdown
DATABASE_IP=<your-database-ip>
DATABASE_PORT=5439
DATABASE_NAME=<your-database-name>
DATABASE_USERNAME=<your-database-username>
DATABASE_PASSWORD=<your-database-password>
DATABASE_SCHEMA=<your-database-schema>
AWS_ACCESS_KEY_ID=<your-aws-access-key-id>
AWS_SECRET_ACCESS_KEY=<your-aws-secret-access-key>
AWS_REGION=<your-aws-region>
```

### 5. Setup Terraform Variables

Create a terraform.tfvars file in the terraform directory with the following content:

```markdown
task_execution_role_arn="<your-task-execution-role-arn>"
ecr_image_uri="<your-ecr-image-uri>
ecs_cluster_arn="<your-ecs-cluster-arn>"
aws_access_key_id="<your-aws-access-key-id>"
aws_secret_access_key="<your-aws-secret-access-key>"
db_name="<your-database-name>"
db_username="<your-database-username>"
db_password="<your-database-password>"
db_host="<your-database-ip>"
db_port="5439"
db_schema="<your-database-schema>"
```