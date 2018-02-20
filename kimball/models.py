from __future__ import unicode_literals

from django.contrib.auth.models import User
from django.db import models

class Edition(models.Model):
	name = models.CharField(max_length=200)
	start_date = models.DateTimeField('start date')
	end_date = models.DateTimeField('end date')
	info_url = models.CharField(max_length=200)

	def __unicode__(self):
		return self.name

class Team(models.Model):
	edition = models.ForeignKey(Edition)
	name = models.CharField(max_length=200)
	group_number = models.PositiveIntegerField()
	group_name = models.CharField(max_length=200)
	locale = models.CharField(max_length=100, default='-')
	checkin_code = models.CharField(max_length=32)

	def __unicode__(self):
		return self.name + ' (' + unicode(self.group_number) + ' - ' + self.group_name + ')'

class Role(models.Model):
	name = models.CharField(max_length=50)

	def __unicode__(self):
		return self.name

class TeamMember(models.Model):
	team = models.ForeignKey(Team)
	role = models.ForeignKey(Role)
	name = models.CharField(max_length=200)
	nin = models.CharField(max_length=13, unique=True)
	user = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True)

	class Meta:
		unique_together = ('team', 'user')

	def __unicode__(self):
		return self.name + ' (' + self.role.name + ')'

class Timebox(models.Model):
	edition = models.ForeignKey(Edition)
	name = models.CharField(max_length=200)
	description = models.CharField(max_length=500)
	info_url = models.CharField(max_length=200)
	start_date = models.DateTimeField('start date')
	end_date = models.DateTimeField('end date')

	def __unicode__(self):
		return self.name

class Station(models.Model):
	timebox = models.ForeignKey(Timebox)
	name = models.CharField(max_length=200)
	description = models.CharField(max_length=500)
	start_date = models.DateTimeField('start date')
	end_date = models.DateTimeField('end date')
	lat = models.DecimalField(max_digits=10,decimal_places=8, blank=True, null=True)
	lng = models.DecimalField(max_digits=11,decimal_places=8, blank=True, null=True)

	def __unicode__(self):
		return self.name

class StationStaff(models.Model):
	station = models.ForeignKey(Station)
	user = models.ForeignKey(User)

	class Meta:
		unique_together = ('station', 'user')

	def __unicode__(self):
		return unicode(self.user) + ' em ' + unicode(self.station)

class ComponentGroup(models.Model):
	name = models.CharField(max_length=200)
	max_points = models.PositiveIntegerField()

	def __unicode__(self):
		return self.name

class StationComponent(models.Model):
	station = models.ForeignKey(Station)
	parent = models.ForeignKey('self', on_delete=models.SET_NULL, blank=True, null=True)
	name = models.CharField(max_length=200)
	description = models.CharField(max_length=500)
	max_points = models.PositiveIntegerField()
	show_on_details = models.BooleanField()
	group = models.ForeignKey(ComponentGroup, on_delete=models.SET_NULL, blank=True, null=True)

	def __unicode__(self):
		return unicode(self.station) + ('' if self.parent is None else ' - ' + self.parent.name) + ' - ' + self.name

	def as_tree(self):
		children = list(self.parent_set.all())
		branch = bool(children)
		yield branch, self
		for child in children:
			for next in child.as_tree():
				yield next
		yield branch, None

	def is_leef(self):
		return count(self.parent_set.all())==0

class StationCheckpoint(models.Model):
	checkin_code = models.CharField(max_length=32, unique=True)
	station = models.ForeignKey(Station)
	patrol = models.ForeignKey(Team)
	checkin = models.DateTimeField('checkin')
	checkedin_by = models.ForeignKey(User, related_name='checkedin_by')
	checkout = models.DateTimeField('chekout', blank=True, null=True)
	checkedout_by = models.ForeignKey(User, related_name='checkedout_by', on_delete=models.SET_NULL, blank=True, null=True)

	class Meta:
		unique_together = ('station', 'patrol')

	def __unicode__(self):
		return unicode(self.station) + ' - ' + self.patrol.name +' ('+unicode(self.patrol.group_number)+')'

class StationComponentTeamPoints(models.Model):
	component = models.ForeignKey(StationComponent)
	checkpoint = models.ForeignKey(StationCheckpoint)
	points = models.PositiveIntegerField(default=0)
	notes = models.CharField(max_length=500, blank=True, null=True)

	class Meta:
		unique_together = ('component', 'checkpoint')

	def __unicode__(self):
		return unicode(self.checkpoint) + ' - '+self.component.name

	def as_tree(self):
		children = list(self.component.children.all())
		branch = bool(children)
		yield branch, self
		for child in children:
			child_component = StationComponentTeamPoints.objects.filter(component=child, checkpoint=self.checkpoint)
			for next in child_component.as_tree():
				yield next
		yield branch, None

class Scoreboard(models.Model):
	id = models.BigIntegerField(primary_key=True)
	team = models.ForeignKey(Team, on_delete=models.DO_NOTHING)
	points = models.PositiveIntegerField(default=0)

	class Meta:
		managed = False
		db_table = 'kimball_scoreboard_v'