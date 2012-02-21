#-*- coding:utf-8 -*-

from ESP.static.models import Icd9, Vaccine, ImmunizationManufacturer
from ESP.utils.utils import log

# Constants defined in the VAERS documents.
TEMP_TO_REPORT = 100.4 # degrees are F in our records, 38C = 100.4F

#ver 3 of vaers doc says 42, prior versions were 30 but code was 60

TIME_WINDOW_POST_EVENT = 42 # Period of time between immunization and event
# TODO should we change the time window post to 30?

#types of action types 
# 1_common: (auto) Common, well described, non-serious, adverse event
# 2_rare: (default) Rare, severe adverse event on VSD list
# 3_possible: (confirm) Possible novel adverse event not previously associated with vaccine
# 4_unlikely: (discard) Routine health visit highly unlikely to be adverse event

NEW_VAERS_LAB_RESULTS = {
    'hemoglobin': {
        'trigger': 'X<10',
        'unit': 'g/L',
        'exclude_if': ('>','LKV*0.8'),
        'category': '3_possible',
        'risk_period': 30,
        },
    'white_blood_cell_count': {
        'trigger':     'X<3.5',
        'unit':        'x109/L',
        'exclude_if':  ('>','LKV*0.7'),
        'category':    '3_possible',
        'risk_period': 30,
        },

    }

