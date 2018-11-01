from django.db import models
from django.forms import ModelForm
from django.contrib.auth.models import User
# Create your models here.

class Task(models.Model):
	'''
	Models a task assigned to a user.
	'''
	user = models.ForeignKey(User, on_delete=models.CASCADE)
	name = models.CharField(max_length=200)
	description = models.TextField(null=True)
	resolved = models.BooleanField(default=False)
	resolved_by = models.ForeignKey(
		User,
		related_name='res_by',
		null=True,
		on_delete=models.CASCADE
		)

	def __str__(self):
		return "{} {} [{}]".format(self.user, self.name, self.resolved)


class NewTaskForm(ModelForm):
    class Meta:
        model = Task
        fields = ['user', 'name', 'description']

class EditTaskForm(ModelForm):
    class Meta:
        model = Task
        fields = ['name', 'description', 'resolved']