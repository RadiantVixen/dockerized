from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager, User

class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        return self.create_user(email, password, **extra_fields)

class User(AbstractUser):
    name = models.CharField(max_length=255, default='default_name')
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=150, unique=True)
    objects = UserManager()
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    display_name = models.CharField(max_length=50, unique=True)
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    language = models.CharField(max_length=10, choices=[('en', 'English'), ('fr', 'French')])

class Friend(models.Model):
    user = models.ForeignKey(Profile, related_name='friends', on_delete=models.CASCADE)
    friend = models.ForeignKey(Profile, related_name='friends_of', on_delete=models.CASCADE)

class GameHistory(models.Model):
    user = models.ForeignKey(Profile, on_delete=models.CASCADE)
    date_played = models.DateTimeField(auto_now_add=True)
    opponent = models.CharField(max_length=50)
    score = models.IntegerField()
