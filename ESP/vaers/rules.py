VACCINE_ADVERSE_EVENTS = [
    {'item':'Hemoglobin',
     'trigger':'<10',
     'unit':'g/L',
     'exclusion':'X > (LKV*0.8)',
     'category':3
     },
    
    {'item':'HB',
     'trigger':'<10',
     'unit':'g/L',
     'exclusion':'X > (LKV*0.8)',
     'category':3
     },
    
    {'item':'WBC',
     'trigger':'<3.5',
     'unit':'x109/L',
     'exclusion':'X > (LKV*0.7)',
     'category':3
     },
    
    {'item':'white blood',
     'trigger':'<3.5',
     'unit':'x109/L',
     'exclusion':'X > (LKV*0.7)',
     'category':3
     },
    
    {'item':'Neutrophil',
     'trigger':'< 2000',
     'unit':'x109/L',
     'exclusion':'X > (LKV*0.7)',
     'category':3
     },
    
    {'item':'Eos',
     'trigger':'> 600',
     'unit':'x109/L',
     'exclusion':'X < (LKV*1.2)',
     'category':3
     },
    
    {'item':'Lymph',
     'trigger':'< 1000',
     'unit':'x109/L',
     'exclusion':'X > (LKV*0.7)',
     'category':3
     },
    
    {'item':'Platelet',
     'trigger':'< 150',
     'unit':'x109/L',
     'exclusion':'X > (LKV*0.7)',
     'category':3
     },
    
    {'item':'plt count',
     'trigger':'< 100',
     'unit':'x109/L',
     'exclusion':'X > (LKV*0.7)',
     'category':2
     },
    
    {'item':'Creatinine',
     'trigger':'> 1.5',
     'unit':'mg/dL',
     'exclusion':'X < (LKV*1.3)',
     'category':3
     },
    
    {'item':'ALT',
     'trigger':'>120',
     'unit':'IU/L',
     'exclusion':'X < (LKV*1.3)',
     'category':3
     },
    
    {'item':'alanine',
     'trigger':'>120',
     'unit':'IU/L',
     'exclusion':'X < (LKV*1.3)',
     'category':3
     },
    
    {'item':'SGPT',
     'trigger':'>120',
     'unit':'IU/L',
     'exclusion':'X < (LKV*1.3)',
     'category':3
     },
    
    {'item':'AST',
     'trigger':'>100',
     'unit':'IU/L',
     'exclusion':'X < (LKV*1.3)',
     'category':3
     },
    
    {'item':'aspartate',
     'trigger':'>100',
     'unit':'IU/L',
     'exclusion':'X < (LKV*1.3)',
     'category':3
     },
    
    {'item':'SGOT',
     'trigger':'>100',
     'unit':'IU/L',
     'exclusion':'X < (LKV*1.3)',
     'category':3
     },
    
    {'item':'Bili',
     'trigger':'>2.0',
     'unit':'mg/dL',
     'exclusion':'X < (LKV*1.2)',
     'category':3
     },
    
    {'item':'ALK',
     'trigger':'>200',
     'unit':'IU/L',
     'exclusion':'X < (LKV*1.3)',
     'category':3
     },
    
    {'item':'PTT',
     'trigger':'>60',
     'unit':'s',
     'exclusion':'X < (LKV*1.3)',
     'category':3
     },
    
    {'item':'Thromboplastin',
     'trigger':'>60',
     'unit':'s',
     'exclusion':'X < (LKV*1.3)',
     'category':3
     },
    
    {'item':'Creatine kinase',
     'trigger':'>500',
     'unit':'U/L',
     'exclusion':'X < (LKV*1.3)',
     'category':3
     },
    
    {'item':'ck',
     'trigger':'>500',
     'unit':'U/L',
     'exclusion':'X < (LKV*1.3)',
     'category':3
     },
    
    {'item':'Glucose',
     'trigger':'>200',
     'unit':'mg/dL',
     'exclusion':'X < (LKV*2.0)',
     'category':3
     },
    
    {'item':'Potassium',
     'trigger':'>5.5',
     'unit':'mmol/L',
     'exclusion':'X < (LKV + 0.5)',
     'category':3
     },
    
    {'item':'Sodium',
     'trigger':'>150',
     'unit':'mmol/L',
     'exclusion':'X < (LKV + 5)',
     'category':3
     },
    
    {'item':'Sodium',
     'trigger':'<130',
     'unit':'mmol/L',
     'exclusion':'X > (LKV - 5)',
     'category':3
     }
    
    ]


