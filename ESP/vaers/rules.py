
TEMP_TO_REPORT = 100.4 # degrees are F in our records, 38C = 100.4F
TIME_WINDOW_POST_EVENT = days=7 # One week to report


VAERS_LAB_RESULTS = [
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


VAERS_DIAGNOSTICS = {
    '357.0': {
        'name':'Guillain-Barre',
        'ignore_period':12,
        'category':2,
        'source':'Menactra'
        },
    
    '351.0': {
        'name':'Bell''s palsy',
        'ignore_period':12,
        'category':2,
        'source':'Menactra'
        },
    
    '345.*; 780.3': {
        'name':'Seizures',
        'ignore_period':None,
        'category':2,
        'source':'Menactra'
        },
    
    '779.0; 333.2':{
        'name':'Seizures (RotaTeq)',
        'ignore_period':None,
        'category':2,
        'source':'RotaTeq'
        },
    
    '780.31': {
        'name':'Febrile seizure',
        'ignore_period':None,
        'category':2,
        'source':'MMR-V'
        },
    
    '052.7; 334.4; 781.2; 781.3': {
        'name':'Ataxia',
        'ignore_period':12,
        'category':2,
        'source':'MMR-V'
        },
    
    '323.9; 323.5; 055.0; 052.0': {
        'name':'Encephalitis',
        'ignore_period':12,
        'category':2,
        'source':'MMR-V'
        },
    
    '714.9; 716.9; 056.71': {
        'name':'Arthritis',
        'ignore_period':12,
        'category':2,
        'source':'MMR-V'
        },
    
    '708.0': {
        'name':'Allergic urticaria',
        'ignore_period':12,
        'category':2,
        'source':'MMR-V'
        },
    
    '995.1': {
        'name':'Angioneurotic edema',
        'ignore_period':12,
        'category':2,
        'source':'MMR-V'
        },
    
    '999.4': {
        'name':'Anaphylactic shock due to serum',
        'ignore_period':12,
          'category':2,
        'source':'MMR-V'
        },
    
    '543.9; 560.0': {
        'name':'Intussusception',
        'ignore_period':12,
        'category':2,
        'source':'RotaTeq'
        
        },
    
    '569.3; 578.1; 578.9': {
        'name':'GI bleeding',
        'ignore_period':12,
        'ignore_codes':['004*', '008*', '204-208*', '286*', '287*', '558.3', '800-998*'],
        'category': 2,
        'source':'RotaTeq'
        },
    
    '047.8; 047.9; 049.9;321.2; 322*;323.5;323.9': {
        'name':'Meningitis / encephalitis',
        'ignore_period':12,
        'ignore_codes':['047.0-047.1', '048*', '049.0-049.8', '053-056*', '320*'],
        'category':2,
        'source':'RotaTeq'
        },
    
    '429.0; 422*': {
        'name':'Myocarditis',
        'ignore_period':12,
        'category':2,
        'source':'RotaTeq'
        },
    
    '995.20': {
        'name':'Hypersensitivity - drug, unspec',
        'ignore_period':None,
        'category':3
        },
    
    '495.9': {
        'name':'Pneumonitis - hypersensitivity',
        'ignore_period':None,
        'category':3
          
        },
    
    '478.8': {
        'name':'Upper respiratory tract hypersensitivity reaction',
        'ignore_period':None,
        'category':3
        },
    
    '978.8': {
        'name':'Poisoning - bacterial vaccine',
        'ignore_period':None,
        'category':3
        },
    
    '978.9': {
        'name':'Poisoning - mixed bacterial (non-pertussis) vaccine',
        'ignore_period':None,
        'category':3
        },
    
    '999.39': {
        'name':'Infection due to vaccine',
        'ignore_period':None,
        'category':3
        },
    
    '999.5': {
        'name':'Post-immunization reaction',
        'ignore_period':None,
        'category':3
        },
    
    '323.52': {
        'name':'Myelitis - post immunization',
        'ignore_period':None,
        'category':3
        },
    
    '323.51':{ 
        'name':'Encephalitis / encephalomyelitis - post immunization',  
        'ignore_period':None,
        'category':3          
        }
    }




VACCINE_CODE_SET = {
    54: {"description":"adenovirus, type 4",
         "full_name":"adenovirus vaccine, type 4, live, oral"
         },
    55:{"description":"adenovirus, type 7",
        "full_name":"adenovirus vaccine, type 7, live, oral"
        },
    82:{"description":"adenovirus, NOS1",
        "full_name":"adenovirus vaccine, NOS"
        },
    24:{"description":"anthrax",
        "full_name":"anthrax vaccine"
        },
    19:{"description":"BCG",
        "full_name":"Bacillus Calmette-Guerin vaccine"
        },
    27:{"description":"botulinum antitoxin",
        "full_name":"botulinum antitoxin"
        },
    26:{"description":"cholera",
        "full_name":"cholera vaccine"
        },
    29:{"description":"CMVIG",
        "full_name":"cytomegalovirus immune globulin, intravenous"
        },
    56:{"description":"dengue fever",
        "full_name":"dengue fever vaccine"
        },
    12:{"description":"diphtheria antitoxin",
        "full_name":"diphtheria antitoxin"
        },
    28:{"description":"DT (pediatric)",
        "full_name":"diphtheria and tetanus toxoids, adsorbed for pediatric use"
        },
    20:{"description":"DTaP",
        "full_name":"diphtheria, tetanus toxoids and acellular pertussis vaccine"
        },
    106:{"description":"DTaP, 5 pertussis antigens",
         "full_name":"diphtheria, tetanus toxoids and acellular pertussis vaccine, 5 pertussis antigens"
         },
    107:{"description":"DTaP, NOS",
         "full_name":"diphtheria, tetanus toxoids and acellular pertussis vaccine, NOS"
         },
    110:{"description":"DTaP-Hep B-IPV",
         "full_name":"DTaP-hepatitis B and poliovirus vaccine"
         },
    50:{"description":"DTaP-Hib",
        "full_name":"DTaP-Haemophilus influenzae type b conjugate vaccine"
        },
    120:{"description":"DTaP-Hib-IPV",
         "full_name":"diphtheria, tetanus toxoids and acellular pertussis vaccine, Haemophilus influenzae type b conjugate, and poliovirus vaccine,inactivated (DTaP-Hib-IPV)"
         },
    130:{"description":"DTaP-IPV",
         "full_name":"Diphtheria, tetanus toxoids and acellular pertussis vaccine, and poliovirus vaccine, inactivated"
         },
    1:{"description":"DTP",
        "full_name":"diphtheria, tetanus toxoids and pertussis vaccine"
        },
    22:{"description":"DTP-Hib",
        "full_name":"DTP-Haemophilus influenzae type b conjugate vaccine"
        },
    102:{"description":"DTP-Hib-Hep B",
         "full_name":"DTP- Haemophilus influenzae type b conjugate and hepatitis b vaccine"
         },
    57:{"description":"hantavirus",
        "full_name":"hantavirus vaccine"
        },
    52:{"description":"Hep A, adult",
        "full_name":"hepatitis A vaccine, adult dosage"
        },
    83:{"description":"Hep A, ped/adol, 2 dose",
        "full_name":"hepatitis A vaccine, pediatric/adolescent dosage, 2 dose schedule"
        },
    84:{"description":"Hep A, ped/adol, 3 dose",
        "full_name":"hepatitis A vaccine, pediatric/adolescent dosage, 3 dose schedule"
        },
    31:{"description":"Hep A, pediatric, NOS",
        "full_name":"hepatitis A vaccine, pediatric dosage, NOS"
        },
    85:{"description":"Hep A, NOS",
        "full_name":"hepatitis A vaccine, NOS"
        },
    104:{"description":"Hep A-Hep B",
         "full_name":"hepatitis A and hepatitis B vaccine"
         },
    30:{"description":"HBIG",
        "full_name":"hepatitis B immune globulin"
        },
    8:{"description":"Hep B, adolescent or pediatric",
        "full_name":"hepatitis B vaccine, pediatric or pediatric/adolescent dosage"
        },
    42:{"description":"Hep B, adolescent/high risk infant2",
        "full_name":"hepatitis B vaccine, adolescent/high risk infant dosage"
        },
    43:{"description":"Hep B, adult",
        "full_name":"hepatitis B vaccine, adult dosage"
        },
    44:{"description":"Hep B, dialysis",
        "full_name":"hepatitis B vaccine, dialysis patient dosage"
        },
    45:{"description":"Hep B, NOS",
        "full_name":"hepatitis B vaccine, NOS"
        },
    58:{"description":"Hep C",
        "full_name":"hepatitis C vaccine"
        },
    59:{"description":"Hep E",
        "full_name":"hepatitis E vaccine"
        },
    60:{"description":"herpes simplex 2",
        "full_name":"herpes simplex virus, type 2 vaccine"
        },
    46:{"description":"Hib (PRP-D)",
        "full_name":"Haemophilus influenzae type b vaccine, PRP-D conjugate"
        },
    47:{"description":"Hib (HbOC)",
        "full_name":"Haemophilus influenzae type b vaccine, HbOC conjugate"
        },
    48:{"description":"Hib (PRP-T)",
        "full_name":"Haemophilus influenzae type b vaccine, PRP-T conjugate"
        },
    49:{"description":"Hib (PRP-OMP)",
        "full_name":"Haemophilus influenzae type b vaccine, PRP-OMP conjugate"
        },
    17:{"description":"Hib, NOS",
        "full_name":"Haemophilus influenzae type b vaccine, conjugate NOS"
        },
    51:{"description":"Hib-Hep B",
        "full_name":"Haemophilus influenzae type b conjugate and Hepatitis B vaccine"
        },
    61:{"description":"HIV",
        "full_name":"human immunodeficiency virus vaccine"
        },
    118:{"description":"HPV, bivalent",
         "full_name":"human papilloma virus vaccine, bivalent"
         },
    62:{"description":"HPV, quadrivalent",
        "full_name":"human papilloma virus vaccine, quadrivalent"
        },
    86:{"description":"IG",
        "full_name":"immune globulin, intramuscular"
        },
    87:{"description":"IGIV",
        "full_name":"immune globulin, intravenous"
        },
    14:{"description":"IG, NOS",
        "full_name":"immune globulin, NOS"
        },
    111:{"description":"influenza, live, intranasal",
         "full_name":"influenza virus vaccine, live, attenuated, for intranasal use"
         },
    15:{"description":"influenza, split (incl. purified surface antigen)",
        "full_name":"influenza virus vaccine, split virus (incl. purified surface antigen)"
        },
    16:{"description":"influenza, whole",
        "full_name":"influenza virus vaccine, whole virus"
        },
    88:{"description":"influenza, NOS",
        "full_name":"influenza virus vaccine, NOS"
        },
    123:{"description":"influenza, H5N1-1203",
         "full_name":"influenza virus vaccine, H5N1, A/Vietnam/1203/2004 (national stockpile)"
         },
    10:{"description":"IPV",
        "full_name":"poliovirus vaccine, inactivated"
        },
    02:{"description":"OPV",
        "full_name":"poliovirus vaccine, live, oral"
        },
    89:{"description":"polio, NOS",
        "full_name":"poliovirus vaccine, NOS"
        },
    39:{"description":"Japanese encephalitis",
        "full_name":"Japanese encephalitis vaccine"
        },
    63:{"description":"Junin virus",
        "full_name":"Junin virus vaccine"
        },
    64:{"description":"leishmaniasis",
        "full_name":"leishmaniasis vaccine"
        },
    65:{"description":"leprosy",
        "full_name":"leprosy vaccine"
        },
    66:{"description":"Lyme disease",
        "full_name":"Lyme disease vaccine"
        },
    03:{"description":"MMR",
        "full_name":"measles, mumps and rubella virus vaccine"
        },
    04:{"description":"M/R",
        "full_name":"measles and rubella virus vaccine"
        },
    94:{"description":"MMRV",
        "full_name":"measles, mumps, rubella, and varicella virus vaccine"
        },
    67:{"description":"malaria",
        "full_name":"malaria vaccine"
        },
    05:{"description":"measles",
        "full_name":"measles virus vaccine"
        },
    68:{"description":"melanoma",
        "full_name":"melanoma vaccine"
        },
    32:{"description":"meningococcal",
        "full_name":"meningococcal polysaccharide vaccine (MPSV4)"
        },
    103:{"description":"meningococcal C conjugate",
         "full_name":"meningococcal C conjugate vaccine"
         },
    114:{"description":"meningococcal A,C,Y,W-135 diphtheria conjugate",
         "full_name":"meningococcal polysaccharide (groups A, C, Y and W-135) diphtheria toxoid co{njugate vaccine (MCV4)"
         },
    108:{"description":"meningococcal, NOS",
         "full_name":"meningococcal vaccine, NOSChanges last made on May 10, 2006"
         },
    07:{"description":"mumps",
        "full_name":"mumps virus vaccine"
        },
    69:{"description":"parainfluenza-3",
        "full_name":"parainfluenza-3 virus vaccine"
        },
    11:{"description":"pertussis",
        "full_name":"pertussis vaccine"
        },
    23:{"description":"plague",
        "full_name":"plague vaccine"
        },
    33:{"description":"pneumococcal",
        "full_name":"pneumococcal polysaccharide vaccine"
        },
    100:{"description":"pneumococcal conjugate",
         "full_name":"pneumococcal conjugate vaccine, polyvalent"
         },
    109:{"description":"pneumococcal, NOS",
         "full_name":"pneumococcal vaccine, NOS"
         },
    70:{"description":"Q fever",
        "full_name":"Q fever vaccine"
        },
    18:{"description":"rabies, intramuscular injection",
        "full_name":"rabies vaccine, for intramuscular injection"
        },
    40:{"description":"rabies, intradermal injection",
        "full_name":"rabies vaccine, for intradermal injection"
        },
    90:{"description":"rabies, NOS",
        "full_name":"rabies vaccine, NOS"
        },
    72:{"description":"rheumatic fever",
        "full_name":"rheumatic fever vaccine"
        },
    73:{"description":"Rift Valley fever",
        "full_name":"Rift Valley fever vaccine"
        },
    34:{"description":"RIG",
        "full_name":"rabies immune globulin"
        },
    119:{"description":"rotavirus, monovalent",
         "full_name":"rotavirus, live, monovalent vaccineChanges last made on Feb. 28, 2006"
         },
    122:{"description":"rotavirus, NOS1",
         "full_name":"rotavirus vaccine, NOSChanges last made on June 1, 2006"
         },
    116:{"description":"rotavirus, pentavalent",
         "full_name":"rotavirus, live, pentavalent vaccineChanges last made on Feb. 28, 2006"
         },
    74:{"description":"rotavirus, tetravalent",
        "full_name":"rotavirus, live, tetravalent vaccineChanges last made on Feb. 28, 2006"
        },
    71:{"description":"RSV-IGIV",
        "full_name":"respiratory syncytial virus immune globulin, intravenous"
        },
    93:{"description":"RSV-MAb",
        "full_name":"respiratory syncytial virus monoclonal antibody (palivizumab), intramuscular"
        },
    06:{"description":"rubella",
        "full_name":"rubella virus vaccine"
        },
    38:{"description":"rubella/mumps",
        "full_name":"rubella and mumps virus vaccine"
        },
    76:{"description":"Staphylococcus bacterio lysate",
        "full_name":"Staphylococcus bacteriophage lysate"
        },
    113:{"description":"Td (adult)",
         "full_name":"tetanus and diphtheria toxoids, adsorbed, preservative free, for adult use"
         },
    9:{"description":"Td (adult)",
        "full_name":"tetanus and diphtheria toxoids, adsorbed for adult use"
        },
    115:{"description":"Tdap",
         "full_name":"tetanus toxoid, reduced diphtheria toxoid, and acellular pertussis vaccine, adsorbed Changes last made on May 10, 2006{"
         },
    35:{"description":"tetanus toxoid",
        "full_name":"tetanus toxoid, adsorbed"
        },
    112:{"description":"tetanus toxoid, NOS",
         "full_name":"tetanus toxoid, NOS"
         },
    77:{"description":"tick-borne encephalitis",
        "full_name":"tick-borne encephalitis vaccine"
        },
    13:{"description":"TIG",
        "full_name":"tetanus immune globulin"
        },
    95:{"description":"TST-OT tine test",
        "full_name":"tuberculin skin test; old tuberculin, multipuncture device"
        },
    96:{"description":"TST-PPD intradermal",
        "full_name":"tuberculin skin test; purified protein derivative solution, intradermal"
        },
    97:{"description":"TST-PPD tine test",
        "full_name":"tuberculin skin test; purified protein derivative, multipuncture device"
        },
    98:{"description":"TST, NOS",
        "full_name":"tuberculin skin test; NOS"
        },
    78:{"description":"tularemia vaccine",
        "full_name":"tularemia vaccine"
        },
    91:{"description":"typhoid, NOS",
        "full_name":"typhoid vaccine, NOS"
        },
    25:{"description":"typhoid, oral",
        "full_name":"typhoid vaccine, live, oral"
        },
    41:{"description":"typhoid, parenteral",
        "full_name":"typhoid vaccine, parenteral, other than acetone-killed, dried"
        },
    53:{"description":"typhoid, parenteral, AKD (U.S. military)",
        "full_name":"typhoid vaccine, parenteral, acetone-killed, dried (U.S. military)"
        },
    101:{"description":"typhoid, ViCPs",
         "full_name":"typhoid Vi capsular polysaccharide vaccine"
         },
    75:{"description":"vaccinia (smallpox)",
        "full_name":"vaccinia (smallpox) vaccine"
        },
    105:{"description":"vaccinia (smallpox) diluted",
         "full_name":"vaccinia (smallpox) vaccine, diluted"
         },
    79:{"description":"vaccinia immune globulin",
        "full_name":"vaccinia immune globulin"
        },
    21:{"description":"varicella",
        "full_name":"varicella virus vaccine"
        },
    81:{"description":"VEE, inactivated",
        "full_name":"Venezuelan equine encephalitis, inactivated"
        },
    80:{"description":"VEE, live",
        "full_name":"Venezuelan equine encephalitis, live, attenuated"
        },
    92:{"description":"VEE, NOS",
        "full_name":"Venezuelan equine encephalitis vaccine, NOS"
        },
    36:{"description":"VZIG",
        "full_name":"varicella zoster immune globulin"
        },
    117:{"description":"VZIG (IND)",
         "full_name":"varicella zoster immune globulin (Investigational New Drug) Changes last made on Feb. 28, 2006"
         },
    37:{"description":"yellow fever",
        "full_name":"yellow fever vaccine"
        },
    121:{"description":"zoster",
         "full_name":"zoster vaccine, live Changes last made on June 1, 2006"
         },
    998:{"description":"no vaccine administered5",
         "full_name":"no vaccine administered"
         },
    999:{"description":"unknown",
         "full_name":"unknown vaccine or immune globulin"
         },
    99:{"description":"RESERVED - do not use3",
        "full_name":"RESERVED - do not use"}
    }


VACCINE_MANUFACTURERS = {
    "AB":"Abbott Laboratories (includes Ross Products Division)",
    "ACA":"Acambis, Inc",
    "AD":"Adams Laboratories, Inc.",
    "ALP":"Alpha Therapeutic Corporation",
    "AR":"Armour [Inactive--use AVB]",
    "AVB":"Aventis Behring L.L.C. (formerly Centeon L.L.C.; includes Armour Pharmaceutical Company) [Inactive--use ZLB]",
    "AVI":"Aviron",
    "BA":"Baxter Healthcare Corporation [Inactive--use BAH]",
    "BAH":"Baxter Healthcare Corporation (includes Hyland Immuno, Immuno International AG, and North American Vaccine, Inc.)",
    "BAY":"Bayer Corporation (includes Miles, Inc. and Cutter Laboratories)",
    "BP":"Berna Products [Inactive--use BPC]",
    "BPC":"Berna Products Corporation (includes Swiss Serum and Vaccine Institute Berne)",
    "MIP":"Bioport Corporation (formerly Michigan Biolologic Products Institute)",
    "CSL":"CSL Biotherapies, Inc.",
    "CNJ":"Cangene Corporation",
    "CMP":"Celltech Medeva Pharmaceuticals [Inactive--use NOV]",
    "CEN":"Centeon L.L.C. [Inactive--use AVB]",
    "CHI":"Chiron Corporation [Inactive--use NOV] includes PowderJect Pharmaceuticals, Celltech Medeva Vaccines and Evans Medical Limited",
    "CON":"Connaught [Inactive--use PMC]",
    "DVC":"DynPort Vaccine Company, LLC",
    "EVN":"Evans Medical Limited [Inactive--use NOV]",
    "GEO":"GeoVax Labs, Inc.",
    "SKB":"GlaxoSmithKline (formerly SmithKline Beecham; includes SmithKline Beecham and Glaxo Welcome)",
    "GRE":"Greer Laboratories, Inc.",
    "IAG":"Immuno International AG [Inactive--use BAH]",
    "IUS":"Immuno-U.S., Inc.",
    "KGC":"Korea Green Cross Corporation",
    "LED":"Lederle [Inactive--use WAL]",
    "MBL":"Massachusetts Biologic Laboratories (formerly Massachusetts Public Health Biologic Laboratories)",
    "MA":"Massachusetts Public Health Biologic Laboratories [Inactive--use MBL]",
    "MED":"MedImmune, Inc.",
    "MSD":"Merck & Co., Inc.",
    "IM":"Merieux [Inactive--use PMC]",
    "MIL":"Miles [Inactive--use BAY]",
    "NAB":"NABI (formerly North American Biologicals, Inc.)",
    "NYB":"New York Blood Center",
    "NAV":"North American Vaccine, Inc. [Inactive--use BAH]",
    "NOV":"Novartis Pharmaceutical Corporation (includes Chiron, PowderJect Pharmaceuticals, Celltech Medeva Vaccines and Evans Limited, Ciba-Geigy Limited and Sandoz Limited)",
    "NVX":"Novavax, Inc.",
    "OTC ":"Organon Teknika Corporation",
    "ORT":"Ortho-Clinical Diagnostics (formerly Ortho Diagnostic Systems, Inc.)",
    "PD":"Parkedale Pharmaceuticals (formerly Parke-Davis)",
    "PWJ":"PowderJect Pharmaceuticals (includes Celltech Medeva Vaccines and Evans Medical Limited) [Inactive--use NOV]",
    "PRX":"Praxis Biologics [Inactive--use WAL]",
    "PMC":"sanofi pasteur (formerly Aventis Pasteur, Pasteur Merieux Connaught; includes Connaught Laboratories and Pasteur Merieux)",
    "JPN":"The Research Foundation for Microbial Diseases of Osaka University (BIKEN)",
    "SCL":"Sclavo, Inc.",
    "SOL":"Solvay Pharmaceuticals",
    "SI":"Swiss Serum and Vaccine Inst. [Inactive--use BPC]",
    "TAL":"Talecris Biotherapeutics (includes Bayer Biologicals)",
    "USA":"United States Army Medical Research and Material Command",
    "VXG":"VaxGen",
    "WA":"Wyeth-Ayerst [Inactive--use WAL]",
"WAL":"Wyeth-Ayerst (includes Wyeth-Lederle Vaccines and Pediatrics, Wyeth Laboratories, Lederle Laboratories, and Praxis Biologics)",
    "ZLB":"ZLB Behring (includes Aventis Behring and Armour Pharmaceutical Company)",
    "OTH":"Other manufacturer",
    "UNK":"Unknown manufacturer"
}




