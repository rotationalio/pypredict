FROM python:3.8

WORKDIR /usr/src/app

COPY pypredict/requirements.txt ./
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

COPY ./entrypoint.sh /usr/src/app/entrypoint.sh

RUN chmod +x /usr/src/app/entrypoint.sh

COPY ./pypredict ./pypredict

CMD ["/bin/bash", "-c", "./entrypoint.sh"]