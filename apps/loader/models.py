from django.db import models
from django.contrib.auth.models import User
from crypto_tax_checker import settings
import os

def user_directory_path(instance, filename):
	instance.original_filename = filename
	newfilename = f"{instance.user.username}_{instance.user.id}_{filename}"
	# file will be uploaded to MEDIA_ROOT/user_<id>/<filename>
	return os.path.join(settings.MEDIA_ROOT,"user_files", filename)

def user_directory_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/username_user_<id>/<filename>
    return 'user_files/{0}_user_{1}/{2}'.format(instance.user.username, instance.user.id, filename)

class Historyfile(models.Model):
	user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
	upload_file = models.FileField(default="none.csv", upload_to=user_directory_path)

	# def save(self, *args, **kwargs):
    # 	randomNum = random.randint(1000000,9000000)
    # 	new_name = str(self.user.username) + str(randomNum) + ".csv"
    # 	self.upload_file.name = new_name
    # 	super(Document, self).save(*args, **kwargs)

	# def user_directory_path(self, filename):
	# 	# file will be uploaded to MEDIA_ROOT/user_<id>/<filename>
	# 	return 'user_{0}/{1}'.format(self.user.id, filename)
