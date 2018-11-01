from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.shortcuts import redirect
from django.http import HttpResponse
from django.urls import reverse

from .models import NewTaskForm
from .models import EditTaskForm
from .models import Task

from .helpers import get_task
from .helpers import task_missing
from .helpers import aok
from .helpers import error

from . import UMESSAGES as um

@login_required
def index(request, include_done=True):
	'''
	[View] - Render all Tasks
	- test: include_done

	'''
	if include_done == True:
		tasks = Task.objects.all().order_by('-id')
	else:
		tasks = Task.objects.filter(resolved=True).order_by('-id')

	return render(request, 'tasks/index.html', {'tasks' : tasks})

@login_required
def add(request):
	'''
	[View] - Create a Task

	- GET: renders an empty NewTaskForm
	- POST: creates the task, if successful, redirects to index.
		- test: a valid Task is created. 403 otherwise
		- test: task's user is the one creating. 403 otherwise
		- test: requesting user exists. 403 otherwise
		- test: on success, redirected to index

	'''
	if request.method == "GET":
		context = {'form' : NewTaskForm()}
		return render(request, 'tasks/form.html', context)

	if request.method == "POST":
		targs = {}
		for key in NewTaskForm.Meta.fields:
			targs[key] = request.POST.get(key)
		try:
			uid = targs['user'][0]
			targs['user'] = User.objects.get(id=uid)
		except ObjectDoesNotExist:
			return error(request, um.get("user_missing"), retry_view='add')

		newtask = Task(**targs)
		newtask.save()
		# return aok(request, "Created task {}".format(newtask.id))
		return redirect(index)

	return HttpResponse(status=405)

@login_required
@get_task
def details(request, tid, task=None):
	'''
	[View] - renders a Task content
	- test: non existent Task returns 404
	'''
	if task is None:
		return task_missing(request, tid)
	return render(request, 'tasks/details.html', {'task': task})

@login_required
@get_task
def edit(request, tid, task=None):
	'''
	[View] - Edit a Task
	- GET: renders the task as a EditTaskForm
		- test: non existent Task returns 404
	- POST: Edits the task. On sucess, redirects to details view
		- test: non existent Task returns 404
		- test: A user is allowed to edit only its own Tasks.->403
		- test: Only fields from EditTaskForm can be edited. ->401
		- test: When editing 'resolved' state:
			- if resolving an already resolved: 'resolved_by' should not change.
			- else if resolving, the 'resolved_by' user changes to the editor's
			- if unresolving, resolved_by should be set to None
	'''

	if task is None:
		return task_missing(request, tid)

	if task.user != request.user:
		return error(request, um.get('edit_diff_user'))


	if request.method == "GET":
		context = {
			'form' : EditTaskForm(instance=task)
		}
		return render(request, 'tasks/form.html', context)

	if request.method == "POST":
		targs = {}
		current_state = False
		if task.resolved == True:
			current_state = True
		_resolved = False
		for key in EditTaskForm.Meta.fields:
			_value = request.POST.get(key)
			if key == 'resolved':
				if _value == 'on':
					_value = True
					_resolved = True
				else:
					_value = False

			setattr(task, key, _value)

		if _resolved == True and current_state == False:
			setattr(task, 'resolved_by', request.user)
		task.save()
		# return aok(request, "Created task {}".format(newtask.id))
		return redirect(details, tid=tid)

	return HttpResponse(status=405)

@login_required
@get_task
def resolve(request, tid, task=None):
	'''
	[View] : Changed the 'resolved' status of a Task. Set the
	resolved_by to the requesting user.
		- test: non existent Task returns 404
		- test: any user is allowed to resolve any Task
		- test: do not alter already resolved Tasks.
	'''
	#renders a filled task form
	if task is None:
		return task_missing(request, tid)
	if task.resolved == True:
		#test: prevent resolving, thus changing resloving user.
		return redirect(index)

	task.resolved = True
	task.resolved_by = request.user
	task.save()
	# return aok(request, "You marked task {} done".format(tid))
	return redirect(index)

@login_required
@get_task
def delete(request, tid, task=None):
	'''
	[View] : Delete a task
		- test: non existent Task returns 404
		- test: only Task user is allowed to delete -> 403
	'''
	if task is None:
		return task_missing(request, tid)

	if task.user != request.user:
		return error(request, um.get('delete_diff_user'))

	task.delete()
	# return aok(request, "Task {} deleted".format(tid))
	return redirect(index)


# def task_action(request, tid, action):
# 	# data = {
# 	# 	'tid' : tid
# 	# 	'message' : 'did {}'.format(action)
# 	# 	'error' : 'failed doing {}'.format(action)
# 	# }

# 	# if action == 'resolve':
# 	# 	return render(request, "tasks/action_dialog.html")
# 	# if action == 'delete':
# 	# 	return render(request, "tasks/action_dialog.html")
# 	# if action == 'edit':
# 	# 	return render(request, "tasks/action_dialog.html")

# 	return render(request, "tasks/action_dialog.html")

