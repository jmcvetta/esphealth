#-*- coding:utf-8 -*-

from ESP.esp.models import Vaccine, ImmunizationManufacturer
from ESP.conf.models import Icd9

from ESP.vaers.models import DiagnosticsEventRule

# Constants defined in the VAERS documents.
TEMP_TO_REPORT = 100.4 # degrees are F in our records, 38C = 100.4F
TIME_WINDOW_POST_EVENT = 7 # One week to report

VAERS_LAB_RESULTS = {
    '718-7':{
        'name':'Hemoglobin',
        'criteria':[{
            'trigger':'X<10',
            'unit':'g/L',
            'exclude_if':('>','LKV*0.8'),
            'category':'confirm'
            }]
        },

    '26464-8':{
        'name':'WBC Count',
        'criteria':[{
            'trigger':'X<3.5',
            'unit':'x109/L',
            'exclude_if':('>','LKV*0.7'),
            'category':'confirm'
            }]
        },

 
    '26499-4':{
        'name':'Neutrophils',
        'criteria':[{
            'trigger':'X<2000',
            'unit':'x109/L',
            'exclude_if':('>','LKV*0.7'),
            'category':'confirm'
            }]
        },

    '26499-9':{
        'name':'Eosinophils',
        'criteria':[{
            'trigger':'X>600',
            'unit':'x109/L',
            'exclude_if':('<','LKV*1.2'),
            'category':'confirm'
            }]
        },

    '26474-7':{
        'name':'Lymphocytes',
        'criteria':[{
            'trigger':'X<1000',
            'unit':'x109/L',
            'exclude_if':('>','LKV*0.7'),
            'category':'confirm'
            }]
        },

    '26515-7':{
        'name':'Platelet count',
        'criteria':[{
            'trigger':'X<150',
            'unit':'x109/L',
            'exclude_if':('>','LKV*0.7'),
            'category':'confirm'
            }]
        },


    '2160-0':{
        'name':'Creatinine',
        'criteria':[{
            'trigger':'X>1.5',
            'unit':'mg/dL',
            'exclude_if':('<','LKV*1.3'),
            'category':'confirm'
            }]
        },

    '1742-6':{
        'name':'ALT',
        'criteria':[{
            'trigger':'X>120',
            'unit':'IU/L',
            'exclude_if':('<','LKV*1.3'),
            'category':'confirm'
     }]
        },



    '1920-8':{
        'name':'AST',
        'criteria':[{
            'trigger':'X>100',
            'unit':'IU/L',
            'exclude_if':('<','LKV*1.3'),
            'category':'confirm'
            }]
        },

    

    '33899-6':{
        'name':'Bilirubin',
        'criteria':[{
            'trigger':'X>2.0',
            'unit':'mg/dL',
            'exclude_if':('<','LKV*1.2'),
            'category':'confirm'
            }]
        },

    '6768-6':{
        'name':'ALK',
        'criteria':[{
            'trigger':'X>200',
            'unit':'IU/L',
            'exclude_if':('<','LKV*1.3'),
            'category':'confirm'
            }]
        },

    '14979-9':{
        'name':'PTT',
        'criteria':[{
            'trigger':'X>60',
            'unit':'s',
            'exclude_if':('<','LKV*1.3'),
            'category':'confirm'
            }]
        },


    '2157-6':{
        'name':'Creatine kinase',
        'criteria':[{
            'trigger':'X>500',
            'unit':'U/L',
            'exclude_if':('<','LKV*1.3'),
            'category':'confirm'
            }]
        },

    '2345-7':{
        'name':'Glucose',
        'criteria':[{
            'trigger':'X>200',
            'unit':'mg/dL',
            'exclude_if':('<','LKV*2.0'),
            'category':'confirm'
            }]
        },

    '2823-3':{
        'name':'Potassium',
        'criteria':[{
            'trigger':'X>5.5',
            'unit':'mmol/L',
            'exclude_if':('<','LKV+0.5'),
            'category':'confirm'
            }]
        },

    '2951-2':{
        'name':'Sodium',
        'criteria':[{
                'trigger':'X>150',
                'unit':'mmol/L',
                'exclude_if':('<','LKV+5'),
                'category':'confirm'
                },
                    {
                'trigger':'X<130',
                'unit':'mmol/L',
                'exclude_if':('>','LKV-5'),
                'category':'confirm'
                }]
        }
    }
        


