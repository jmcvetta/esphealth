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


ADVERSE_EVENTS_DIAGNOSTICS_RULES = [
    {'diagnosis':'Guillain-Barre',
     'icd9_code':'357.0',
     'ignore_if_previous_occurence':12,
     'category':2,
     'source':'Menactra'
     },
 
    {'diagnosis':'Bell''s palsy',
     'icd9_code':'351.0',
     'ignore_if_previous_occurence':12,
     'category':2,
     'source':'Menactra'},

    {'diagnosis':'Seizures',
     'icd9_code':'345.*; 780.3',
     'ignore_if_previous_occurence':None,
     'category':2,
     'source':'Menactra'},

    {'diagnosis':'Seizures (RotaTeq)',
     'icd9_code':'779.0; 333.2',
     'ignore_if_previous_occurence':None,
     'category':2,
     'source':'RotaTeq'},
    
    {'diagnosis':'Febrile seizure ',
     'icd9_code':'780.31',
     'ignore_if_previous_occurence':None,
     'category':2,
     'source':'MMR-V'},
    
    {'diagnosis':'Ataxia',
     'icd9_code':'052.7; 334.4; 781.2; 781.3',
     'ignore_if_previous_occurence':12,
     'category':2,
     'source':'MMR-V'},
    
    {'diagnosis':'Encephalitis',
     'icd9_code':'323.9; 323.5; 055.0; 052.0',
     'ignore_if_previous_occurence':12,
     'category':2,
     'source':'MMR-V'},
    
    {'diagnosis':'Arthritis',
     'icd9_code':'714.9; 716.9; 056.71',
     'ignore_if_previous_occurence':12,
     'category':2,
     'source':'MMR-V'},
    
    {'diagnosis':'Allergic urticaria',
     'icd9_code':'708.0',
     'ignore_if_previous_occurence':12,
     'category':2,
     'source':'MMR-V'},
    
    {'diagnosis':'Angioneurotic edema',
     'icd9_code':'995.1',
     'ignore_if_previous_occurence':12,
     'category':2,
     'source':'MMR-V'},
    
    {'diagnosis':'Anaphylactic shock due to serum',
     'icd9_code':'999.4',
     'ignore_if_previous_occurence':12,
     'category':2,
     'source':'MMR-V'},
    
    {'diagnosis':'Intussusception',
     'icd9_code':'543.9; 560.0',
     'ignore_if_previous_occurence':12,
     'category':2,
     'source':'RotaTeq'
     },
    
    {'diagnosis':'GI bleeding',
     'icd9_code':'569.3; 578.1; 578.9',
     'ignore_if_previous_occurence':12,
     'ignore_codes':['004*', '008*', '204-208*', '286*', '287*', '558.3', '800-998'],
     'category': 2,
     'source':'RotaTeq'},
    
    {'diagnosis':'Meningitis / encephalitis',
     'icd9_code':'047.8; 047.9; 049.9;321.2; 322*;323.5;323.9',
     'ignore_if_previous_occurence':12,
     'ignore_codes':['047.0-047.1', '048*', '049.0-049.8', '053-056*', '320*'],
     'category':2,
     'source':'RotaTeq'},
    
    {'diagnosis':'Myocarditis',
     'icd9_code':'429.0; 422*',
     'ignore_if_previous_occurence':12,
     'category':2,
     'source':'RotaTeq'},
    
    {'diagnosis':'Hypersensitivity - drug, unspec',
     'icd9_code':'995.20',
     'ignore_if_previous_occurence':None,
     'category':3
     },
    
    {'diagnosis':'Pneumonitis - hypersensitivity',
     'icd9_code':'495.9',
     'ignore_if_previous_occurence':None,
     'category':3
     },

    {'diagnosis':'Upper respiratory tract hypersensitivity reaction',
     'icd9_code':'478.8',
     'ignore_if_previous_occurence':None,
     'category':3
     },

    {'diagnosis':'Poisoning - bacterial vaccine',
     'icd9_code':'978.8',
     'ignore_if_previous_occurence':None,
     'category':3
     },

    {'diagnosis':'Poisoning - mixed bacterial (non-pertussis) vaccine',
     'icd9_code':'978.9',
     'ignore_if_previous_occurence':None,
     'category':3
     },

    {'diagnosis':'Infection due to vaccine',
     'icd9_code':'999.39',
     'ignore_if_previous_occurence':None,
     'category':3
     },

    {'diagnosis':'Post-immunization reaction',
     'icd9_code':'999.5',
     'ignore_if_previous_occurence':None,
     'category':3
     },

    {'diagnosis':'Myelitis - post immunization',
     'icd9_code':'323.52',
     'ignore_if_previous_occurence':None,
     'category':3
     },

    {'diagnosis':'Encephalitis / encephalomyelitis - post immunization',
     'icd9_code':'323.51',
     'ignore_if_previous_occurence':None,
     'category':3
     }
]

