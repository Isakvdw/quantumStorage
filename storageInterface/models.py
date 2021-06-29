from django.db import models
from django.conf import settings
#==
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.contrib.auth.hashers import make_password
from quantumStorage.settings import AUTH_SALT
import binascii
import os
###############################################################################
#                          CODING CONVENTIONS
# ------------------------------------------------------------------------------
#   - field names are lowercase separated by underscores
#   - class names each word begins with capital and no spaces between words
#   - files are named with underscores
#   - Add comments to explain
###############################################################################

# Defines the bucket model
class Bucket(models.Model):
    # id = models.AutoField(primary_key=True)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    name = models.CharField(null=False, max_length=50)

    class Meta:
        unique_together = ("owner","name")

# @returns (user: StorageUser, bucket: Bucket)
class AppTokenManager(models.Manager):
    def authenticate(self, app_token):
        key = self.objects.filter(token=app_token)
        return key.first().user, key.first().bucket if key.exists() else None, None

    def create_token(self, user, bucket):
        token = binascii.hexlify(os.urandom(20)).decode()
        self.objects.create(token=token, user=user,bucke=bucket)
        return token

# Defines the model that holds the application authentication/authorization tokens.
class AppTokens(models.Model):
    # hash of the application token that is used to access and update a bucket
    token = models.CharField(primary_key=True, null=False, max_length=20)
    # user who the token belongs to
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    # Bucket the key is bound to
    bucket = models.ForeignKey(Bucket, on_delete=models.CASCADE)
    objects = AppTokenManager()


class DownloadTokens(models.Model):
    # id = models.AutoField(primary_key=True)
    #Need to check for length

    # Location of the file in the bucket
    location = models.CharField(max_length=150) # unique=True
    # When the token was created, provides expiry ability if needed in future, serves to validate key - hence its the primary key
    timestamp = models.DateTimeField(primary_key=True)
    # which bucket its stored in
    bucket = models.ForeignKey(Bucket, on_delete=models.CASCADE)


class StorageUserManager(BaseUserManager):
    def create_user(self, email, username, password):
        """
        Creates and saves a User with the given email and password.
        """
        if not email:
            raise ValueError('Users must have an email address')
        if not username:
            raise ValueError('Users must have an username address')
        if not password:
            raise ValueError('Users must have an password address')

        # email = self.normalize_email(email)
        # user = self.model(email=email, **extra_fields)
        # user.set_password(password)
        # user.save()
        # return user

        user = self.model(
            email=self.normalize_email(email),
            username=username,
        )

        user.set_password(password)
        # triggers password_changed() -> which will also trigger custom auth to update token
        user.save(using=self._db)
        return user

    def create_superuser(self, email, username, password):
        """
        Creates and saves a superuser with the given email and password.
        """

        user = self.create_user(
            email,
            password=password,
            username=username,
        )
        user.is_admin = True
        user.save(using=self._db)
        return user


class StorageUser(AbstractBaseUser):
    username = models.CharField(max_length=50, primary_key=True)
    # email = models.EmailField(verbose_name='email', max_length=50, unique=True, primary_key=True)
    email = models.EmailField(verbose_name='email', max_length=255, unique=True)

    # refer to auth.py for masterkey handling
    masterkey = models.CharField(max_length=40, unique=True)
    quota = models.PositiveIntegerField(default=1024*1024) # 1 MB

    # creation_date = models.DateTimeField(verbose_name='creation_date', auto_now_add=True)
    # last_login = models.DateTimeField(verbose_name='last_login', auto_now=True)

    #admin page required fields
    is_active = models.BooleanField(default='True')
    is_admin = models.BooleanField(default='False')

    EMAIL_FIELD = 'email'
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email'] #this affects createsuperuser, but add anyway

    objects = StorageUserManager()

    # _masterkey = None
    # def save(self, *args, **kwargs):
    #     super().save(*args, **kwargs)
    #     if self._password is not None:
    #         password_validation.password_changed(self._password, self)
    #         self._password = None
    #     self._masterkey = None


    def set_password(self, raw_password):
        self.password = make_password(raw_password)
        key = binascii.hexlify(os.urandom(20)).decode()
        temp = make_password(key, AUTH_SALT)
        self.masterkey = temp
        # Todo: Do this a different way
        print(temp)
        print(key)
        self._password = raw_password
        return key

    #Printout display name
    def __str__(self):
        return self.email

    def has_perm(self, perm, obj=None):
        return self.is_staff

    #We dont restrict on models, change if needed in future
    # def has_module_perms(self, app_label):
    #     return True

    @property
    def is_staff(self):
        # All admins are staff for our purposes
        return self.is_admin