VAERS_DIAGNOSTICS = {
    '357.0': {
        'name':'Guillain-Barre',
        'ignore_period':12,
        'category':'default',
        'source':'Menactra'
        },
    
    '351.0': {
        'name':'Bell''s palsy',
        'ignore_period':12,
        'category':'default',
        'source':'Menactra'
        },
    
    '345.*; 780.3': {
        'name':'Seizures',
        'ignore_period':None,
        'category':'default',
        'source':'Menactra'
        },
    
    '779.0; 333.2':{
        'name':'Seizures (RotaTeq)',
        'ignore_period':None,
        'category':'default',
        'source':'RotaTeq'
        },
    
    '780.31': {
        'name':'Febrile seizure',
        'ignore_period':None,
        'category':'default',
        'source':'MMR-V'
        },
    
    '052.7; 334.4; 781.2; 781.3': {
        'name':'Ataxia',
        'ignore_period':12,
        'category':'default',
        'source':'MMR-V'
        },
    
    '323.9; 323.5; 055.0; 052.0': {
        'name':'Encephalitis',
        'ignore_period':12,
        'category':'default',
        'source':'MMR-V'
        },
    
    '714.9; 716.9; 056.71': {
        'name':'Arthritis',
        'ignore_period':12,
        'category':'default',
        'source':'MMR-V'
        },
    
    '708.0': {
        'name':'Allergic urticaria',
        'ignore_period':12,
        'category':'default',
        'source':'MMR-V'
        },
    
    '995.1': {
        'name':'Angioneurotic edema',
        'ignore_period':12,
        'category':'default',
        'source':'MMR-V'
        },
    
    '999.4': {
        'name':'Anaphylactic shock due to serum',
        'ignore_period':12,
        'category':'default',
        'source':'MMR-V'
        },
    
    '543.9; 560.0': {
        'name':'Intussusception',
        'ignore_period':12,
        'category':'default',
        'source':'RotaTeq'
        
        },
    
    '569.3; 578.1; 578.9': {
        'name':'GI bleeding',
        'ignore_period':12,
        'ignore_codes':['004*', '008*', '204-208*', '286*', '287*', '558.3', '800-998*'],
        'category':'default',
        'source':'RotaTeq'
        },
    
    '047.8; 047.9; 049.9;321.2; 322*;323.5;323.9': {
        'name':'Meningitis / encephalitis',
        'ignore_period':12,
        'ignore_codes':['047.0-047.1', '048*', '049.0-049.8', '053-056*', '320*'],
        'category':'default',
        'source':'RotaTeq'
        },
    
    '429.0; 422*': {
        'name':'Myocarditis',
        'ignore_period':12,
        'category':'default',
        'source':'RotaTeq'
        },
    
    '995.20': {
        'name':'Hypersensitivity - drug, unspec',
        'ignore_period':None,
        'category':'confirm'
        },
    
    '495.9': {
        'name':'Pneumonitis - hypersensitivity',
        'ignore_period':None,
        'category':'confirm'
          
        },
    
    '478.8': {
        'name':'Upper respiratory tract hypersensitivity reaction',
        'ignore_period':None,
        'category':'confirm'
        },
    
    '978.8': {
        'name':'Poisoning - bacterial vaccine',
        'ignore_period':None,
        'category':'confirm'
        },
    
    '978.9': {
        'name':'Poisoning - mixed bacterial (non-pertussis) vaccine',
        'ignore_period':None,
        'category':'confirm'
        },
    
    '999.39': {
        'name':'Infection due to vaccine',
        'ignore_period':None,
        'category':'confirm'
        },
    
    '999.5': {
        'name':'Post-immunization reaction',
        'ignore_period':None,
        'category':'confirm'
        },
    
    '323.52': {
        'name':'Myelitis - post immunization',
        'ignore_period':None,
        'category':'confirm'
        },
    
    '323.51':{ 
        'name':'Encephalitis / encephalomyelitis - post immunization',  
        'ignore_period':None,
        'category':'confirm'          
        }
    }

