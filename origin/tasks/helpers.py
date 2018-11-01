from .models import Task
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render
from django.shortcuts import render
from django.shortcuts import redirect
from django.http import HttpResponse
from django.urls import reverse

from . import UMESSAGES as um
def get_task(function):
	'''
	Decorator that adds a Task instance for Views receiving
	a task id (tid).
	Passes the task as the kwarg 'task'
	'''
	def wrap_function(*args, **kwargs):
		tid = kwargs.get('tid')
		if tid is not None:
			kwargs['task'] = None
			try:
				kwargs['task'] = Task.objects.get(id=tid)
			except ObjectDoesNotExist:
				pass
		return function(*args, **kwargs)
	return wrap_function

def task_missing(request, tid):
	return error(request, um.get("task_404"), status=404)

def aok(request, message):
	return render(request, 'tasks/dialog.html', {
		'message' : message
		})

def error(request, message, retry_view=None, status=403):
	ctx = {
		'error' : message
	}
	if retry_view is not None:
		ctx['cancel_url'] = reverse("index")

	return render(request, 'tasks/dialog.html', ctx, status=status)
