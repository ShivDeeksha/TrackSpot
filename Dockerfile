# Use the official Python image
FROM python:3.12

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt /app/requirements.txt

# Install the dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire project into the container
COPY . /app

# Set environment variables for Django
ENV DJANGO_SETTINGS_MODULE=TrackSpot.settings
ENV PYTHONUNBUFFERED 1

# Collect static files
RUN python manage.py collectstatic --noinput

# Expose port 8000 to the outside world
EXPOSE 8000

# Run the Gunicorn server
CMD ["gunicorn", "--config", "gunicorn_config.py", "TrackSpot.wsgi:application"]
