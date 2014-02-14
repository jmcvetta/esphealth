'''
                              ESP Health Project
                     Electronic Medical Records Warehouse
                                  Data Models

@authors: Jason McVetta <jason.mcvetta@gmail.com>, Raphael Lullis <raphael.lullis@gmail.com>
@organization: Channing Laboratory - http://www.channing.harvard.edu
@contact: http://esphealth.org
@copyright: (c) 2009-2011 Channing Laboratory
@license: LGPL 3.0 - http://www.gnu.org/licenses/lgpl-3.0.txt
'''



from django.db import models


YES_NO_UNSURE = [  ('Y', 'Yes'),('N', 'No') ,('U','Unsure' ) ]

WEIGHT_TYPE = [('L','Low'),('N', 'Normal'), ('OW','Overweight'), ('OB','Obese') ]

DIABETES_TYPE = [  ('PRE','Pre-diabetes'),('T1', 'Type 1 Diabetes'), ('T2','Type 2 Diabetes'),('GDM', 'Gestational Diabetes')]

RACE = [('B','Black'), ('W','White'), ('A','Asian'), ('H','Hispanic'), ('O','Other')]

GENDER = [('M','Male'),('F','Female')]

UNSURE = [('on','True' ), ('False','False' ) ]
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#
# Models
#
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class Participant(models.Model):
    login = models.CharField('login  - mrn',max_length=50, blank=False, db_index=True)
    authtokenDigest =  models.CharField('auth token digest',max_length=50, blank=False, db_index=True)

    def __str__(self):
        return '%s | %s ' % (self.id, self.login )

class Survey(models.Model):
    name =  models.CharField('Survey name',max_length=100, blank=False, db_index=True)
    #perhaps deadline or other fields in general for the survey

    def __str__(self):
        return '%s  ' % (self.id  )

class ParticipantActivity(models.Model):
    survey = models.ForeignKey(Survey, blank=False, null=False) 
    participant = models.ForeignKey(Participant, blank=False, null=False) 
    completed = models.BooleanField('completed', blank=False, default=False, db_index=False)
    completion_date = models.DateTimeField(auto_now_add=True, blank=False)

    def __str__(self):
        return '%s | %s | %s' % ( self.id, self.survey.id , self.participant.login)


class QuestionGroup(models.Model):
    survey = models.ForeignKey(Survey, blank=True, null=True) 
    seq = models.IntegerField('sequence', null=True, default=0)
    text =  models.CharField('question group text',max_length=100, blank=False, db_index=True)

    def __str__(self):
        return '%s | %s | %s' % (self.id, self.survey.id , self.text)

class Question(models.Model):
    question_group = models.ForeignKey(QuestionGroup, blank=True, null=True) 
    short_name = models.CharField('short name',max_length=20, blank=False, db_index=False)
    type = models.IntegerField('question type', null=True, default=0)
    inline = models.BooleanField('inline', blank=False, default=False, db_index=False)
    conditional = models.BooleanField('conditional', blank=False, default=False, db_index=False)
    # TODO ? do we want multiple responses or only one value
    conditional_response = models.CharField('conditional response',max_length=20, blank=True, db_index=False)
    #which question and what kind of answer... 
    conditional_question = models.IntegerField('conditional question', null=True, default=0)
    #TODO conditional to what? to the group or which question id, should be a q id. and conditional to which response of prior response?
    text = models.CharField('question text',max_length=80, blank=False, db_index=False)

    def __str__(self):
        return '%s | %s ' % (self.id, self.short_name )

    def  __unicode__(self):
        return u"Survey question for %s  - %s" % (
            self.id,  self.short_name)


class Response(models.Model):
    participant = models.ForeignKey(Participant, blank=False, null=False) 
    survey = models.ForeignKey(Survey, blank=False, null=False) 
    question = models.ForeignKey(Question, blank=False, null=False) 
    response_int = models.IntegerField('response int', null=True, default=0)
    response_float = models.FloatField('response float', null=True, default=0)
    response_string = models.CharField('response string',max_length=30, null=True, blank=True, db_index=False)
    response_choice = models.CharField('response choice', max_length=3,null=True, blank=True,  db_index=False)
    response_boolean = models.BooleanField('response boolean', blank=True, default=False)
    date = models.DateTimeField(auto_now_add=True, blank=True)

    def __str__(self):
        return '%s | %s ' % (self.id, self.survey.id )

    @staticmethod
    def create_survey():
        #should return the list of objects with the questions based on the type and survey
        # get survey name
        # get SurveyQuestionGroup based on surveyid 
        # for every group get SurveyQuestion in it
           
        surveys =  Survey.objects.all()
        survey_objects = []
        for survey in surveys:
            
            name = survey.name
            question_groups = QuestionGroup.objects.filter(survey__in = surveys)
            questions = Question.objects.filter(question_group__in = question_groups)
            survey_objects += [{'name' : name, 'id': survey.id, 
                            'questions' :questions }]
        return survey_objects
    
    class Meta:
        verbose_name = 'Survey Response'
        ordering = ['date']  

    def  __unicode__(self):
        return u"Survey Response for %s  on %s" % (
            self.participant,  self.date)


