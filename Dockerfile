FROM python:3.11
# Später auf tiangolo/uvicorn-gunicorn-fastapi:latest umstellen

# 
WORKDIR /app

# 
COPY ./requirements.txt /app/requirements.txt

# 
RUN pip install --no-cache-dir --upgrade -r /app/requirements.txt

# 
COPY . /app

#
EXPOSE 8140

RUN chmod +x /app
# 
CMD ["uvicorn", "main:app", "--proxy-headers", "--host", "0.0.0.0", "--port", "8140"]