VAERS_LAB_RESULTS = {
    #TODO issue 345 fix me we need to define these sets of codes as sets for an abstract labs 
    'Hemoglobin':{
        'codes':[
            '83036--258', '83051--258', '83036--1638', '80055--1100', '82955--1100', '83020--1100',
            '83021--1100', '85014--1100', '85018--1100', '85018--9', '85021--1100', '85021--9',
            '85025--1100', '85025--9', '85027--1100', '85027--9', '83021--4264', '83020--420',
            '83021--6651', '82948--2882', '83036--2882', '83036--4859', '83036--2481', '83020--423',
            '83021--423', '83020--4865', '83020--4866', '83021--4266', '85027--584', '83020--4864',
            '83020--421', 'N1743--421', '83021--4268', '85027--586', '83050--1579', '83045--3449',
            '83021--4265', '83020--424', '83021--424', '83020--2293', '87341--4585', '86382--636',
            '87516--5162', '87516--5795', '87516--5160', '87516--5161'],
        'criteria':[{
                'trigger':'X<10',
                'unit':'g/L',
                'exclude_if':('>','LKV*0.8'),
                'category':'3_possible',
                'risk_period':30
                }]
        },
    
    'WBC Count':{
        'codes':[
            '89051--4914', '89051--710', '85007--2548', '89320--1446', 'LA0326--1446', '89320--1446', 
            'LA0326--1446', '80055--2965', '83970--2842', '85007--2965', '85025--2842', '85025--2965', 
            '85027--2842', '85027--2965', '85048--2842', '85048--2965', '87210--5340', '81000--474', 
            '81001--474', '81015--474', '85027--254', '85048--254', '85025--1102', '85027--1102', 
            '85048--1102', '81000--43', '81001--43', '81015--43', '81099--43', '85027--582'
            ],
        'criteria':[{
            'trigger':'X<3.5',
            'unit':'x109/L',
            'exclude_if':('>','LKV*0.7'),
            'category':'3_possible',
            'risk_period':30
            }]
        },

 
    'Neutrophils':{
        'codes':[
            '85025--2772', '85027--2772', '85048--2772', '85007--2781', '85007--2525', '85025--2525',
            '85027--2525', '89051--4916', '85008--6746', '86038--6067', '80055--2978', '80055--2980',
            '82272--2980', '85007--2978', '85007--2980', '85007--3035', '85025--2544', '85025--2764',
            '85025--2980', '85027--2764', '85027--2978', '85027--2980', '87205--2544', '89051--3135',
            'N2131--2978', '85007--2979', '85025--3123', '89051--3123', '84443--2776', '85007--2776',
            '85025--2776', '80053--1106', '80061--1106', '81001--1106', '85007--1106', '85025--1106',
            '85027--1106'
            ],

        'criteria':[{
            'trigger':'X<2000',
            'unit':'x109/L',
            'exclude_if':('>','LKV*0.7'),
            'category':'3_possible',
            'risk_period':30
            }]
        },

    'Eosinophils':{
        'codes':[
            '85025--2770', '85027--2770', '85999--2770', '85007--2784', '85007--2528', '85025--2528',
            '85027--2528', '86235--6532', '89190--219', '85025--2767', '85027--2767', '80055--194',
            '85007--194', '85027--194', '85999--194', 'TA137--4147', '81015--3144', '80055--2970',
            '85007--1307', '85007--2970', '85025--1307', '85025--2970', '85027--1307', '85027--2970',
            '85007--2779', '85025--2779', '85025--3140', '89051--3128', '89051--3140', '89050--2634'
            ],
        
        'criteria':[{
            'trigger':'X>600',
            'unit':'x109/L',
            'exclude_if':('<','LKV*1.2'),
            'category':'3_possible',
            'risk_period':30
            }]
        },

    'Lymphocytes':{
        'codes':[
            '83718--196', '85007--196', 'N1001--196', '85007--2782', '85007--2773', '85025--2773',
            '85027--2773', '80055--3184', '85007--3184', '85027--3184', '85007--2526', '85025--2526',
            '85027--2526', '80055--3179', '85007--3037', '85007--3179', '85025--3037', '85027--3179',
            '89050--240', '89051--240', '89051--4918', '89051--743', '86355--5980', '80055--2972',
            '80055--2973', '85007--1107', '85007--2972', '85007--2973', '85007--2974', '85025--1107',
            '85025--2765', '85025--2973', '85027--1107', '85027--2765', '85027--2972', '85027--2973',
            '86355--2972', '86360--2972', '86361--2972', '88180--5984', '85007--2777', '85025--2777',
            '85007--3124', '85025--3124', '89051--3124', '86729--1201', '86999--1201', '88230--1506',
            '85007--1109', '86355--3605'
            ],
        
        'criteria':[{
            'trigger':'X<1000',
            'unit':'x109/L',
            'exclude_if':('>','LKV*0.7'),
            'category':'3_possible',
            'risk_period':30
            }]
        },

    'Platelet count':{
        'codes':[
            '85027--590', '86022--4869', '85025--1247', '85027--1247', '85049--1247', '85590--6154',
            '85027--591', '85595--591', '85007--2991', '85007--96', '85008--2991', '85008--96',
            '80055--4468', '85007--4468', '85027--4468', '86022--1189', '86022--662', '80055--2982',
            '85025--2982', '85027--2982', '85049--2982', '86023--4458'
            ],
        
        'criteria':[{
                'trigger':'X<100',
                'unit':'x109/L',
                'exclude_if':('>','LKV*0.7'),
                'category':'2_rare',
                'risk_period':30
                },
            {   'trigger':'X<150',
                'unit':'x109/L',
                'exclude_if':('>','LKV*0.7'),
                'category':'3_possible',
                'risk_period':30
                }]
        },
    
    'Creatinine':{
        'codes':[
            '80048--2926', '80053--2926', '80069--2926', '82040--2926', '84520--2926', '82382--3393',
            '82495--5222', '80004--1796', '80048--5642', '80048--59', '80053--5642', '80053--59',
            '80069--59', '80178--59', '82040--59', '82175--5639', '82382--3401', '82384--5640',
            '82540--59', '82565--1796', '82565--5642', '82565--59', '82575--59', '82947--59',
            '84520--59', '83520--1078', '83945--3400', '82575--322', '82570--2433', '84165--2433',
            '84166--2433', '86325--2433', 'LA0220--2433', '82043--50', '82128--900', '82131--900',
            '82135--50', '82139--900', '82382--50', '82384--50', '82495--50', '82507--50',
            '82530--50', '82570--50', '83088--50', '83497--50', '83505--50', '83586--50',
            '83835--50', '83945--50', '84105--50', '84120--50', '84166--50', '84585--50',
            '82570--2440', '84165--2440', '84166--2440', '86325--2440', '82104--4607', '82175--3589',
            '83015--3587', '82175--5643', '82570--320', '82570--5641', '84133--320', '84166--320',
            '84255--320', '84300--320', '86325--320', '81002--3429', '82088--3670', '82540--3085',
            '84120--3409', '82043--2552', '82089--2552', '82340--2552', '82507--2552', '82570--2552',
            '82575--2552', '83735--2552', '84120--2552', '84133--2552', '84165--2552', '84166--2552',
            '84300--2552', '84560--2552', '84585--2552', '86325--2552', '82340--2434', '82570--2434',
            '82043--4279', '84133--3901', '84300--3901', 'LA0220--675', '82043--674', '82340--674',
            '82384--674', '82436--674', '82570--674', '82575--674', '83497--674', '83520--674',
            '84133--674', '84165--674', '84166--674', '84300--674', '84560--674', '84585--674',
            '86325--674', 'LA0220--674', '82570--3891', '84166--3891', '84560--3903', '82570--2899',
            '82340--2439', '82043--1662', '82507--1662', '82570--1662', '83520--1662', '83735--1662',
            '84105--1662', '86945--1662'
            ],
        
        'criteria':[{
                'trigger':'X>1.5',
                'unit':'mg/dL',
                'exclude_if':('<','LKV*1.3'),
                'category':'3_possible',
                'risk_period':30
                }]
        },

    'ALT':{
        'codes':[
            '86003--4388', '86001--6602', '80053--1728', '84460--1728', '82785--1911', '86003--1911',
            '82785--3002', '86003--3002', '86003--1911', '86003--4752', '86003--4751', '86001--6603',
            '86003--4752', '86003--4751', '80053--58', '80076--58', '82040--58', '82947--58',
            '84450--58', '84460--58', '85048--58', 'LA0269--1793', '80053--1728', '84460--1728',
            '80053--58', '80076--58', '82040--58', '82947--58', '84450--58', '84460--58',
            '85048--58', 'LA0269--1793'],
        
        'criteria':[{
                'trigger':'X>120',
                'unit':'IU/L',
                'exclude_if':('<','LKV*1.3'),
                'category':'3_possible',
                'risk_period':30
                }]
        },
    


    'AST':{
        'codes':[
            '86003--4832', '86003--2739', '85007--1507', '86606--3807', '86003--4856', '86003--4855',
            '81001--2992', '81015--2992', '82465--1321', '81000--257', '81001--257', '81015--257',
            '87102--4297', '88173--4344', '88160--4343', '80061--6748', '81000--435', '81001--435',
            '81015--435', '86376--3111', '86255--2679', '82941--432', '80048--2877', '80053--2877',
            '82947--2877', '82948--560', '82951--2877', '82951--2943', '82951--560', '82952--560',
            'DMA002--2877', '82951--2875', '82951--2876', '82951--882', '82951--3301', '81001--4094',
            '81099--4094', '80061--390', '82465--390', '83718--390', '86606--3802', '86698--3828',
            '86698--5827', '81000--256', '81001--256', '81015--256', '81099--256', '82951--157',
            '82950--1378', '81001--4097', '82656--5110', '85730--1221', '80053--57', '80076--57',
            '82040--57', '82947--57', '84450--1792', '84450--57', '84455--57', 'LA0269--1792',
            '82951--2880', '82951--64', '82952--64', '81000--476', '81001--476', '81015--476',
            '81001--475', '81015--475', '81001--255', '81015--255', '81000--474', '81001--474',
            '81015--474', '81000--195', '81001--195', '81015--195', '81099--195', '87210--195',
            '87220--195', '87210--5341', '87220--5341', '86698--901', '86698--901', '80053--57',
            '80076--57', '82040--57', '82947--57', '84450--1792', '84450--57', '84455--57',
            'LA0269--1792'
            ],
        
        'criteria':[{
                'trigger':'X>100',
                'unit':'IU/L',
                'exclude_if':('<','LKV*1.3'),
                'category':'3_possible'
                }]
        },
    
    
    
    'Bilirubin':{
        'codes':[
            '82542--5442', '80076--206', '81000--206', '81002--206', '82040--206', '82247--206', 
            '82248--206', '82251--206', 'LA0349--206', '82248--1715', '80076--478', '82040--478',
            '82247--478', 'LA0349--478', '82247--2938', '82248--1511', '82247--1448', '80053--2893',
            '80053--365', '80076--2893', '80076--365', '82040--2893', '82247--2893', '82247--365',
            '82251--2893', '82251--365', '82947--365', 'LA0269--2893', 'LA0349--2893', '82247--2551',
            '81001--2894', '81002--2894', '81005--2894', '84110--826', '84110--3254', '84120--3408', 
            '87205--2254', '87205--2253', '81000--38', '81001--38', '81002--38', '81003--38', 
            '81099--38', '81001--1392', '81003--1392', '81005--1392', '81000--1058', '81001--1058', 
            '81002--1058', '81003--1058', '81001--2954', '81002--2954', '81003--2954'
            ],
        
        'criteria':[{
                'trigger':'X>2.0',
                'unit':'mg/dL',
                'exclude_if':('<','LKV*1.2'),
                'category':'3_possible',
                'risk_period':30
                }]
        },

    'ALK':{
        'codes':[
            '80053--66', '80076--66', '82040--66', '82947--66', '84075--66', '84080--66',
            '84078--5405', '84075--3480', 'LA0269--3480', '81002--3137', '85540--3137', 
            '84080--180','84080--179', '84080--178', '84080--181', '80076--177', '84075--177', 
            '84080--177', '84078--5803', '81002--818', '85540--818'
            ],
        
        'criteria':[{
                'trigger':'X>200',
                'unit':'IU/L',
                'exclude_if':('<','LKV*1.3'),
                'category':'3_possible',
                'risk_period':30
                }]
        },
    
    'PTT':{
        'codes':[
            '85610--4595', '85610--2858', '85730--2858', '85300--2249', '85613--2249', '85730--759',
            '85300--3159', '86148--3159', '85730--1221'
            ],
        'criteria':[{
                'trigger':'X>60',
                'unit':'s',
                'exclude_if':('<','LKV*1.3'),
                'category':'3_possible',
                'risk_period':30
                }]
        },
    

    'Creatine kinase':{
        'codes':['82552--5637','82552--6721'],
        'criteria':[{
                'trigger':'X>500',
                'unit':'U/L',
                'exclude_if':('<','LKV*1.3'),
                'category':'3_possible',
                'risk_period':30
                }]
        },
    
    'Glucose':{
        'codes':[
            '80004--3301', '80048--2523', '80051--2523', '80053--2523', '80069--2523', '80076--2523',
            '81000--2523', '81002--2523', '82040--2523', '82272--2523', '82947--2523', '82948--2523',
            '82948--2948', '82948--3301', '82948--3302', '82948--3303', '82948--3305', '82948--3307',
            '82951--2523', '82951--3301', '82951--3302', '82951--3303', '82951--3305', '82951--3306',
            '82951--3307', '82951--4506', '82951--4774', '82951--5758', 'N1646--2523', '82947--4454',
            '82947--6545', '82950--2861', '82951--2862', '82951--2857', '82951--2855', 'DMA002--2855',
            '82951--2944', '82951--562', '82951--714', '82952--714', '82950--2859', '82951--2859',
            'DMA002--2859', '82950--2896', '82950--2848', '82951--2848', '82951--2866', 'DMA002--2866',
            '82951--2867', '82951--805', '82952--805', '82951--2945', '82951--1592', '82947--2863',
            '82951--2863', 'DMA002--2863', '82951--715', '82952--715', '82951--2865', '82947--2847',
            '82951--2847', '82947--459', '82950--459', '82951--459', '82951--563', '82951--716',
            '82952--716', '82951--2868', '82951--2887', '82951--884', '82951--2870', '82951--832',
            '82951--2920', '82951--833', '82951--2873', '82951--2921', '82951--886', '82951--887',
            '82948--2948', '83036--2948', '82947--881', '82948--881', '82947--383', '80048--2877',
            '80053--2877', '82947--2877', '82948--560', '82951--2877', '82951--2943', '82951--560',
            '82952--560', 'DMA002--2877', '82951--2875', '82951--2876', '82951--882', '82947--2948',
            '82948--2948', '82962--2948', '81000--35', '81001--35', '81002--35', '81003--35',
            '81099--35', '82947--1795', '82948--1795', '82947--61', '82948--61', '81001--2952',
            '81002--2952', '81003--2952', '81005--2952', '87210--2', '82951--3301', '82945--4637',
            '82955--643', '82951--5759', '82951--5760', '82951--5761', '83036--1186', '82951--160',
            '82951--157', '82951--158', '82951--159', '82950--1378', '82950--161', '82951--161',
            '82951--1028', '82952--1028', '82951--1469', '82952--1469', '82951--1029', '82952--1029',
            '82951--1470', '82952--1470', '82951--1575', '82951--1576', '82951--2880', '82951--64',
            '82952--64'
            ],
        'criteria':[{
                'trigger':'X>200',
                'unit':'mg/dL',
                'exclude_if':('<','LKV*2.0'),
                'category':'3_possible',
                'risk_period':30
                }]
        },
    
    'Potassium':{
        'codes':[
            '80004--1804', '80004--70', '80048--70', '80051--70', '80053--70', '80069--70',
            '82040--70', '84132--70', '84133--4477', '84132--5208', '84133--3899', '84300--3899',
            '84133--815', '81002--3434', '84133--2348', '84133--2360', '84133--2361', '84133--3901',
            '84300--3901'
            ],
        'criteria':[{
                'trigger':'X>5.5',
                'unit':'mmol/L',
                'exclude_if':('<','LKV+0.5'),
                'category':'3_possible',
                'risk_period':30
                }]
        },
    
    'Sodium':{
        'codes':[
            '80004--1798', '80004--60', '80048--60', '80051--60', '80053--60', '80069--60',
            '82040--60', '84295--60', '84300--494', '81002--3435', '84300--2349', '84300--2357',
            '84300--2358', '84300--5338'
            ],
        'criteria':
            [{
                'trigger':'X>150',
                'unit':'mmol/L',
                'exclude_if':('<','LKV+5'),
                'category':'3_possible',
                'risk_period':30
                },
             {
                'trigger':'X<130',
                'unit':'mmol/L',
                'exclude_if':('>','LKV-5'),
                'category':'3_possible',
                'risk_period':30
                }
             ]
        },

     'Calcium':{
         'codes':[
             '80004--1810', '80048--74', '80053--74', '80069--74', '82040--74', '82307--74',
             '82310--74', '83970--74', '84443--74', 'LA0216--74', 'LA0344--74', '81002--5504',
             '81002--3446', '82340--3892', '82570--3892', '82340--446', '82340--3430', '83970--678',
             '82340--2434', '82570--2434', '82330--679', '82340--1904', '82570--1904'
             ],
         'criteria':[{
                'trigger':'X>12',
                'unit':'mg/dL',
                'exclude_if':('<','LKV+0.5'),
                'category':'3_possible',
                'risk_period':30
                },
                {
                'trigger':'X<7',
                'unit':'mg/dL',
                'exclude_if':('<','LKV-2'),
                'category':'3_possible',
                'risk_period':30
                }
                ]
         } 

    }  

