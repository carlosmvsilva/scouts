from django.contrib import admin

from .models import Edition, Team, Role, TeamMember, Timebox, Station, StationStaff, ComponentGroup, StationComponent, StationCheckpoint, StationComponentTeamPoints

# Define Forms for models
class TimeboxInline(admin.TabularInline):
	model = Timebox
	extra = 1

class EditionAdmin(admin.ModelAdmin):
	list_display = ('name', 'start_date', 'end_date', 'info_url')
	fieldsets = [
        (None, {'fields': ['name']}),
        ('Dates', {'fields': ['start_date','end_date']}),
        (None, {'fields': ['info_url']}),
    ]
	list_filter = ['start_date']
	search_fields = ['name', 'start_date', 'end_date']
	inlines = [TimeboxInline]

class TeamMemberInline(admin.TabularInline):
	model = TeamMember
	extra = 1

class TeamAdmin(admin.ModelAdmin):
	list_filter = ['group_number', 'locale']
	list_display = ('name', 'group_number', 'group_name', 'locale', 'edition')	
	search_fields = ['name', 'group_number', 'group_name', 'locale', 'edition']
	inlines = [TeamMemberInline]

class TeamMemberAdmin(admin.ModelAdmin):
	list_filter = ['role']
	list_display = ('nin', 'name', 'role', 'team', 'user')
	search_fields = ['nin', 'name', 'team', 'user']

class StationInline(admin.TabularInline):
	model = Station
	extra = 1

class TimeboxAdmin(admin.ModelAdmin):
	list_filter = ['start_date']
	list_display = ('name', 'description', 'info_url', 'start_date', 'end_date', 'edition')	
	search_fields = ['name', 'description', 'start_date', 'end_date', 'edition']
	inlines = [StationInline]

class StationStaffInline(admin.TabularInline):
	model = StationStaff
	extra = 1

class StationComponentInline(admin.TabularInline):
	model = StationComponent
	extra = 1

class StationAdmin(admin.ModelAdmin):
	list_filter = ['start_date']
	list_display = ('name', 'description', 'lat', 'lng', 'start_date', 'end_date', 'timebox')
	search_fields = ['name', 'description', 'start_date', 'end_date', 'timebox']
	inlines = [StationStaffInline, StationComponentInline]

class StationStaffAdmin(admin.ModelAdmin):
	list_filter = ['station']
	list_display = ('station', 'user')
	search_fields = ['station', 'user']

class StationComponentAdmin(admin.ModelAdmin):
	list_filter = ['station']
	list_display = ('station', 'parent', 'name', 'description', 'max_points', 'show_on_details')
	search_fields = ['station', 'parent', 'name', 'description', 'max_points', 'show_on_details']


class StationTeamPointsInline(admin.TabularInline):
	model = StationComponentTeamPoints
	extra = 1

class StationCheckpointAdmin(admin.ModelAdmin):
	list_filter = ['station']
	list_display = ('station', 'patrol', 'checkin', 'checkedin_by', 'checkout', 'checkedout_by')
	search_fields = ['station', 'patrol']
	inlines = [StationTeamPointsInline]

class StationComponentTeamPointsAdmin(admin.ModelAdmin):
	list_filter = ['checkpoint']
	list_display = ('checkpoint', 'component', 'points', 'notes')
	search_fields = ['checkpoint', 'component', 'notes']

class ComponentGroupAdmin(admin.ModelAdmin):
	list_display = ('name', 'max_points')
	search_fields = ['name', 'max_points']


# Register your models here.
admin.site.register(Edition, EditionAdmin)
admin.site.register(Team, TeamAdmin)
admin.site.register(Role)
# admin.site.register(TeamMember, TeamMemberAdmin)
admin.site.register(Timebox, TimeboxAdmin)
admin.site.register(Station, StationAdmin)
# admin.site.register(StationStaff, StationStaffAdmin)
# admin.site.register(StationComponent, StationComponentAdmin)
admin.site.register(StationCheckpoint, StationCheckpointAdmin)
# admin.site.register(StationComponentTeamPoints, StationComponentTeamPointsAdmin)
admin.site.register(ComponentGroup, ComponentGroupAdmin)