ADVERSE_EVENTS_DIAGNOSTICS = {
    '357.0': {
        'diagnosis':'Guillain-Barre',
        'ignore_if_previous_occurence':12,
        'category':2,
        'source':'Menactra'
        },
    
    '351.0': {
        'diagnosis':'Bell''s palsy',
        'ignore_if_previous_occurence':12,
        'category':2,
        'source':'Menactra'
        },
    
    '345.*; 780.3': {
        'diagnosis':'Seizures',
        'ignore_if_previous_occurence':None,
        'category':2,
        'source':'Menactra'
        },
    
    '779.0; 333.2':{
        'diagnosis':'Seizures (RotaTeq)',
        'ignore_if_previous_occurence':None,
        'category':2,
        'source':'RotaTeq'
        },
    
    '780.31': {
        'diagnosis':'Febrile seizure ',
        'ignore_if_previous_occurence':None,
        'category':2,
        'source':'MMR-V'
        },
    
    '052.7; 334.4; 781.2; 781.3': {
        'diagnosis':'Ataxia',
          'ignore_if_previous_occurence':12,
        'category':2,
        'source':'MMR-V'
        },
    
    '323.9; 323.5; 055.0; 052.0': {
        'diagnosis':'Encephalitis',
        'ignore_if_previous_occurence':12,
        'category':2,
        'source':'MMR-V'
        },
    
    '714.9; 716.9; 056.71': {
        'diagnosis':'Arthritis',
        'ignore_if_previous_occurence':12,
        'category':2,
        'source':'MMR-V'
        },
    
    '708.0': {
        'diagnosis':'Allergic urticaria',
        'ignore_if_previous_occurence':12,
        'category':2,
        'source':'MMR-V'
        },
    
    '995.1': {
        'diagnosis':'Angioneurotic edema',
        'ignore_if_previous_occurence':12,
        'category':2,
        'source':'MMR-V'
        },
    
    '999.4': {
        'diagnosis':'Anaphylactic shock due to serum',
        'ignore_if_previous_occurence':12,
          'category':2,
        'source':'MMR-V'
        },
    
    '543.9; 560.0': {
        'diagnosis':'Intussusception',
        'ignore_if_previous_occurence':12,
        'category':2,
        'source':'RotaTeq'
        
        },
    
    '569.3; 578.1; 578.9': {
        'diagnosis':'GI bleeding',
        'ignore_if_previous_occurence':12,
        'ignore_codes':['004*', '008*', '204-208*', '286*', '287*', '558.3', '800-998*'],
        'category': 2,
        'source':'RotaTeq'
        },
    
    '047.8; 047.9; 049.9;321.2; 322*;323.5;323.9': {
        'diagnosis':'Meningitis / encephalitis',
        'ignore_if_previous_occurence':12,
        'ignore_codes':['047.0-047.1', '048*', '049.0-049.8', '053-056*', '320*'],
        'category':2,
        'source':'RotaTeq'
        },
    
    '429.0; 422*': {
        'diagnosis':'Myocarditis',
        'ignore_if_previous_occurence':12,
        'category':2,
        'source':'RotaTeq'
        },
    
    '995.20': {
        'diagnosis':'Hypersensitivity - drug, unspec',
        'ignore_if_previous_occurence':None,
        'category':3
        },
    
    '495.9': {
        'diagnosis':'Pneumonitis - hypersensitivity',
        'ignore_if_previous_occurence':None,
        'category':3
          
        },
    
    '478.8': {
        'diagnosis':'Upper respiratory tract hypersensitivity reaction',
        'ignore_if_previous_occurence':None,
        'category':3
        },
    
    '978.8': {
        'diagnosis':'Poisoning - bacterial vaccine',
        'ignore_if_previous_occurence':None,
        'category':3
        },
    
    '978.9': {
        'diagnosis':'Poisoning - mixed bacterial (non-pertussis) vaccine',
        'ignore_if_previous_occurence':None,
        'category':3
        },
    
    '999.39': {
        'diagnosis':'Infection due to vaccine',
        'ignore_if_previous_occurence':None,
        'category':3
        },
    
    '999.5': {
        'diagnosis':'Post-immunization reaction',
        'ignore_if_previous_occurence':None,
        'category':3
        },
    
    '323.52': {
        'diagnosis':'Myelitis - post immunization',
        'ignore_if_previous_occurence':None,
        'category':3
        },
    
    '323.51':{ 
        'diagnosis':'Encephalitis / encephalomyelitis - post immunization',  
        'ignore_if_previous_occurence':None,
        'category':3          
        }
    }


