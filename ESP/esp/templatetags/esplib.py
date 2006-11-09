from django import template
register = template.Library()

from ESP.esp.models import *


#############################################
#############################################
class CurICDNode(template.Node):
    def __init__(self, nodelist):
        self.nodelist=nodelist
        self.caseid=''
        self.icd=''
        self.encid=''
        
    def render(self, context):
        output = self.nodelist.render(context)
        self.caseid, self.encid, self.icd = [x.strip() for x in output.split(',')]

        c = Case.objects.filter(id=self.caseid)[0]
        caseencidl=[x.strip() for x in c.caseEncID.split(',')]
        icdl = [x.strip() for x in c.caseICD9.split(',')]
        context['curicdcolor']="BLACK"
        try:
            indx = caseencidl.index(self.encid)
            if self.icd and self.icd in icdl[indx].split():
                context['curicdcolor']="RED"
        except:
            pass

        return ''
                                            
###################################
def get_icd9_color(parser,token):
     nodelist = parser.parse(('endcoloricd',))
     parser.delete_first_token()
     return CurICDNode(nodelist)
         


###################################
class CurRowNode(template.Node):
    def __init__(self, nodelist):
        self.nodelist=nodelist
        self.casestr=''
        self.rowid=''
        
    def render(self, context):
        output = self.nodelist.render(context)
        self.casestr, self.rowid = output.split(':')
        caserowidl=[x.strip() for x in self.casestr.split(',')]
        
        if self.rowid.strip() in caserowidl:
            context['currowcolor']="RED"
        else:
            context['currowcolor']="BLACK"
            
        return ''
    
    
############################
def get_currow_color(parser, token):
    nodelist = parser.parse(('endcolorcurrow',))
    parser.delete_first_token()
    
    return CurRowNode(nodelist)

                                                                                                                    
                                                                                                                     
        

register.tag('coloricd',get_icd9_color)
register.tag('colorcurrow',get_currow_color)
