import os
import sys

if __name__ == "__main__":
	os.environ.setdefault("DJANGO_SETTINGS_MODULE", "origin.settings")
	import django
	django.setup()
	from django.contrib.auth.models import User
	from django.core.exceptions import ObjectDoesNotExist

	users = min(10,int(sys.argv[1]))
	password = sys.argv[2]
	for uid in range(0,users):
		username="user{}".format(uid)
		try:
			User.objects.get(username=username)
		except ObjectDoesNotExist:
			user = User.objects.create_user(
				username=username,
				password=password
				)
			user.is_superuser = True
			user.is_staff = True
			user.save()
			print ("created user ", user)
