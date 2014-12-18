'''
                               ESP Health Project
                             User Interface Module
                                     Views

@authors: Bob Zambarano <bzambarano@commoninf.com>
@organization: Commonwealth Informatics Inc. http://www.commoninf.com
@copyright: (c) 2014 Commonwealth Informatics, Inc.
@license: LGPL
'''
import io
from django import forms
from django.core.exceptions import ImproperlyConfigured
from django.http import HttpResponseRedirect
from django.http import HttpResponse
from django.conf.urls import url, patterns
from ESP.qmetric.models import Measure, Results
from ESP.qmetric.base import PivotQueryGen
from tabination.views import TabView
from xlsxwriter.workbook import Workbook

class TabFormMixin(object):
    """
    A mixin that provides a way to show and handle a form in a request.
    Mostly copied from django.views.generic.base.edit, except 
    removed get_contect_data because TabView has to super that from View
    """

    initial = {}
    form_class = None
    success_url = None

    def get_initial(self):
        """
        Returns the initial data to use for forms on this view.
        """
        return self.initial.copy()

    def get_form_class(self):
        """
        Returns the form class to use in this view
        """
        return self.form_class

    def get_form(self, form_class):
        """
        Returns an instance of the form to be used in this view.
        """
        return form_class(**self.get_form_kwargs())

    def get_form_kwargs(self):
        """
        Returns the keyword arguments for instanciating the form.
        """
        kwargs = {'initial': self.get_initial()}
        if self.request.method in ('POST', 'PUT'):
            kwargs.update({
                'data': self.request.POST,
                'files': self.request.FILES,
            })
        return kwargs

    def get_success_url(self):
        if self.success_url:
            url = self.success_url
        else:
            raise ImproperlyConfigured(
                "No URL to redirect to. Provide a success_url.")
        return url

    def form_valid(self, form):
        return HttpResponseRedirect(self.get_success_url())

    def form_invalid(self, form):
        return self.render_to_response(self.get_context_data(form=form))

class ResultsFilterForm(forms.Form):
    __metric = Measure.objects.all().values_list('cmsname', 'title')
    __period = Results.objects.all().distinct('periodstartdate','periodenddate').values_list('periodstartdate','periodenddate')
    metric = forms.ChoiceField(choices=__metric, widget=forms.Select(attrs={'onchange':'get_periods();'}))
    period = forms.MultipleChoiceField(choices=__period, widget=forms.SelectMultiple(attrs={'onchange':'gettables()'}))

#class FilteredTabView(TabFormMixin, TabView):
class FilteredTabView(TabView):
    dataobjdict = []
    cols = None
    
    def get_context_data(self, **kwargs):
        context = super(FilteredTabView, self).get_context_data(**kwargs)
        context['dataobjdict']=self.dataobjdict
        context['cols']=self.cols
        return context
    
#    def get_object(self, queryset=None):
    # Mostly borrowed from django/views/generic/detail/singleobjectmixin
#        pk = self.kwargs.get(self.pk_url_kwarg, None)
#        if pk is not None:
#           queryset = queryset.filter(pk=pk)
#        else:
#            raise AttributeError(u"View %s cannot have pk_url_kwarg=None."
#                                 % self.__class__.__name__)
#
#        try:
#            obj = queryset.get()
#        except ObjectDoesNotExist:
#            raise Http404(_(u"No %(verbose_name)s found matching the query") %
#                          {'verbose_name': queryset.model._meta.verbose_name})
#        return obj  

def create_racetab_views():
    views = []
    races = []
    ethnicities = []
    stratifiers = Results.objects.all().distinct('stratification').values_list('stratification', flat=True)
    for strat in stratifiers:
        if strat.strip().split(' | ')[1] not in races:
            races.append(strat.strip().split(' | ')[1])
        if strat.strip().split(' | ')[0] not in ethnicities:
            ethnicities.append(strat.strip().split(' | ')[0])
    for race in races:
        url = r'^qmetric/%s/$' % race
        dodict = {}
        for ethnic in ethnicities:
            pqg = PivotQueryGen('rate', 'period', 'age_group', ethnic, race)
            pq, columns = pqg.displayquery()
            dataobj = Results.rmanager.getrdata(pq)
            dodict[ethnic] = dataobj  
        view_class = type ( str("%s%s" % (race.capitalize(), 'View')),
                        (FilteredTabView,),
                        dict(_is_tab = True,
                             tab_id = race,
                             tab_group = 'Race',
                             tab_classes = ['racetabs'],
                             tab_label = race.capitalize(),
                             template_name = 'qmetric/qmetric_report.html',
                             url = url,
                             view_name = 'qmetric_' + race,
                             dataobjdict = dodict,
                             cols=columns
                             ))
        views.append(view_class)
    return views

def create_urls():
    urls=[]
    for view in create_racetab_views():
        urls.append(url(view.url, view.as_view(), name=view.view_name))
    urls.append(url(r'^qmetric/download/$','ESP.qmetric.views.results_xlsx',name='results_xlsx'))
    return patterns('', *urls)

def results_xlsx(request):
    '''
    Returns an excel workbook of results
    '''
    header = [
        'Numerator',
        'Denominator',
        'Rate', 
        'Ethnicity', 
        'Age_Group', 
        'PeriodStartDate', 
        'PeriodEndDate',
        ]
    qry0 = ('select numerator, denominator, round(rate::numeric,2) rate, '
          + "split_part(stratification,' | ',1) ethnicity, "
          + "split_part(stratification,' | ',3) age_group, " 
          + 'periodstartdate, periodenddate '
          + "from qmetric_results where split_part(stratification,' | ',2)='")
    races = []
    stratifiers = Results.objects.all().distinct('stratification').values_list('stratification', flat=True)
    for strat in stratifiers:
        if strat.strip().split(' | ')[1] not in races:
            races.append(strat.strip().split(' | ')[1])
    output = io.BytesIO()
    workbook = Workbook(output, {'in memory': True})
    date_format = workbook.add_format({'num_format': 'yyyy-mmm-dd'})
    for race in races:
        qry = qry0 + race + "'"
        dataobj = Results.rmanager.getrdata(qry)
        worksheet = workbook.add_worksheet(race)
        h=0
        for name in header:
            worksheet.write(0,h,name)
            h+=1
        r=1
        for row in dataobj:
            c=0
            for col in row:
                if c<=4:
                    worksheet.write(r,c,col)
                else:
                    worksheet.write_datetime(r, c, col, date_format)
                c+=1
            r+=1
    workbook.close()
    output.seek(0)
    response = HttpResponse(output.read(), content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    response['Content-Disposition'] = 'attachment; filename=quality_metrics.xlsx'
    return response
        
