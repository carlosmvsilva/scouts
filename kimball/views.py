from django.shortcuts import get_object_or_404, render, redirect

from django.contrib.auth import authenticate, login as login, logout

from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User

from django.utils import timezone
from django.utils.crypto import get_random_string

from django.urls import reverse

from .models import Team, StationStaff, Station, StationComponent, StationCheckpoint, Timebox, Edition, StationComponentTeamPoints, Scoreboard

from .forms import ContactForm, TeamPointsLineForm

from django.forms import inlineformset_factory

from django.core.mail import EmailMessage
from django.template import Context
from django.template.loader import get_template

def index(request):
	return render(request, 'kimball/index.html')

def contact(request):
	form_class = ContactForm

	if request.method == 'POST':
		form = form_class(data=request.POST)

		name = request.POST.get('name', '')
		sender = request.POST.get('sender', '')
		subject = request.POST.get('subject', '')
		message = request.POST.get('message', '')
		cc_myself = request.POST.get('cc_myself', False)

		if form.is_valid():
			template = get_template('kimball/contact_template.txt')
			context = Context({
				'contact_name': name,
				'contact_email': sender,
				'contact_subject': subject,
				'form_content': message,
			})
			content = template.render(context)
			email = EmailMessage(
				"Novo contacto via kimball app",
				content,
				"No Reply kimball <no-reply-kimball@escutismo.pt>",
				['kimball@escutismo.pt'],
				headers = {'Reply-To': sender }
			)
			email.send()
			return render(request, 'kimball/contact.html' )

	return render(request, 'kimball/contact.html', {'form': form_class} )

def login_view(request):
	if 'next' in request.POST:
		next_page = request.POST['next']
	else:
		next_page = reverse('index')
	if 'username' in request.POST and 'password' in request.POST:
		username = request.POST['username']
		password = request.POST['password']
		user = authenticate(request, username=username, password=password)
		if user is not None:
			login(request, user)
			return redirect(next_page)

	return render(request, 'kimball/login.html', {'next':next_page})

def logout_view(request):
	logout(request)
	return render(request, 'kimball/login.html')

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

	board = Scoreboard.objects.all()

	return render(request, 'kimball/scoreboard.html', {'board': board})

@login_required(login_url='/kimball/login')
def team(request, team_id):

	team = Team.objects.get(pk=team_id)

	return render(request, 'kimball/team.html', {'team': team})

@login_required(login_url='/kimball/login')
def station(request, station_id):
	return render(request, 'kimball/station.html', {'station_id': station_id})

@login_required(login_url='/kimball/login')
def checkin(request, checkin_code):
	checkpoints = StationCheckpoint.objects.filter(checkin_code=checkin_code,checkout__isnull=True)
	if checkpoints.count()==1:
		checkpoint = checkpoints[0]
		return report(request, checkpoint.station.id, checkin_code)
	elif checkpoints.count()>1:
		return checkpoint(request, checkin_code)
	else:
		staff_stations_ids = StationStaff.objects.filter(user=request.user).values_list('station_id').distinct()
		stations = Station.objects.filter(id__in=staff_stations_ids).order_by('start_date')
		if stations.count()==1:
			station = stations[0]
			patrol = Team.objects.filter(checkin_code=checkin_code)
			if patrol:
				checkpoint = StationCheckpoint(checkin_code=checkin_code, station=station, patrol=patrol, checkin=timezone.now(), checkedin_by=request.user)
				checkpoint.save()
				return report(request, station.id, checkin_code)
			else:
				erro = 'Equipa desconhecida!'
		elif stations.count()>1:
			erro = 'Escolha o posto...'
		else:
			erro = 'Posto desconhecido!'
	
		return render(request, 'kimball/checkin.html', {'erro': erro, 'stations': stations})

