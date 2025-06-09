# Stage 1: Use an official Python runtime as a parent image
# Using a "slim" image is a good practice for smaller production images.
FROM python:3.11-slim

# Stage 2: Set the working directory inside the container
WORKDIR /app

# Stage 3: Copy and install dependencies
# Copying requirements.txt first leverages Docker's layer caching.
# If requirements.txt doesn't change, Docker won't re-install dependencies on every build.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Stage 4: Copy the application code into the container
# This copies everything from your project's root into the container's /app directory.
COPY . .

# Stage 5: Expose the port the app runs on
# Gradio defaults to 7860. We're telling Docker that the container will listen on this port.
EXPOSE 7860

# Disable output buffering
ENV PYTHONUNBUFFERED=1

# Stage 6: Define the command to run the application
# This is the command that will be executed when the container starts.
# "0.0.0.0" is crucial to make the server accessible from outside the container.
CMD ["python", "app.py"]
