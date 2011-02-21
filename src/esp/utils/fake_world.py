from esp.emr.fake import fiat_mondo
from esp.vaers.fake import massive_immunization_action


if __name__ == '__main__':
    fiat_mondo(population_size=200)
    massive_immunization_action()
