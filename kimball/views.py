from django.shortcuts import get_object_or_404, render
from django.contrib.auth.decorators import login_required

from django.contrib.auth.models import User
from .models import StationStaff, Station, StationCheckpoint

def index(request):
	return render(request, 'kimball/index.html')

def timeline(request):
	return render(request, 'kimball/timeline.html')

def scoreboard(request):
	return render(request, 'kimball/scoreboard.html')

@login_required
def team(request, team_id):
	return render(request, 'kimball/team.html', {'team_id': team_id})

@login_required
def station(request, station_id):
	return render(request, 'kimball/station.html', {'stage_id': station_id})

@login_required
def checkpoint(request, checkin_code):
	return render(request, 'kimball/checkpoint.html', {'checkin_code': checkin_code})

@login_required(login_url='/kimball/admin/login/')
def report(request, station_id=0, checkin_code=''):

	stations = []
	checkpoints = []

	if station_id == 0:
		# Obter os postos do utilizador e seleccionar o primeiro da lista
		staff_stations_ids = StationStaff.objects.filter(user=request.user).value_list('station_id').distinct()
		stations = Station.object.filter(id__in=staff_stations_ids)

		if stations.count()>0:
			station = stations[0]
		else:
			# lancar mensagem de erro a dizer que o utilizador nao esta alocado a nenhum posto
			raise Http404("Utilizador sem postos alocados")

	if checkin_code == '':
		# Listar as equipas com checkin feito no respectivo posto
		checkpoints = StationCheckpoint.objects.filter(station=station).order_by('checkin')
	else:
		# abrir o relatorio da equipa / chechpoint respectivo
		checkpoints = get_object_or_404(StationCheckpoint, checkin_code=checkin_code)

	return render(request, 'kimball/report.html', {'stations': stations, 'checkpoints':checkpoints})