# TODO issue 345 add more from spec, perhaps change to load this into a table (fixture) and 
# read in from it in the code that uses it.

VAERS_DIAGNOSTICS = {
    '357.0': {#
        'name':'Guillain-Barre',
        'ignore_period':12,
        'category':'2_rare',
        'source':'Menactra',
        'risk_period_days': 30,
        },
    
    '351.0': {#
        'name':'Bell''s palsy',
        'ignore_period':12,
        'category':'2_rare',
        'source':'Menactra',
        'risk_period_days': 30,        
        },
        
    '723.3; 723.4': {#
        'name':'Brachial neuritis',
        'ignore_period':12,
        'category':'2_rare',
        'source':'HPV',
        'risk_period_days': 30,        
        },    
    
    '493*; 786.07': {#
        'name':'Bronchospasm',
        'ignore_period':3,
        'category':'3_possible',
        'source':'',
        'risk_period_days': 7,        
        },
        
    '682.3': {#
        'name':'Cellulitis – upper arm',
        'ignore_period':3,
        'category':'3_possible',
        'source':'',
        'risk_period_days': 30,        
        },
        
    '682.5': {#
        'name':'Cellulitis – buttock',
        'ignore_period':3,
        'category':'3_possible',
        'source':'',
        'risk_period_days': 30,        
        },        
    
    '682.6': {#
        'name':'Cellulitis – thigh',
        'ignore_period':3,
        'category':'3_possible',
        'source':'',
        'risk_period_days': 30,        
        }, 
        
    '350; 351; 352': {#
        'name':'Cranial nerve disorders',
        'ignore_period':12,
        'category':'2_rare',
        'source':'TdaP',
        'risk_period_days': 30,        
        },    
        
    '780.92': {#
        'name':'Excessive crying',
        'ignore_period':None,
        'category':'2_rare',
        'source':'',
        'risk_period_days': 7,        
        },  
                 
    '345*; 780.3': {#
        'name':'Seizures',
        'ignore_period':None,
        'category':'2_rare',
        'source':'Menactra',
        'risk_period_days': 30,
        },
    
    '779.0; 333.2':{#
        'name':'Seizures (RotaTeq)',
        'ignore_period':None,
        'category':'2_rare',
        'source':'RotaTeq',
        'risk_period_days': 30,
        },
    
    '433*; 434*; 435.0; 435.1; 435.8; 435.9; 436*; 437.1':{#
        'name':'Stroke',
        'ignore_period':12,
        'category':'2_rare',
        'source':'HPV',
        'risk_period_days': 30,
        },
    
    '798.0':{#
        'name':'Sudden infant death syndrome',
        'ignore_period':None,
        'category':'2_rare',
        'risk_period_days': 30,
        },
    
    '780.2':{#
        'name':'Syncope',
        'ignore_period':12,
        'category':'2_rare',
        'source':'HPV',
        'risk_period_days': 30,
        },
                
    '780.31': {#
        'name':'Febrile seizure',
        'ignore_period':None,
        'category':'2_rare',
        'source':'MMR-V',
        'risk_period_days': 14,
        },
    
    '052.7; 334.4; 781.2; 781.3': {#
        'name':'Ataxia',
        'ignore_period':12,
        'category':'2_rare',
        'source':'MMR-V',
        'risk_period_days': 30,
        },
    
    '323.9; 323.5; 323.6; 323.7; 323.8; 055.0; 052.0': {
        'name':'Encephalitis',#
        'ignore_period':12,
        'category':'2_rare',
        'source':'MMR-V',
        'risk_period_days': 30,
        },
    
    '348.3; 348.5': {#
        'name':'Encephalopathy',#
        'ignore_period':12,
        'category':'2_rare',
        'source':'TdaP',
        'risk_period_days': 30,
        },
        
    '714.9; 716.9; 056.71': {#
        'name':'Arthritis',
        'ignore_period':12,
        'category':'2_rare',
        'source':'MMR-V',
        'risk_period_days': 30,
        },
    
    '708.0': {#
        'name':'Allergic urticaria',
        'ignore_period':12,
        'category':'2_rare',
        'source':'MMR-V',
        'risk_period_days': 14,
        },
    
    '995.1': {#
        'name':'Angioneurotic edema',
        'ignore_period':12,
        'category':'2_rare',
        'source':'MMR-V',
        'risk_period_days': 7,
        },
    
    '999.4': {#
        'name':'Anaphylactic shock due to serum',
        'ignore_period':12,
        'category':'2_rare',
        'source':'MMR-V',
        'risk_period_days': 14,
        },
        
    '995.0': {#
        'name':'Anaphylxis',
        'ignore_period':12,
        'category':'2_rare',
        'source':'MMR-V',
        'risk_period_days': 7,
        },    
    
    '540*': {#
        'name':'Appendicitis',
        'ignore_period':12,
        'category':'2_rare',
        'source':'MMR-V',
        'risk_period_days': 30,
        },
        
    '543.9; 560.0': {#
        'name':'Intussusception',
        'ignore_period':12,
        'category':'2_rare',
        'source':'RotaTeq',
        'risk_period_days': 30,
        },
    
    '446.1': {#
        'name':'Kawasaki disease',
        'ignore_period':12,
        'category':'2_rare',
        'source':'RotaTeq',
        'risk_period_days': 30,
        },
    
    '569.3; 578.1; 578.9': {#
        'name':'GI bleeding',
        'ignore_period':12,
        'ignore_codes':['004*', '008*', '204-208*', '286*', '287*', '558.3', '800-998*'],
        'category':'2_rare',
        'source':'RotaTeq',
        'risk_period_days': 30,
        },
    
    '047.8; 047.9; 049.9;321.2; 322*': {#
        'name':'Meningitis',
        'ignore_period':12,
        'ignore_codes':['047.0-047.1', '048*', '049.0-049.8', '053-056*', '320*'],
        'category':'2_rare',
        'source':'RotaTeq',
        'risk_period_days': 30,
        },
    
    '429.0; 422*': {#
        'name':'Myocarditis',
        'ignore_period':12,
        'category':'2_rare',
        'source':'RotaTeq',
        'risk_period_days': 30,
        },
    
    '342; 344; 781.4; 341.2; 341.20; 341.21; 341.22': {# 
        'name':'Paralytic syndromes',
        'ignore_period':12,
        'category':'2_rare',
        'source':'TdaP',
        'risk_period_days': 30,
        },
    
    '420*': {#
        'name':'Pericarditis',
        'ignore_period':12,
        'category':'2_rare',
        'source':'Influenza',
        'risk_period_days': 30,
        },
           
    '377.3; 377.30; 377.31; 377.32; 377.34; 377.39': {#
        'name':'Optic neuritis',
        'ignore_period':12,
        'category':'2_rare',
        'source':'Influenza Hep B',
        'risk_period_days': 30,
        },
    
    '347*': {#
        'name':'Narcolepsy',
        'ignore_period':12,
        'category':'2_rare',
        'source':'Pandemrix',
        'risk_period_days': 30,
        },
                    
    '995.20': {#
        'name':'Hypersensitivity - drug, unspec',
        'ignore_period':12,
        'category':'3_possible',
        'risk_period_days': 7,
        },
    
    '287.0': {#
        'name':'Henoch-Schonlein purpura',
        'ignore_period':12,
        'category':'2_rare',
        'source':'Polysaccharide MeningococcalV',
        'risk_period_days': 30,
        },
        
    '287.31': {#
        'name':'Idiopathic thrombocytopenic purpura',
        'ignore_period':12,
        'category':'2_rare',
        'source':'MMR',
        'risk_period_days': 30,
        },
            
    '495.9': {#
        'name':'Pneumonitis - hypersensitivity',
        'ignore_period':12,
        'category':'3_possible',
        'risk_period_days': 30,
          
        },
    
    '478.8': {#
        'name':'Upper respiratory tract hypersensitivity reaction',
        'ignore_period':12,
        'category':'3_possible',
        'risk_period_days': 14,
        },
    
    '360.11; 363.20; 364.3': {#
        'name':'Uveitis',
        'ignore_period':12,
        'category':'2_rare',
        'source':'Heb B',
        'risk_period_days': 30,
        },
        
    '999.0': {#
        'name':'Vaccinia (generalized)',
        'ignore_period':None,
        'category':'2_rare',
        'risk_period_days': 30,
        },
        
    '415.1; 415.11; 415.12; 415.19; 453*': {#   
        'name':'Venous thromboembolism',
        'ignore_period':12,
        'category':'2_rare',
        'source':'HPV',
        'risk_period_days': 30,
        },    
        
    '978*': {#
        'name':'Poisoning - bacterial vaccine',
        'ignore_period':None,
        'category':'2_rare',
        'risk_period_days': 30,
        },
    
    '979*': {#
        'name':'Poisoning - mixed bacterial (non-pertussis) vaccine',
        'ignore_period':None,
        'category':'2_rare',
        'risk_period_days': 30,
        },
    
    '999.39': {#
        'name':'Infection due to vaccine',
        'ignore_period':None,
        'category':'2_rare',
        'risk_period_days': 30,
        },
    
    '999.5': {#
        'name':'Post-immunization reaction',
        'ignore_period':None,
        'category':'2_rare',
        'risk_period_days': 30,
        },
    
    '323.52': {#
        'name':'Myelitis - post immunization',
        'ignore_period':None,
        'category':'2_rare',
        'risk_period_days': 30,
        },
    
    '323.51':{ #
        'name':'Encephalitis / encephalomyelitis - post immunization',  
        'ignore_period':None,
        'category':'2_rare',
        'risk_period_days': 30,          
        }
    }


