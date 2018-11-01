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
] # at least 3 users required.

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

	def test_edit_only_own(self):
		users = get_create_users()
		self.client.force_login(users[0])
		for user in users:
			#create a task per user, assigned to
			#the user.
			_test_id = generate_test_id()
			_uid = user.id
			_name = "crud_test_name_{}".format(_test_id)
			_desc = "crud_test_desc_{}".format(_test_id)

			res = self.client.post(reverse('add'), {
				'user' : _uid,
				'name' : _name,
				'description' : _desc
				})
			self.assertEqual(res.status_code, 302)

		for user in users:
			self.client.force_login(user)
			utasks = Task.objects.filter(user=user)
			assert len(utasks) > 0
			self._edit_tasks(utasks, assert_code=302, msg="can only edit own")

			otasks = Task.objects.exclude(user=user)
			assert len(otasks) > 0
			self._edit_tasks(otasks, assert_code=403, msg="can not edit others")

	def test_task_resolution(self):
		users = get_create_users()

		#change to USER 0
		self.client.force_login(users[0])
		_test_id = generate_test_id()
		_uid = users[0].id
		_name = "crud_test_name_{}".format(_test_id)
		_desc = "crud_test_desc_{}".format(_test_id)

		#create the task
		res = self.client.post(reverse('add'), {
			'user' : _uid,
			'name' : _name,
			'description' : _desc
			})
		self.assertEqual(res.status_code, 302)

		#get the last task created
		latest = get_last_added_task()

		# as USER 1, mark the task resolved
		self.client.force_login(users[1])
		self.client.get(reverse('resolve', kwargs={'tid':latest.id}) )
		latest = Task.objects.get(id=latest.id)
		self.assertTrue(latest.resolved,
			"did not resolved the task")
		self.assertEqual(latest.resolved_by, users[1],
			"resolved_by does not match")

		# as USER 2, re-resolve the Task
		self.client.force_login(users[2])
		self.client.get(reverse('resolve', kwargs={'tid':latest.id}) )
		latest = Task.objects.get(id=latest.id)
		self.assertTrue(latest.resolved,
			"re-resolving toggled state")

		self.assertEqual(latest.resolved_by, users[1],
			"re-resolving modified user")

		#As the original USER 0, un-resolve the task
		self.client.force_login(users[0])
		self._edit_tasks([latest], set_resolve=False, assert_code=302)
		latest = Task.objects.get(id=latest.id)
		self.assertFalse(latest.resolved,
			"un-resolving failed")
		self.assertIsNone(latest.resolved_by,
			"un-resolving did not clear resolved_by field")


	def _edit_tasks(self, tasks, set_resolve=None, assert_code=403, msg=None):
		for task in tasks:
			_name = "{}__edited".format(task.description)
			_description =  "{}__edited".format(task.description)
			resolve = task.resolved
			if set_resolve is not None:
				resolve = set_resolve

			res = self.client.post(
				reverse('edit', kwargs={'tid':task.id}),
				{
					'name' : _name,
					'descripton' : _description,
					'user' : task.user.id,
					'resolved' : resolve,
				})
			self.assertEqual(res.status_code, assert_code, msg)



	pass