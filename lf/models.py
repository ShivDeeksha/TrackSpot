from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils import timezone
# from django.contrib.auth import get_user_model
from django.conf import settings


class WebsiteUserManager(BaseUserManager):
    def create_user(self, username, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        return self.create_user(username, email, password, **extra_fields)

def default_profile_image_path():
    return 'profile_images/default.avif'
class WebsiteUser(AbstractBaseUser, PermissionsMixin):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, default=1)
    first_name = models.CharField(max_length=100)
    middle_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    username = models.CharField(max_length=100, unique=True)
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=15)
    prn_number = models.CharField(max_length=20, unique=True)
    college_id_image = models.ImageField(upload_to='college_ids/', blank=True, null=True)
    date_joined = models.DateTimeField(default=timezone.now)
    profile_image = models.ImageField(upload_to='profile_images/', default=default_profile_image_path, blank=True, null=True)
    is_verified = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = WebsiteUserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    def __str__(self):
        return self.username

    @property
    def is_anonymous(self):
        return False

    @property
    def is_authenticated(self):
        return True

class UploadedItem(models.Model):
    uploader = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    name = models.CharField(max_length=100, null=True)
    description = models.TextField()
    location = models.CharField(max_length=100, null=True)
    # contact = models.CharField(max_length=100)
    image = models.ImageField(upload_to='uploaded_items/', null=True)
    claimed = models.BooleanField(default=False)
    def __str__(self):
        return self.name

class Question(models.Model):
    item = models.ForeignKey('UploadedItem', related_name='questions', on_delete=models.CASCADE)
    text = models.CharField(max_length=255)

    def __str__(self):
        return self.text

class Answer(models.Model):
    item = models.ForeignKey('UploadedItem', related_name='answers', on_delete=models.CASCADE)
    question = models.ForeignKey('Question', related_name='answers', on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    answer_text = models.TextField()

    def __str__(self):
        return f"Answer by {self.user.username} for question '{self.question.text}' on item '{self.item.name}'"



class Notification(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    message = models.TextField()
    approver_username = models.CharField(max_length=100,default="MYAdmin")  # Add field for approver's username
    approver_phone_number = models.CharField(max_length=15,default="1234567897")  # Add field for approver's phone number
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.user.username} - {self.message}"
