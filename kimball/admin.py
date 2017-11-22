from django.contrib import admin

from .models import Edition, Team, Role, TeamMember, Timebox, Station, StationStaff, StationComponent, StationCheckpoint, StationComponentTeamPoints

# Define Forms for models
class EditionAdmin(admin.ModelAdmin):
	list_display = ('name', 'start_date', 'end_date', 'info_url')
	fieldsets = [
        (None, {'fields': ['name']}),
        ('Dates', {'fields': ['start_date','end_date']}),
        (None, {'fields': ['info_url']}),
    ]
	list_filter = ['start_date']
	search_fields = ['name', 'start_date', 'end_date']

class TeamMemberInline(admin.TabularInline):
	model = TeamMember
	extra = 5

class TeamAdmin(admin.ModelAdmin):
	list_filter = ['group_number']
	list_display = ('name', 'group_number', 'group_name', 'edition')	
	search_fields = ['name', 'group_number', 'group_name', 'edition']
	inlines = [TeamMemberInline]

class TeamMemberAdmin(admin.ModelAdmin):
	list_filter = ['role']
	list_display = ('nin', 'name', 'role', 'team', 'user')
	search_fields = ['nin', 'name', 'team', 'user']

class TimeboxAdmin(admin.ModelAdmin):
	list_filter = ['start_date']
	list_display = ('name', 'description', 'info_url', 'start_date', 'end_date', 'edition')	
	search_fields = ['name', 'description', 'start_date', 'end_date', 'edition']


# Register your models here.
admin.site.register(Edition, EditionAdmin)
admin.site.register(Team, TeamAdmin)
admin.site.register(Role)
admin.site.register(TeamMember, TeamMemberAdmin)
admin.site.register(Timebox, TimeboxAdmin)
admin.site.register(Station)
admin.site.register(StationStaff)
admin.site.register(StationComponent)
admin.site.register(StationCheckpoint)
admin.site.register(StationComponentTeamPoints)