VACCINE_MAPPING = {
    "BCG IMMUNIZATION":Vaccine.objects.get(code=19),
    "CHOLERA VACCINE":Vaccine.objects.get(code=26),
    "CMV IMMUNE GLOBULIN":Vaccine.objects.get(code=8),
    "DT VACCINE (CHILD)":Vaccine.objects.get(code=28),
    "DTAP VACCINE":Vaccine.objects.get(code=20),
    "DTAP-HEP B-IPV":Vaccine.objects.get(code=110),
    "DTAP-HEP B-IPV (PEDIARIX)":Vaccine.objects.get(code=110),
    "DTAP-HFLU B CONJ VACCINE":Vaccine.objects.get(code=50),
    "DTAP-HFLU B CONJ-IPV (PENTACEL)":Vaccine.objects.get(code=120),
    "DTAP-HFLU B CONJ-IPV VACCINE":Vaccine.objects.get(code=120),
    "DTAP-IPV VACCINE":Vaccine.objects.get(code=130),
    "DTP VACCINE":Vaccine.objects.get(code=1),
    "DTP-HFLU B CONJ VACCINE":Vaccine.objects.get(code=22),
    "HEP A & B VACCINE ADULT":Vaccine.objects.get(code=104),
    "HEP A IMMUNE GLOBULIN":Vaccine.objects.get(code=999),
    "HEP A VACCINE":Vaccine.objects.get(code=999),
    "HEP A VACCINE ADULT":Vaccine.objects.get(code=52),
    "HEP A VACCINE PEDI/ADOL-2 DOSE SCHED":Vaccine.objects.get(code=83),
    "HEP A VACCINE PEDI/ADOL-3 DOSE SCHED":Vaccine.objects.get(code=84),
    "HEP B - HFLU B CONJ (PRP-OMP)":Vaccine.objects.get(code=999),
    "HEP B IMMUNE BY SEROLOGY":Vaccine.objects.get(code=999),
    "HEP B IMMUNE GLOBULIN (HBIG)":Vaccine.objects.get(code=30),
    "HEP B VACCINE (11-19 YEARS)":Vaccine.objects.get(code=8),
    "HEP B VACCINE (20+ YEARS)":Vaccine.objects.get(code=43),
    "HEP B VACCINE (<11 YEARS)":Vaccine.objects.get(code=999),
    "HEP B VACCINE (ILL PT, ANY AGE)":Vaccine.objects.get(code=999),
    "HEP B VACCINE (PLASMA-DERIVED)":Vaccine.objects.get(code=999),
    "HEP B VACCINE (RECOMBINANT)":Vaccine.objects.get(code=999),
    "HEP B VACCINE ADOL-2 DOSE SCHED":Vaccine.objects.get(code=999),
    "HFLU B (NON-CONJ)":Vaccine.objects.get(code=999),
    "HFLU B (UNSPECIFIED)":Vaccine.objects.get(code=999),
    "HFLU B CONJ (HBOC)":Vaccine.objects.get(code=47),
    "HFLU B CONJ (PRP-D)":Vaccine.objects.get(code=46),
    "HFLU B CONJ (PRP-OMP)":Vaccine.objects.get(code=49),
    "HFLU B CONJ (PRP-T)":Vaccine.objects.get(code=48),
    "HPV (6, 11, 16, 18) VACCINE":Vaccine.objects.get(code=62),
    "HPV VACCINE(16, 18)":Vaccine.objects.get(code=118),
    "HPV VACCINE(6, 11, 16, 18)":Vaccine.objects.get(code=62),
    "IMMUNE GLOBULIN, IV":Vaccine.objects.get(code=999),
    "IMMUNE GLOBULIN, SC":Vaccine.objects.get(code=999),
    "IMMUNE SERUM GLOBULIN (ISG)":Vaccine.objects.get(code=999),
    "INFLUENZA VACCINE":Vaccine.objects.get(code=16),
    "JAPANESE ENCEPHALITIS VACCINE":Vaccine.objects.get(code=999),
    "LYME VACCINE":Vaccine.objects.get(code=66),
    "MEASLES (RUBEOLA) - MUMPS VACCINE":Vaccine.objects.get(code=05),
    "MEASLES (RUBEOLA) - RUBELLA VACCINE":Vaccine.objects.get(code=04),
    "MEASLES IMMUNE BY SEROLOGY":Vaccine.objects.get(code=999),
    "MEASLES VACCINE (RUBEOLA)":Vaccine.objects.get(code=999),
    "MENINGOC IM (MENACTRA) VACCINE":Vaccine.objects.get(code=108),
    "MENINGOC SQ (MENOMUNE) VACCINE":Vaccine.objects.get(code=108),
    "MENINGOCOCCAL C VACCINE (BRITISH)":Vaccine.objects.get(code=114),
    "MMR VACCINE":Vaccine.objects.get(code=03),
    "MMR VARICELLA VACCINE":Vaccine.objects.get(code=64),
    "MMR-VARICELLA VACCINE":Vaccine.objects.get(code=94),
    "MUMPS IMMUNE BY SEROLOGY":Vaccine.objects.get(code=999),
    "MUMPS VACCINE":Vaccine.objects.get(code=999),
    "PERTUSSIS VACCINE (MONOVALENT)":Vaccine.objects.get(code=11),
    "PLAGUE VACCINE":Vaccine.objects.get(code=23),
    "PNEUMOCOC/ADULT-POLYSAC":Vaccine.objects.get(code=999),
    "PNEUMOCOC/PEDI-CONJUGATE":Vaccine.objects.get(code=999),
    "POLIO VACCINE (INACTIVATED)":Vaccine.objects.get(code=10),
    "POLIO VACCINE(ORAL,TRIVALENT)":Vaccine.objects.get(code=02),
    "RABIES IMMUNE GLOBULIN (RIG)":Vaccine.objects.get(code=34),
    "RABIES VACCINE":Vaccine.objects.get(code=999),
    "RABIES VACCINE (HUMAN DIPLOID CELL)":Vaccine.objects.get(code=999),
    "RABIES VACCINE (RHESUS DIPLOID CELL)":Vaccine.objects.get(code=999),
    "RABIES VACCINE, ID":Vaccine.objects.get(code=40),
    "RABIES VACCINE, IM":Vaccine.objects.get(code=18),
    "RHOGAM":Vaccine.objects.get(code=999),
    "ROCKY MTN SPOTTED FEVER VACCINE":Vaccine.objects.get(code=999),
    "ROTAVIRUS VACCINE":Vaccine.objects.get(code=122),
    "ROTAVIRUS VACCINE (ROTARIX)":Vaccine.objects.get(code=999),
    "ROTAVIRUS VACCINE (ROTATEQ)":Vaccine.objects.get(code=999),
    "RSV IMM GLOB (IM, SYNAGIS)":Vaccine.objects.get(code=71),
    "RUBELLA IMMUNE BY SEROLOGY":Vaccine.objects.get(code=999),
    "RUBELLA VACCINE":Vaccine.objects.get(code=999),
    "SMALLPOX VACCINE":Vaccine.objects.get(code=999),
    "TB TEST":Vaccine.objects.get(code=999),
    "TD VACCINE (ADULT)":Vaccine.objects.get(code=999),
    "TDAP":Vaccine.objects.get(code=115),
    "TETANUS BOOSTER":Vaccine.objects.get(code=999),
    "TETANUS IMMUNE GLOBULIN":Vaccine.objects.get(code=999),
    "TETANUS TOXOID":Vaccine.objects.get(code=999),
    "TYPHOID VACCINE (ORAL) TY21A":Vaccine.objects.get(code=25),
    "TYPHOID VACCINE (PAREN,HEAT-PHENOL)":Vaccine.objects.get(code=53),
    "TYPHOID VACCINE (VICPS,PAREN,CPS)":Vaccine.objects.get(code=101),
    "TYPHUS VACCINE":Vaccine.objects.get(code=999),
    "VACCINIA VIRUS":Vaccine.objects.get(code=999),
    "VARICELLA DISEASE":Vaccine.objects.get(code=21),
    "VARICELLA IMMUNE BY SEROLOGY":Vaccine.objects.get(code=36),
    "VARICELLA VACCINE":Vaccine.objects.get(code=999),
    "VARICELLA-ZOSTER IMMUNE GLOBULIN (VZIG)":Vaccine.objects.get(code=36),
    "YELLOW FEVER VACCINE":Vaccine.objects.get(code=999),
    "ZOSTER SHINGLES VACCINE":Vaccine.objects.get(code=12),
}


