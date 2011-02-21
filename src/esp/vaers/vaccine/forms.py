from django import forms

from esp.conf.models import Vaccine, ImmunizationManufacturer

STANDARD_VACCINES = ((x.code, unicode(x)) for x in 
                     Vaccine.acceptable_mapping_values())

STANDARD_MANUFACTURERS = ((x.code, unicode(x)) for x in 
                          ImmunizationManufacturer.objects.all())


class StandardVaccinesForm(forms.Form):
    vaccine = forms.ChoiceField(choices=STANDARD_VACCINES)

class StandardManufacturersForm(forms.Form):
    manufacturer = forms.ChoiceField(choices=STANDARD_MANUFACTURERS)

