import os
import django

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'TrackSpot.settings')
django.setup()

from django.contrib.auth import get_user_model

# Get the custom user model
User = get_user_model()
# Create superuser if not exists
username = os.getenv('username')
email = os.getenv('email')
password = os.getenv('password')

if not User.objects.filter(username=username).exists():
    User.objects.create_superuser(username=username, email=email, password=password)
    print('Superuser created.')
else:
    print('Superuser already exists.')
