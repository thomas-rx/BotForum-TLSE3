FROM python:3.9.7-alpine
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . app/
CMD [ "python", "app/discord_bot.py"]