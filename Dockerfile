FROM python:3.9-slim

EXPOSE 5000
WORKDIR /app
COPY ./ /app
RUN pip install -r /app/requirements.txt
CMD ["flask", "run", "-h", "0.0.0.0"]