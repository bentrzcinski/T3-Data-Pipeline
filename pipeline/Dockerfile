FROM public.ecr.aws/lambda/python:3.9

WORKDIR ${LAMBDA_TASK_ROOT}

COPY requirements.txt ./
RUN pip3 install --no-cache-dir -r requirements.txt

COPY pipeline/load.py ./
COPY pipeline/report.py ./

CMD ["report.lambda_handler"]