from django.test import TestCase
from django.urls import reverse
from .models import Task
from django.contrib.auth.models import User
TEST_USERS = [
	'aaa',
	'eee',
	'iii',
	'ooo',
	'uuu',
]
TEST_PASS = 'kaskkask'
def check_create_users():
	users = []
	for name in TEST_USERS:
		user = User.objects.create_user(
			username=name
			)
		users.append(user)
	return users

class QueryTaskTests(TestCase):
	def test_404_on_missing(self):
		users = check_create_users()
		r = self.client.force_login(users[0])
		tasks = Task.objects.all().order_by('-id')
		max_id = 0
		if len(tasks) > 0:
			max_id = tasks[0].id
		max_id += 1
		test_views = ['details', 'edit', 'resolve', 'delete']
		for view in test_views:
			res = self.client.get(reverse(view,
			 	kwargs={'tid':max_id}))
			res.status_code
			self.assertEqual(res.status_code, 404,
				"on view {}, tid {}".format(view, max_id))
		return
	pass

class EditTaskTest(TestCase):
	pass