MANUFACTURER_MAPPING = {
    "ARMOUR":ImmunizationManufacturer.objects.get(code="AR"),
    "BAYER":ImmunizationManufacturer.objects.get(code="BAY"),
    "BERKELEY":ImmunizationManufacturer.objects.get(code="OTH"),
    "BERNA":ImmunizationManufacturer.objects.get(code="BPC"),
    "BURROUGHS":ImmunizationManufacturer.objects.get(code="OTH"),
    "CHIRON BEHRI":ImmunizationManufacturer.objects.get(code="CHI"),
    "CONNAUGHT":ImmunizationManufacturer.objects.get(code="PMC"),
    "DELMONT":ImmunizationManufacturer.objects.get(code="OTH"),
    "GSK":ImmunizationManufacturer.objects.get(code="SKB"),
    "IMMUNO U.S.":ImmunizationManufacturer.objects.get(code="IUS"),
    "LEDERLE":ImmunizationManufacturer.objects.get(code="LED"),
    "LYONS":ImmunizationManufacturer.objects.get(code="OTH"),
    "MASS DPH":ImmunizationManufacturer.objects.get(code="OTH"),
    "MEDIMMUNE":ImmunizationManufacturer.objects.get(code="MED"),
    "MERCK & CO":ImmunizationManufacturer.objects.get(code="MSD"),
    "MSD":ImmunizationManufacturer.objects.get(code="MSD"),
    "NABI BIOPHAR":ImmunizationManufacturer.objects.get(code="NAB"),
    "NOVARTIS":ImmunizationManufacturer.objects.get(code="NOV"),
    "ORGANON":ImmunizationManufacturer.objects.get(code="OTH"),
    "ORTHO DIAG":ImmunizationManufacturer.objects.get(code="ORT"),
    "PARKDALE":ImmunizationManufacturer.objects.get(code="PD"),
    "PASTEUR":ImmunizationManufacturer.objects.get(code="PMC"),
    "PRAXIS":ImmunizationManufacturer.objects.get(code="PRX"),
    "ROCHE":ImmunizationManufacturer.objects.get(code="OTH"),
    "sanofi paste":ImmunizationManufacturer.objects.get(code="PMC"),
    "SCHERING":ImmunizationManufacturer.objects.get(code="OTH"),
    "SMITHKLINE":ImmunizationManufacturer.objects.get(code="SKB"),
    "TALECRIS":ImmunizationManufacturer.objects.get(code="TAL"),
    "WYETH-AYERST":ImmunizationManufacturer.objects.get(code="WA"),
    "ZLB BEHRING":ImmunizationManufacturer.objects.get(code="ZLB")
    }



