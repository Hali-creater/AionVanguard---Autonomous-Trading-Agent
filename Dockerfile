# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container at /app
COPY aionvanguard/requirements.txt .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application's code from the host to the container at /app
COPY aionvanguard/ .

# Make port 8501 available to the world outside this container
EXPOSE 8501

# Run the app when the container launches
CMD ["streamlit", "run", "main.py"]
