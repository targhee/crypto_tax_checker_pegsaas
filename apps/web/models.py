from django.db import models
from django.contrib.auth.models import User
from crypto_tax_checker import settings
import os

def user_directory_path(instance, filename):
	# file will be uploaded to MEDIA_ROOT/username_user_<id>/<filename>
    #return 'user_files/{0}_user_{1}/{2}'.format(instance.user.username, instance.user.id, filename)
	return f'user_files/user_{instance.user.id}/{filename}'

class Historyfile(models.Model):
	user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
	upload_file = models.FileField(default="none.csv", upload_to=user_directory_path)
