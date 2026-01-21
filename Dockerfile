#base image
FROM python:3.13-slim

#set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

#set the working directory
WORKDIR /app

#copy the requirements file and install dependencies
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

#copy the application code
COPY . /app

#expose the port
EXPOSE 5000

#run the application
CMD ["python", "run.py"]    