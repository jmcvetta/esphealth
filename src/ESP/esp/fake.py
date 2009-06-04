from ESP.esp.models import Provider, Demog

def fiat_mondo(population_size=5000):
    for klass in [Provider, Demog]:
        klass.delete_fakes()
    
    Provider.make_fakes(int(population_size/20))
    Demog.make_fakes(population_size)
        
if __name__ == '__main__':
    fiat_mondo()
  



