from django.conf.urls import url
# from django.contrib.auth.views import login
import django.contrib.auth.views as auth_views
from . import views

urlpatterns = [
	# url('^', auth_views.login),
	# url(r'^login', auth_views.login),
	url(r'^add', views.add, name='add'),
	url(r'^task/(?P<tid>[0-9]+)$', views.details, name='details'),
	url(r'^task/(?P<tid>[0-9]+)/resolve$', views.resolve, name='resolve'),
	url(r'^task/(?P<tid>[0-9]+)/delete$', views.delete, name='delete'),
	url(r'^task/(?P<tid>[0-9]+)/edit$', views.edit, name='edit'),
	url('', views.index, name='index'),

	# url('/task/<tid>', views.details_view, name='details')
	# url('/task/<tid>/resolve', views.resolve, name='resolve')
	# url('/task/<tid>/delete', views.delete, name='delete')
	# url('/task/<tid>/edit', views.edit, name='edit')
]

