FROM python:3.12-slim

WORKDIR /app

COPY . /app

RUN apt-get update && apt-get install -y git
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install git+https://github.com/ftpskid/discord.py.git
RUN apt-get install -y tk

CMD ["python", "main.py"]