def define_active_rules():
    '''Read each of the rules defined in VAERS_DIAGNOSTICS
    dict to create the Rule objects. The keys in the dict define a
    whole set of icd9 codes that are indication of a VAERS Event'''
    log.info('running define_active_rules for diagnosis')
    
    from ESP.vaers.models import DiagnosticsEventRule
    
    
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
                if len(codes) == 0:
                    for c in code_expression_list:
                        try:
                            Icd9.objects.get(code=c.strip())
                        except:
                            print c

                for code in codes:
                    code_set.add(code)


    # Deactivating ALL Rules and replacing them with the current set
    #DiagnosticsEventRule.deactivate_all()
    
    #
    # Flush out the old table entries
    #
    DiagnosticsEventRule.objects.all().delete()


    for k, v in VAERS_DIAGNOSTICS.items():
        obj, created = DiagnosticsEventRule.objects.get_or_create(
            name=v['name'],
            ignore_period = v['ignore_period'],
            category=v['category'],
            source=v.get('source', None),
            risk_period = v['risk_period_days'],
            )
        
        obj.activate()

        find_and_add_codes(k.split(';'), obj.heuristic_defining_codes)
        find_and_add_codes(v.get('ignore_codes', []), 
                           obj.heuristic_discarding_codes)




def main():
    define_active_rules()
    map_lab_tests()


if __name__ == '__main__':
    main()
