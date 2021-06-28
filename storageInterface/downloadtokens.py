from datetime import datetime, timedelta, timezone
from django.conf import settings
from django.utils.crypto import constant_time_compare, salted_hmac
from django.utils.http import base36_to_int, int_to_base36
from .models import DownloadTokens
from quantumStorage.settings import STORAGE_ROOT
from django.core.files.storage import FileSystemStorage
from os import path
# Generates a one time use token to access a file
# based on PasswordResetTokenGenerator from django.contrib.auth.tokens
class QuantumStorageTokenGenerator:

    key_salt = "django.contrib.auth.tokens.QuantumStorageTokenGenerator"
    algorithm = settings.DEFAULT_HASHING_ALGORITHM
    secret = settings.SECRET_KEY

    def make_token(self, bucket, file_path):
        # Return a token that can be used once to access a file
        _now = datetime.now()
        now = int((_now - datetime(2001, 1, 1)).total_seconds()*1000000)
        newToken = DownloadTokens.objects.create(bucket=bucket,location=file_path, timestamp=_now)
        return self._make_token(newToken, now)

    def use_token(self, token):
        # Check if access token is valid for given file.

        if not token:
            return False
        # Parse the token
        try:
            # date is base36 encoded
            ts_b36, _ = token.split("-")
            ts = base36_to_int(ts_b36)
        except ValueError:
            return False

        try:
            currToken = DownloadTokens.objects.get(timestamp=timedelta(microseconds=ts)+datetime(2001,1,1).replace(tzinfo=None))
            #
        except DownloadTokens.DoesNotExist:
            return False

        currRoot = path.join(STORAGE_ROOT, str(currToken.bucket.id))
        fs = FileSystemStorage(location=currRoot, base_url=None)
        if not fs.exists(currToken.location):
            currToken.delete()
            return False

        # Check that the timestamp/uid has not been tampered with
        # constant_time_compare() prevents timing attacks
        if not constant_time_compare(self._make_token(currToken, ts), token):
            currToken.delete()
            return False

        # can be uncommented to provide token expiration date
        now = int((datetime.now() - datetime(2001, 1, 1)).total_seconds())
        # Check the timestamp is within limit.
        # if (now - ts) > settings.PASSWORD_RESET_TIMEOUT:
        #     currtoken.delete()
        #     return False


        file = fs.open(currToken.location)
        # invalidate it from db
        currToken.delete()
        return file

    def _make_token(self, currToken, timestamp):
        # timestamp is number of micro seconds since 2001-1-1. Converted to base 36,
        # this gives us a 10 digit string until about 2069.
        # if you dont call this overkill, then I really dont know what is - provides security even if this model gets compromised
        ts_b36 = int_to_base36(timestamp)
        hash_string = salted_hmac(
            self.key_salt,
            self._make_hash_value(currToken.bucket, currToken.location, timestamp),
            secret=self.secret,
            algorithm=self.algorithm,
        ).hexdigest()[::2]  # Limit to shorten the URL.
        return "%s-%s" % (ts_b36, hash_string)

    def _make_hash_value(self, bucket, file_location, timestamp):
        """
        Hash the user's primary key, email (if available), and some user state
        that's sure to change after a password reset to produce a token that is
        invalidated when it's used:
        1. The password field will change upon a password reset (even if the
           same password is chosen, due to password salting).
        2. The last_login field will usually be updated very shortly after
           a password reset.
        Failing those things, settings.PASSWORD_RESET_TIMEOUT eventually
        invalidates the token.

        Running this data through salted_hmac() prevents password cracking
        attempts using the reset token, provided the secret isn't compromised.
        """

        currRoot = path.join(STORAGE_ROOT, str(bucket.id))

        file_timestamp = FileSystemStorage(location=currRoot, base_url=None).get_accessed_time(file_location)

        # user's masterkey (bucket.owner.masterkey) can be added to invalidate on password change
        # file_timestamp can be replaced so that other tokens do not get invalidated on access - if replace, use file hash instead

        return f'{file_timestamp}{file_location}{bucket.owner_id}{bucket.id}{timestamp}'

file_token_generator = QuantumStorageTokenGenerator()