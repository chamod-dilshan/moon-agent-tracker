# Use an official Python image
FROM python:3.10

# Set the working directory inside the container
WORKDIR /app

# Copy the app files into the container
COPY . .

# Install dependencies
RUN pip install -r requirements.txt

# Expose the Flask app's port
EXPOSE 5001

# Start the Flask app
CMD ["python", "app.py"]