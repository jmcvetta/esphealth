from ESP.emr.models import Provider, Patient

def fiat_mondo(population_size=200):
    for klass in [Provider, Patient]:
        klass.delete_fakes()
    
    Provider.make_fakes(int(population_size/20))
    Patient.make_fakes(population_size)
        
if __name__ == '__main__':
    fiat_mondo()
  



