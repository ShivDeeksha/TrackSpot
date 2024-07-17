import os
import django
from django.contrib.auth.models import User

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'TrackSpot.settings')
django.setup()

# Create superuser if not exists
username = 'admin'
email = 'admin@example.com'
password = 'disha123'

if not User.objects.filter(username=username).exists():
    User.objects.create_superuser(username=username, email=email, password=password)
    print('Superuser created.')
else:
    print('Superuser already exists.')
