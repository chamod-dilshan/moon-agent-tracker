# Use an official Python image
FROM python:3.10

# Set the working directory inside the container
WORKDIR /app

# Copy the app files into the container
COPY . .

# Install dependencies
RUN pip install -r requirements.txt

# Start the Flask app
CMD ["python", "app.py"]