def define_active_rules():
    '''Read each of the rules defined in VAERS_DIAGNOSTICS
    dict to create the Rule objects. The keys in the dict define a
    whole set of icd9 codes that are indication of a VAERS Event'''
    
    def find_and_add_codes(code_expression_list, code_set):
        for code_expression in code_expression_list:
            try:
                # If it's a single code, we should be able to find it
                # here. Before we try to raise ValueError to check if
                # it's an expression or a code. Faster than going to
                # the DB.
                c = float(code_expression)
                code = Icd9.objects.get(code=code_expression)
                code_set.add(code)
            except:
                # DoesNotExist. It means we're dealing with an expression.
                # We'll expand it, get the codes and add
                codes = Icd9.expansion(code_expression)
                for code in codes:
                    code_set.add(code)


    # Deactivating ALL Rules and replacing them with the current set
    DiagnosticsEventRule.deactivate_all()


    for k, v in VAERS_DIAGNOSTICS.items():
        obj, created = DiagnosticsEventRule.objects.get_or_create(
            name=v['name'],
            ignored_if_past_occurrence = v['ignore_period'],
            category=v['category'],
            source=v.get('source', None)
            )
        
        obj.activate()

        find_and_add_codes(k.split(';'), obj.heuristic_defining_codes)
        find_and_add_codes(v.get('ignore_codes', []), 
                           obj.heuristic_discarding_codes)


if __name__ == '__main__':
    define_active_rules()
