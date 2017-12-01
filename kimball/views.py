from django.shortcuts import get_object_or_404, render
from django.contrib.auth.decorators import login_required

from django.contrib.auth.models import User
from .models import StationStaff, Station, StationComponent, StationCheckpoint, Timebox, Edition, StationComponentTeamPoints

from django.utils import timezone


def index(request):
	return render(request, 'kimball/index.html')

def timeline(request):

	if 'edidion_id' in request.POST:
		edition_id = request.POST['edition_id']
		edition = Edition.objects.get(pk=edidion_id);
	else:
		edition = None

	editions = Edition.objects.all()

	if edition==None and editions.count()>0:
		edition = editions[0]

	if edition!=None:
		timeboxes = Timebox.objects.filter(edition=edition).order_by('start_date')
	else:
		timeboxes = []

	return render(request, 'kimball/timeline.html', {'edition': edition, 'editions':editions, 'timeboxes': timeboxes})

def scoreboard(request):
	return render(request, 'kimball/scoreboard.html')

@login_required
def team(request, team_id):
	return render(request, 'kimball/team.html', {'team_id': team_id})

@login_required
def station(request, station_id):
	return render(request, 'kimball/station.html', {'station_id': station_id})

@login_required
def checkpoint(request, checkin_code):


	return render(request, 'kimball/checkpoint.html', {'checkin_code': checkin_code})

@login_required
def report(request, station_id=None, checkin_code=None):

	if 'station_id' in request.POST:
		station_id = request.POST['station_id']
		station = Station.objects.get(pk=station_id)
	else:
		station = None

	if 'checkin_code' in request.POST:
		checkin_code = request.POST['checkin_code']
		checkpoint = StationCheckpoint.objects.filter(checkin_code=checkin_code)
	else:
		checkpoint = None

	# Obter os postos do utilizador e seleccionar o primeiro da lista
	staff_stations_ids = StationStaff.objects.filter(user=request.user).values_list('station_id').distinct()
	stations = Station.objects.filter(id__in=staff_stations_ids).order_by('start_date')
		

	if station == None and stations.count()>0:
		station = stations[0]

	if station != None:
		# Listar as equipas com checkin feito no respectivo posto
		checkpoints = StationCheckpoint.objects.filter(station=station).order_by('checkin')
	else:
		checkpoints = []

	if checkpoint == None and checkpoints.count()==1:
		checkpoint = checkpoints[0]

	if checkpoint != None:
		teampoints = StationComponentTeamPoints.objects.filter(checkpoint=checkpoint)
		if teampoints.count()==0:
			components = StationComponent.objects.filter(station=station)
			for component in components:
				c = StationComponentTeamPoints(component=component, checkpoint=checkpoint)
				c.save()

			teampoints = StationComponentTeamPoints.objects.filter(checkpoint=checkpoint)
		else:
			teampoints = []

	return render(request, 'kimball/report.html', {'stations': stations, 'checkpoints':checkpoints, 'station': station, 'checkpoint': checkpoint, 'teampoints':teampoints})
