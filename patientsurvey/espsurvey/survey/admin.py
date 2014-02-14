'''
                              ESP Health Project
                     Electronic Medical Records Warehouse
                         Admin Interface Configuration

@authors: Jason McVetta <jason.mcvetta@gmail.com>
@organization: Channing Laboratory http://www.channing.harvard.edu
@copyright: (c) 2009 Channing Laboratory
@license: LGPL
'''


from django.contrib import admin

from espsurvey.survey.models import Participant
from espsurvey.survey.models import ParticipantActivity
from espsurvey.survey.models import Survey
from espsurvey.survey.models import QuestionGroup
from espsurvey.survey.models import Response
from espsurvey.survey.models import Question

class ParticipantAdmin(admin.ModelAdmin):
    list_display = ['id', 'login']
    search_fields = ['login']

class ParticipantActivityAdmin(admin.ModelAdmin):
    list_display = ['id', 'survey', 'participant']
    raw_id_fields = ['participant']
    search_fields = ['survey']

class SurveyAdmin(admin.ModelAdmin):
    list_display = ['id', 'name']
    list_display_links = ['id']
    search_fields =  ['name']

class QuestionGroupAdmin(admin.ModelAdmin):
    list_display = ['id', 'survey', 'text']
    raw_id_fields = ['survey']
    search_fields =  ['text']
    
class ResponseAdmin(admin.ModelAdmin):
    list_display = ['id', 'participant', 'survey' ]
    list_display_links = ['id']
    raw_id_fields = ['survey', 'participant']
    search_fields =  ['participant', 'survey' ]
    ordering = ['participant']

class QuestionAdmin(admin.ModelAdmin):
    list_display = ['id', 'short_name' ]
    list_display_links = ['id']
    raw_id_fields = ['question_group']
    search_fields =  ['short_name']
    ordering = ['question_group']

admin.site.register(Participant, ParticipantAdmin)
#admin.site.register(ParticipantActivity, ParticipantActivityAdmin)
admin.site.register(Survey,SurveyAdmin)
admin.site.register(QuestionGroup, QuestionGroupAdmin)
#admin.site.register(Response, ResponseAdmin)
admin.site.register(Question, QuestionAdmin)
