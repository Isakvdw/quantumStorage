from django.contrib.auth.backends import BaseBackend
from storageInterface.models import StorageUser
from django.contrib.auth.hashers import check_password, make_password
# from quantumStorage.settings import AUTH_SALT
from django.conf import settings

class AuthToken(BaseBackend):
    def authenticate(self, request, token=None):
        # Check the token, pass in the salt(pepper) - we can't use a salt since we dont have an independent identifier
        token_hash = make_password(token, settings.AUTH_SALT)
        try:
            return StorageUser.objects.get(masterkey=token_hash)
        except StorageUser.DoesNotExist:
            return None

    def get_user(self, user_id):
        # Check the username/password and return a user.
        try:
            return StorageUser.objects.get(pk=user_id)
        except StorageUser.DoesNotExist:
            return None