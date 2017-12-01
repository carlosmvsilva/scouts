from django.conf.urls import include, url
from django.contrib import admin

from . import views

urlpatterns = [
	url(r'^$', views.index, name='index'),
	url(r'^timeline/$', views.timeline, name='timeline'),
	url(r'^scoreboard/$', views.scoreboard, name='scoreboard'),
	url(r'^team/(?P<team_id>\d+)/$', views.team, name='team'),
	url(r'^station/(?P<station_id>\d+)/$', views.station, name='station'),
	url(r'^checkpoint/(?P<checkin_code>\.*)/$', views.checkpoint, name='checkpoint'),
	url(r'^report/', include([
		url(r'^$', views.report, name="report"),
		url(r'(?P<station_id>\d+)/', include([
			url(r'^$', views.report, name="report"),
			url(r'(?P<checkin_code>\.*)/$', views.report, name="report"),
		])),
	])),
]