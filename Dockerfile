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

# Ensure popper.min.js and popper.min.js.map are present
RUN mkdir -p /app/static/vendors/popperjs /app/media && \
    curl -o /app/static/vendors/popperjs/popper.min.js https://cdnjs.cloudflare.com/ajax/libs/popper.js/1.14.7/umd/popper.min.js && \
    curl -o /app/static/vendors/popperjs/popper.min.js.map https://cdnjs.cloudflare.com/ajax/libs/popper.js/1.14.7/umd/popper.min.js.map

# Set environment variables for Django
ENV DJANGO_SETTINGS_MODULE=TrackSpot.settings
ENV PYTHONUNBUFFERED 1

# Copy and set permissions for wait-for-it.sh
COPY wait_for_db.py /wait_for_db.py

# Collect static files
RUN python manage.py collectstatic --noinput

RUN chmod -R 755 /app/media
RUN chown -R www-data:www-data /app/media

# Expose port 8000 to the outside world
EXPOSE 8000

# Wait for the PostgreSQL server to be ready, then run migrations and create superuser
CMD ["sh", "-c", "python /wait_for_db.py && python manage.py migrate && python create_superuser.py && gunicorn --bind 0.0.0.0:8000 --workers 3 TrackSpot.wsgi:application"]
