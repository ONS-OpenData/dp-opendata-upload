FROM public.ecr.aws/lambda/python:3.8

# Lambda name from build arg.
ARG LAMBDA_NAME

# Copy function code and common code
COPY ./${LAMBDA_NAME}/* ${LAMBDA_TASK_ROOT}/
COPY ./common/* ${LAMBDA_TASK_ROOT}/

# Install the function's dependencies using file requirements.txt
COPY ./${LAMBDA_NAME}/requirements.txt .
RUN  pip3 install -r requirements.txt --target "${LAMBDA_TASK_ROOT}"

CMD [ "app.handler" ]
