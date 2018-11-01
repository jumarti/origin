import random
import hashlib
from django.test import TestCase
from django.urls import reverse
from django.core.exceptions import ObjectDoesNotExist

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
def get_create_users():
	users = []
	for name in TEST_USERS:
		try:
			user = User.objects.get(username=name)
		except ObjectDoesNotExist:
			user = User.objects.create_user(
				username=name
				)
		users.append(user)
	return users

def get_tasks():
	return Task.objects.all().order_by('-id')

def get_last_added_task():
	tasks = get_tasks()
	if len(tasks) == 0:
		return None
	return tasks[0]

def generate_test_id():
	m = hashlib.md5()
	m.update("{}".format(random.randint(0,1000)).encode())
	return m.hexdigest()[0:4]


class QueryTaskTests(TestCase):
	def test_404_on_missing(self):
		users = get_create_users()
		self.client.force_login(users[0])
		tasks = get_tasks()
		max_id = 0
		latest = get_last_added_task()
		if latest is not None:
			max_id = latest.id

		max_id += 1
		test_views = ['details', 'edit', 'resolve', 'delete']
		for view in test_views:
			res = self.client.get(reverse(view,
			 	kwargs={'tid':max_id}))
			res.status_code
			self.assertEqual(res.status_code, 404,
				"on view {}, tid {}".format(view, max_id))
		return


class CRUDTaskTest(TestCase):

	def test_add_creates_valid_task(self):
		users = get_create_users()
		self.client.force_login(users[0])
		_uid = users[1].id
		_test_id = generate_test_id()
		_name = "crud_test_name_{}".format(_test_id)
		_desc = "crud_test_desc_{}".format(_test_id)
		res = self.client.post(reverse('add'), {
			'user' : _uid,
			'name' : _name,
			'description' : _desc
			})

		self.assertEqual(res.status_code, 302)
		latest = get_last_added_task()
		self.assertIsNotNone(latest)
		self.assertEqual(latest.name, _name)
		self.assertEqual(latest.description, _desc)
		self.assertEqual(latest.user.id, _uid)
		self.assertFalse(latest.resolved)
		self.assertIsNone(latest.resolved_by)

	def test_add_missing_assignee_user_fails(self):
		users = get_create_users()
		self.client.force_login(users[0])
		_uid = users[1].id
		User.objects.get(id=_uid).delete()

		_test_id = generate_test_id()
		_name = "crud_test_name_{}".format(_test_id)
		_desc = "crud_test_desc_{}".format(_test_id)
		res = self.client.post(reverse('add'), {
			'user' : _uid,
			'name' : _name,
			'description' : _desc
			})


		self.assertEqual(res.status_code, 403)

	def test_task_get(self):
		users = get_create_users()
		self.client.force_login(users[0])
		latest = get_last_added_task()
		if latest is None:
			_test_id = generate_test_id()
			_uid = users[0].id
			_name = "crud_test_name_{}".format(_test_id)
			_desc = "crud_test_desc_{}".format(_test_id)
			res = self.client.post(reverse('add'), {
				'user' : _uid,
				'name' : _name,
				'description' : _desc
				})
			self.assertEqual(res.status_code, 302)

		latest = get_last_added_task()
		res = self.client.get(reverse('details',
			kwargs={'tid':latest.id}))
		self.assertEqual(res.status_code, 200)

		res = self.client.get(reverse('details',
			kwargs={'tid':latest.id + 1}))

		self.assertEqual(res.status_code, 404)

	pass