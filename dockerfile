# Use official Python image as base
FROM python:3.11-slim

# Set the working directory
WORKDIR /app

# Copy requirements file and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

RUN pip install -U langchain-community

# Copy FastAPI app files
COPY . .

# Expose the FastAPI port
EXPOSE 8000

# Set the default command to run the app
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
