FROM python:3.12-alpine
WORKDIR /app
COPY app.py cert-365days.pem key.pem ./
RUN pip install flask
EXPOSE 8443
CMD ["python", "app.py"]
