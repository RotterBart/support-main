FROM python:3.8.13-bullseye
WORKDIR /app
COPY requirements.txt /app
RUN pip3 install -r requirements.txt
COPY . /app
ENTRYPOINT [ "python" ]
CMD [ "app.py" ]