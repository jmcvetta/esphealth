import datetime

from ESP.emr.models import Provider, Patient
from ESP.conf.common import EPOCH

TODAY = datetime.date.today()

PROVIDERS = [
     Provider(first_name='Michael', last_name='Jones'),
     Provider(first_name='Michael', last_name='Taylor'),
     Provider(first_name='Raphael', last_name='Garcia'),
     Provider(first_name='Ross',    last_name='Smith'),
     Provider(first_name='Jason',   last_name='Wilson')             
]

def fiat_mondo(population_size=200, start_date=EPOCH, end_date=TODAY,
               save_to_epic=False, save_on_db=False):
    Provider.make_fakes(save_on_db=save_on_db, save_to_epic=save_to_epic)
    Patient.make_fakes(population_size, 
                       save_on_db=save_on_db, save_to_epic=save_to_epic,
                       make_lab_results=True, make_encounters=True,
                       make_immunizations=True)
    
        
if __name__ == '__main__':
    fiat_mondo(population_size=10**7, save_on_db=True)
  