@login_required(login_url='/kimball/login')
def checkpoint(request, checkin_code):

	if 'station_id' in request.POST:
		station_id = request.POST['station_id']
		station = Station.objects.get(pk=station_id)
	else:
		station = None

	if station == None:
		staff_stations_ids = StationStaff.objects.filter(user=request.user).values_list('station_id').distinct()
		stations = Station.objects.filter(id__in=staff_stations_ids).order_by('start_date')	

		if stations.count()==1:
			station = stations[0]

	checkpoint = None
	if station:
		checkpoint = StationCheckpoint.objects.filter(station=station, checkin_code=checkin_code)
		if checkpoint==None:
			patrol = Team.objects.filter(checkin_code=checkin_code)
			checkpoint = StationCheckpoint(checkin_code=checkin_code, station=station, patrol=patrol, checkin=timezone.now(), checkedin_by=request.user)
			checkpoint.save()

	if checkpoint:
		return report(request, checkpoint.station.id, checkpoint.checkin_code)
	else:
		return render(request, 'kimball/checkpoint.html', {'checkin_code': checkin_code, 'stations':stations})

@login_required(login_url='/kimball/login')
def report(request, station_id=None, checkin_code=None):

	PointsFormSet = inlineformset_factory(StationCheckpoint, StationComponentTeamPoints, form=TeamPointsLineForm, fields=('component', 'points', 'notes',), extra=0, can_delete=False)

	if request.method == 'POST':
		if 'checkin_code' in request.POST:
			checkin_code = request.POST['checkin_code']
			checkpoint = StationCheckpoint.objects.filter(checkin_code=checkin_code,checkout__isnull=True)
			teampoints = PointsFormSet(request.POST, request.FILES, instance=checkpoint)
			if teampoints.is_valid():
				teampoints.save()
				
			return checkpoint(request, None)
		else:
			checkpoint = None

		if 'station_id' in request.POST:
			station_id = request.POST['station_id']
			station = Station.objects.get(pk=station_id)
		else:
			station = None
	else:
		checkpoint = None
		station = None

	staff_stations_ids = StationStaff.objects.filter(user=request.user).values_list('station_id').distinct()
	stations = Station.objects.filter(id__in=staff_stations_ids).order_by('start_date')	

	if station == None and stations.count()>0:
		station = stations[0]

	if station != None:
		checkpoints = StationCheckpoint.objects.filter(station=station,checkout__isnull=True).order_by('checkin')
	else:
		checkpoints = []

	if checkpoint == None and checkpoints.count()==1:
		checkpoint = checkpoints[0]

	if checkpoint != None:
		start_points(station, checkpoint)
		teampoints = PointsFormSet(instance=checkpoint)
	else:
		teampoints = None

	return render(request, 'kimball/report.html', {'stations': stations, 'checkpoints':checkpoints, 'station': station, 'checkpoint': checkpoint, 'teampoints':teampoints})

def start_points(station, checkpoint):
	if not StationComponentTeamPoints.objects.filter(checkpoint=checkpoint).exists():
		components = StationComponent.objects.filter(station=station, parent__isnull=True)
		for component in components:
			start_component_points(component, checkpoint)

def start_component_points(component, checkpoint):
	c = StationComponentTeamPoints(component=component, checkpoint=checkpoint)
	c.save()
	children = StationComponent.objects.filter(station=station, parent=component)
	for child in children:
		start_component_points(component, checkpoint)

@login_required(login_url='/kimball/login')
def checkout(request, checkpoint_id):

	failed = False
	msg = 'Checkout feito com sucesso'

	checkpoint = StationCheckpoint.objects.get(pk=checkpoint_id)

	points = StationComponentTeamPoints.objects.filter(checkpoint=checkpoint)
	components = StationComponent.objects.filter(station=checkpoint.station)

	if points.count()>100:
		
		if checkpoint.checkout__isnull==True:
			failed = True
			msg = 'Ja foi feito checkout neste posto para esta equipa'
		else:

			checkpoint.checkout = timezone.now()
			checkpoint.checkedout_by = request.user
			checkpoint.save()

			team = checkpoint.patrol
			team.checkin_code = get_random_string(length=32)
			team.save()
		
	else:
		failed = True
		msg = 'Checkout falhou!'


	return render(request, 'kimball/checkout.html', {'failed': failed, 'msg': msg})
