from ESP.emr.models import Provider, Patient

PROVIDERS = [
    Provider(first_name='Michael',
             last_name='Klompas'),
    Provider(first_name='Michael',
             last_name='Lee'),
    Provider(first_name='Raphael',
             last_name='Lullis'),
    Provider(first_name='Ross',
             last_name='Lazarus'),
    Provider(first_name='Jason',
             last_name='McVetta')             
]

def fiat_mondo(population_size=200):
    for klass in [Provider, Patient]:
        klass.delete_fakes()
    
    Provider.make_fakes()
    Patient.make_fakes(population_size)
        
if __name__ == '__main__':
    fiat_mondo()
  



