# some data structures for developing
# esp:ss
# NOTE - the site exclusion complexitiesre ATRIUS specific and will need to be
# completely adjusted for the kinds of exclusions required to satisfy the local
# DPH - here, we're excluding all the specialty practices to try to make ILI reporting more like
# sentinel site practice reporting...not sure how this affects other syndromes - should
# almost certainly be ignored!
# ross lazarus April 20 2009
# mostly from Katherine Yih provided spreadsheets
# syndrome defs 5 15 06 clean.xls eg
# atrius sites updated april 29 2009
# and again jun 23



localSiteSites="""Asterisk	Zip	 count(EncEncounter_SiteName) | EncEncounter_SiteName                                        | EncEncounter_Site |
		+------------------------------+--------------------------------------------------------------+-------------------+
*		|                       141532 |                                                              | 16                |
*		|                            1 | Adult Cardiology - Warwick                                   | 823611            |
*		|                        84627 | Adult Telecomm                                               | 2004701           |
*		|                            7 | Anatomical Pathology                                         | 351901            |
*		|                            1 | Arbour IP                                                    | 342101            |
*		|                            6 | Arbour OP                                                    | 342102            |
*		|                        21048 | Atrius Health Women''s Center                                | 672601            |
*		|                           28 | Bedford Internal Medicine                                    | 401801            |
*		|                          419 | BILLING OPERATIONS GROUP                                     | 27                |
*		|                          183 | Boston Case Management                                       | 088501            |
*		|                           11 | Boston Dental                                                | 080901            |
*		|                            8 | Boston Extended Care Facility Rounding                       | 088601            |
*		|                           82 | Boston Intensive Home Based Program                          | 088602            |
*		|                            8 | Boston Pharmacy                                              | 088701            |
*		|                        11426 | Boston Physical Therapy Combined                             | 083501            |
*		|                         1576 | Boston Podiatry                                              | 083601            |
*		|                          177 | Boston Radiology                                             | 083901            |
*		|                            1 | Braintree Administration                                     | 061601            |
*		|                         3427 | Braintree Allergy                                            | 060201            |
*		|                        54134 | Braintree Annex Behavioral Health                            | 505501            |
*		|                         2165 | Braintree Annex Educational Assessment Center                | 505502            |
*		|                          341 | Braintree Annex Educational Testing and Consultation Service | 505502            |
*		|                        23949 | Braintree Anticoagulation Program                            | 061804            |
*		|                         2490 | Braintree Behavioral Health                                  | 065501            |
*		|                         3401 | Braintree Cardiology, Combined                               | 065701            |
*		|                          515 | Braintree Case Management                                    | 068501            |
*		|                            2 | Braintree Cashier                                            | 069301            |
*		|                         2459 | Braintree Complex Chronic Care                               | 060401            |
*		|                         1663 | Braintree Dental                                             | 060901            |
*		|                        22008 | Braintree Dermatology                                        | 061001            |
*		|                            3 | Braintree Developmental Consultation Services                | 066301            |
*		|                           25 | Braintree Ear, Nose and Throat                               | 061201            |
*		|                            3 | Braintree ECF Rounding                                       | 068601            |
*		|                           12 | Braintree Endocrinology                                      | 061101            |
	02184	|                         7992 | Braintree Family Medicine                                    | 061805            |
	02184	|                       149903 | Braintree Internal Medicine A                                | 061801            |
	02184	|                       134275 | Braintree Internal Medicine B                                | 061802            |
	02184	|                        96119 | Braintree Internal Medicine C                                | 061803            |
*		|                         1011 | Braintree Laboratory                                         | 061901            |
*		|                          442 | Braintree Main Reception                                     | 069401            |
*		|                           67 | Braintree Maternal Home Care                                 | 068301            |
*		|                            1 | Braintree Medical Records                                    | 068001            |
*		|                        11549 | Braintree MH Combined                                        | 065501            |
*		|                          375 | Braintree MRI                                                | 063902            |
*		|                         4710 | Braintree Neurology, Combined                                | 062401            |
*		|                         3915 | Braintree Nutrition                                          | 062501            |
*		|                        12051 | Braintree Obstetrics and Gynecology                          | 062601            |
*		|                        12955 | Braintree Ophthalmology                                      | 062901            |
*		|                            2 | Braintree Optical Services                                   | 069701            |
*		|                        11057 | Braintree Optometry                                          | 063001            |
*		|                        26433 | Braintree Orthopedics, Combined                              | 065601            |
	02184	|                          117 | Braintree Pediatric Asthma                                   | 067701            |
	02184	|                       143624 | Braintree Pediatrics                                         | 063401            |
*		|                          778 | Braintree Pharmacy                                           | 068701            |
*		|                        16879 | Braintree Physical Therapy, Combined                         | 063501            |
*		|                         4631 | Braintree Podiatry                                           | 063601            |
*		|                          432 | Braintree Pulmonary Medicine                                 | 063801            |
*		|                          178 | Braintree Radiology                                          | 063901            |
*		|                        15515 | Braintree Rheumatology                                       | 064001            |
*		|                           99 | Braintree Spine Unit                                         | 065602            |
*		|                        13234 | Braintree Surgery, General                                   | 064301            |
*		|                            1 | Braintree Travel Medicine                                    | 069801            |
	02184	|                          141 | Braintree Urgent Care, After Hours, Adult                    | 064701            |
	02184	|                          106 | Braintree Urgent Care, After Hours, Pediatrics               | 064801            |
	02184	|                        23623 | Braintree Urgent Care, Weekend/Holiday, Adult                | 066401            |
	02184	|                        18737 | Braintree Urgent Care, Weekend/Holiday, Pediatric            | 066501            |
*		|                           56 | Braintree Urology Gynecology                                 | 062602            |
*		|                            5 | Braintree Visual Services                                    | 065401            |
*		|                           13 | Braintree Women''s Health Services                           | 067901            |
*		|                            2 | Braintree Women's Health Services                            | 067901            |
*		|                            1 | Burlington Administration                                    | 241601            |
*		|                         1289 | Burlington Allergy                                           | 240201            |
*		|                          744 | Burlington Anticoagulation Program                           | 241803            |
*		|                         1369 | Burlington Behavioral Health                                 | 245501            |
*		|                          152 | Burlington Case Management                                   | 248501            |
*		|                            1 | Burlington Cashier                                           | 249301            |
*		|                         3971 | Burlington Dermatology                                       | 241001            |
*		|                        18469 | Burlington Fertility and Endocrinology                       | 241301            |
*		|                          684 | Burlington Gastroenterology                                  | 241401            |
*		|                           15 | Burlington Genetics                                          | 241501            |
	01803	|                        77737 | Burlington Internal Medicine A                               | 241801            |
*		|                          529 | Burlington Laboratory                                        | 241901            |
*		|                           27 | Burlington Main Reception                                    | 249401            |
*		|                           69 | Burlington Maternal Fetal Medicine                           | 242604            |
*		|                          522 | Burlington MH,Combined                                       | 245501            |
*		|                            1 | Burlington Neurology Combined                                | 242401            |
*		|                          286 | Burlington Nutrition                                         | 242501            |
*		|                        41489 | Burlington Obstetrics and Gynecology                         | 242601            |
	01803	|                       127881 | Burlington Pediatrics                                        | 243401            |
*		|                            9 | Burlington Pharmacy                                          | 248701            |
*		|                         6905 | Burlington Physical Therapy Combined                         | 243501            |
*		|                            1 | Burlington Resource Department                               | 240101            |
*		|                         5663 | Burlington Urology Gynecology                                | 242603            |
*		|                        26485 | Burlington Vulvar Specialty                                  | 242602            |
*		|                        15388 | Cambridge Anticoagulation Program                            | 021803            |
*		|                         7894 | Cambridge Behavioral Health                                  | 025501            |
*		|                          111 | Cambridge Case Management                                    | 028501            |
*		|                            1 | Cambridge Cashier                                            | 029301            |
*		|                            2 | Cambridge Chiropractic Medicine                              | 028801            |
*		|                          232 | Cambridge Complex Chronic Care                               | 020401            |
*		|                        11645 | Cambridge Dermatology                                        | 021001            |
*		|                         7123 | Cambridge Ear, Nose and Throat                               | 021201            |
*		|                           35 | Cambridge ECF Rounding                                       | 028601            |
*		|                         4084 | Cambridge Endocrinology                                      | 021101            |
*		|                        11112 | Cambridge Gastroenterology                                   | 021401            |
*		|                           38 | Cambridge Intensive Home Based Program                       | 028602            |
	02138	|                       110068 | Cambridge Internal Medicine 1                                | 021801            |
	02138	|                        99483 | Cambridge Internal Medicine 2                                | 021802            |
*		|                          307 | Cambridge Laboratory                                         | 021901            |
*		|                            2 | Cambridge Main Desk                                          | 029401            |
*		|                          491 | Cambridge Medical Records                                    | 028001            |
*		|                        29402 | Cambridge MH,Combined                                        | 025501            |
*		|                         1606 | Cambridge Nephrology                                         | 022301            |
*		|                         1070 | Cambridge Nutrition                                          | 022501            |
*		|                        29479 | Cambridge Obstetrics and Gynecology                          | 022601            |
*		|                            1 | Cambridge Orthopedics, Combined                              | 025601            |
*		|                            1 | Cambridge Parking                                            | 029501            |
	02138	|                        48607 | Cambridge Pediatrics                                         | 023401            |
*		|                           10 | Cambridge Radiology                                          | 023901            |
*		|                         4856 | Cambridge Surgery, General                                   | 024301            |
	02138	|                            5 | Cambridge Urgent Care, After Hours, Adult                    | 024701            |
*		|                            1 | Cash Receipts Department                                     | 26                |
*		|                            2 | Chelmsford Administration                                    | 131601            |
*		|                         4325 | Chelmsford Allergy                                           | 130201            |
*		|                        22158 | Chelmsford Anticoagulation Program                           | 131803            |
*		|                        10238 | Chelmsford Behavioral Health                                 | 135501            |
*		|                         8803 | Chelmsford Cardiology                                        | 130401            |
*		|                         1253 | Chelmsford Case Management                                   | 138501            |
*		|                         1289 | Chelmsford Complex Chronic Care                              | 130402            |
*		|                          997 | Chelmsford Contact Lens                                      | 130701            |
*		|                         3045 | Chelmsford Dental                                            | 130901            |
*		|                        17316 | Chelmsford Dermatology                                       | 131001            |
*		|                            1 | Chelmsford Developmental Consultation Services               | 136301            |
*		|                          984 | Chelmsford Ear, Nose and Throat                              | 131201            |
*		|                          228 | Chelmsford ECF ROUNDING                                      | 138601            |
*		|                            9 | Chelmsford Employee Health                                   | 133402            |
*		|                         5249 | Chelmsford Endocrinology                                     | 131101            |
*		|                         8260 | Chelmsford Gastroenterology                                  | 131401            |
*		|                          653 | Chelmsford Intensive Home Based Program                      | 138602            |
	01824	|                       295368 | Chelmsford Internal Medicine A                               | 131801            |
*		|                         2370 | Chelmsford Laboratory                                        | 131901            |
*		|                          120 | Chelmsford Main Desk                                         | 139401            |
*		|                            2 | Chelmsford Maternal Home Care                                | 138301            |
*		|                        66177 | Chelmsford Medical Records                                   | 138001            |
*		|                        41514 | Chelmsford MH-Combined                                       | 135501            |
*		|                         2063 | Chelmsford Nephrology                                        | 132301            |
*		|                         4831 | Chelmsford Neurolgy Adult                                    | 135901            |
*		|                         1327 | Chelmsford Nutrition                                         | 132501            |
*		|                        43109 | Chelmsford Obstetrics and Gynecology                         | 132601            |
*		|                        10381 | Chelmsford Ophthalmology                                     | 132901            |
*		|                        15513 | Chelmsford Optometry                                         | 133001            |
*		|                        14423 | Chelmsford Orthopedic Combined                               | 135601            |
	01824	|                       101248 | Chelmsford Pediatrics                                        | 133401            |
*		|                        10589 | Chelmsford Physical Therapy Combined                         | 133501            |
*		|                         2768 | Chelmsford Podiatry                                          | 133601            |
*		|                          930 | Chelmsford Pulmonary Medicine                                | 133801            |
*		|                          177 | Chelmsford Radiology                                         | 133901            |
*		|                            1 | Chelmsford Resource Department                               | 130101            |
*		|                          168 | Chelmsford Rheumatology                                      | 134001            |
*		|                         1607 | Chelmsford Speech Therapy                                    | 134101            |
*		|                         9413 | Chelmsford Surgery                                           | 134301            |
*		|                            3 | Chelmsford Translators                                       | 136901            |
*		|                            2 | Chelmsford Ultrasound                                        | 139101            |
	01824	|                           48 | Chelmsford Urgent Care Combined                              | 134901            |
	01824	|                        13796 | Chelmsford Urgent Care Pedi, After Hours                     | 134801            |
	01824	|                        10271 | Chelmsford Urgent Care Weekend Combined                      | 136101            |
*		|                         5007 | Chelmsford Urology                                           | 135301            |
*		|                          206 | Chelmsford Visual Services                                   | 135401            |
*		|                           28 | Clinical Pathology                                           | 351902            |
*		|                          408 | Concord Anticoagulation Program                              | 391806            |
*		|                          345 | Concord Case Management                                      | 398501            |
*		|                          284 | Concord Complex Chronic Care                                 | 390401            |
*		|                          377 | Concord Hillside Emerson Hospital Urological Gynecology      | 392601            |
	01742	|                         1942 | Concord Internal Medicine 1                                  | 391804            |
	01742	|                       109581 | Concord Internal Medicine A                                  | 391801            |
	01742	|                       104969 | Concord Internal Medicine B                                  | 391802            |
	01742	|                        84860 | Concord Internal Medicine D                                  | 391803            |
*		|                         1680 | Concord Laboratory                                           | 391901            |
*		|                         4373 | Concord Main Desk                                            | 399401            |
*		|                        46438 | Concord Medical Records                                      | 398001            |
*		|                         7365 | Concord MH-Combined                                          | 395501            |
	01742	|                       161753 | Concord Pediatrics                                           | 393401            |
*		|                         1640 | Concord Special Care Unit                                    | 391805            |
*		|                         1740 | Copley Anticoagulation Program                               | 141803            |
*		|                         1905 | Copley Behavioral Health                                     | 145501            |
*		|                           17 | Copley Case Management                                       | 148501            |
*		|                            5 | Copley ECF Rounding                                          | 148601            |
*		|                            1 | Copley Genetics                                              | 141501            |
*		|                            4 | Copley Infectious Disease                                    | 145801            |
*		|                           19 | Copley Intensive Home Based Program                          | 148602            |
	02116	|                       157148 | Copley Internal Med. A                                       | 141801            |
*		|                            6 | Copley Internal Medicine B                                   | 141802            |
*		|                          395 | Copley Laboratory                                            | 141901            |
*		|                           12 | Copley Main Desk                                             | 149401            |
*		|                          136 | Copley MH-Combined                                           | 145501            |
*		|                            4 | Copley Nutrition                                             | 142501            |
*		|                        45569 | Copley Obstetrics and Gynecology                             | 142601            |
*		|                            3 | Copley Pediatric Asthma Program                              | 147701            |
	02116	|                        49146 | Copley Pediatrics                                            | 143401            |
*		|                          291 | Copley Pharmacy                                              | 148701            |
*		|                            5 | Copley Radiology                                             | 143901            |
*		|                            3 | Copley Rheumatology                                          | 144001            |
*		|                         1026 | Copley Uterine Artery Embolization                           | 142603            |
*		|                           10 | Copley Vulvar Specialty                                      | 142602            |
*		|                            5 | Dedham Administration                                        | 701601            |
*		|                         8753 | Dedham Allergy                                               | 700201            |
*		|                           21 | Dedham Anticoagulation                                       | 701802            |
*		|                        23680 | Dedham Dermatology                                           | 701001            |
*		|                        18665 | Dedham Ears, Nose and Throat                                 | 701201            |
*		|                          150 | Dedham Endocrinology                                         | 701101            |
*		|                         1577 | Dedham Gastroenterology                                      | 701401            |
*		|                            1 | Dedham Information Systems                                   | 701602            |
	02026	|                       350425 | Dedham Internal Medicine                                     | 701801            |
*		|                        31499 | Dedham Laboratory                                            | 701901            |
*		|                        32876 | Dedham Medical Associates Obstetrics and Gynecology          | 042602            |
*		|                        81229 | Dedham Medical Records                                       | 708001            |
*		|                        43423 | Dedham Ophthalmology                                         | 702901            |
*		|                        31331 | Dedham Orthopedics, Combined                                 | 705601            |
	02026	|                       140722 | Dedham Pediatrics                                            | 703401            |
*		|                        10299 | Dedham Physiatry                                             | 705602            |
*		|                        17051 | Dedham Physical Therapy, Combined                            | 703501            |
*		|                         3039 | Dedham Podiatry                                              | 703601            |
*		|                         2131 | Dedham Radiology                                             | 703901            |
*		|                         4242 | Dedham Rheumatology                                          | 704001            |
*		|                         6305 | Dedham Surgery                                               | 704301            |
*		|                        16289 | Dedham Urology                                               | 705301            |
*		|                          971 | Dedham Vein & Aesthetic                                      | 701701            |
*		|                           17 | Dermatology - Providence                                     | 811431            |
*		|                            1 | Dermatology - Warwick                                        | 821431            |
*		|                            1 | Dermatology-Lincoln Ctr                                      | 851431            |
*		|                        31637 | DMA Norwood Obstetrics and Gynecology                        | 042605            |
*		|                            8 | Emergency Services-BWH                                       | 2001801           |
*		|                            5 | Family Practice - Plainville                                 | 831181            |
*		|                            1 | Family Practice - Swansea                                    | 841181            |
*		|                          130 | Faulkner Anticoagulation Program                             | 471802            |
*		|                            2 | Faulkner Cardiology                                          | 010402            |
*		|                           28 | Faulkner Case Management                                     | 478501            |
*		|                           53 | Faulkner Complex Chronic Care                                | 470401            |
	02130	|                        73897 | Faulkner Internal Medicine                                   | 471801            |
*		|                            2 | Faulkner Laboratory                                          | 471901            |
*		|                        12967 | Faulkner Neurology                                           | 105902            |
*		|                           55 | Faulkner Podiatry                                            | 103602            |
*		|                         6551 | Faulkner Surgery                                             | 104302            |
	01701	|                       118247 | Framingham Adult Medicine                                    | 721801            |
*		|                          486 | Framingham Allergy                                           | 720201            |
*		|                         4899 | Framingham Cardiology                                        | 720401            |
*		|                        30212 | Framingham Laboratory                                        | 721901            |
*		|                         4618 | Framingham Medical Records                                   | 728001            |
*		|                         1443 | Framingham Obstatrics and Gynecology                         | 722601            |
*		|                        29597 | Framingham Obstetrics and Gynecology                         | 722601            |
*		|                            2 | Framingham Orthopedics                                       | 725601            |
	01701	|                        11949 | Framingham Pediatrics                                        | 723401            |
*		|                          825 | Framingham Podiatry                                          | 723601            |
*		|                        11189 | Framingham Practice                                          | 723401            |
*		|                            1 | Franklin Street Obstetrics and Gynecology                    | 792601            |
*		|                            4 | Granite Cardiology                                           | 650401            |
*		|                            4 | Granite Coumadin                                             | 651804            |
*		|                            1 | Granite Gastroenterology                                     | 651401            |
	02169	|                            1 | Granite Internal Medicine - 2F                               | 651803            |
	02169	|                           13 | Granite Internal Medicine - 3A                               | 651801            |
	01451	|                        29264 | Harvard Pediatrics                                           | 463401            |
*		|                            9 | HVMA Clinical Assessment and Support Team                    | 358501            |
*		|                         1481 | HVMA Division of Medicine at Brigham and Womens              | 351801            |
*		|                         2222 | HVMA Division of Medicine at Mount Auburn Hospital           | 351802            |
*		|                          971 | HVMA Pediatrics at Children''s Hospital                      | 363401            |
*		|                          989 | HVMA Pediatrics at Children's Hospital                       | 363401            |
*		|                            3 | HVMA Utilization Management and Clinical Programs            | 28                |
*		|                          882 | Intensive Home Based Program                                 | 108602            |
*		|                          597 | Internal Medicine - Providence                               | 811101            |
*		|                            1 | Internal Medicine - Warwick                                  | 821101            |
*		|                         4994 | Kenmore - Infusion Unit                                      | 019201            |
*		|                            1 | Kenmore - Travel Medicine                                    | 019801            |
*		|                           16 | Kenmore Administration                                       | 011601            |
*		|                         4081 | Kenmore Allergy                                              | 010201            |
*		|                          576 | Kenmore Allergy, Pediatrics                                  | 010202            |
*		|                            4 | Kenmore Andrology                                            | 019601            |
*		|                        37054 | Kenmore Anticoagulation Program                              | 011805            |
*		|                            3 | Kenmore Audiology                                            | 010301            |
*		|                         7185 | Kenmore Behavioral Health                                    | 015501            |
*		|                        29180 | Kenmore BH Combined                                          | 015501            |
*		|                          194 | Kenmore BH F & E                                             | 015502            |
*		|                           47 | Kenmore BH Palliative Care                                   | 015503            |
*		|                           30 | Kenmore Bone Density                                         | 013905            |
*		|                        17289 | Kenmore Cardiology Testing                                   | 010601            |
*		|                        51849 | Kenmore Cardiology, Adult                                    | 010401            |
*		|                         2511 | Kenmore Cardiology, Pediatrics                               | 010501            |
*		|                         4213 | Kenmore Case Management                                      | 018501            |
*		|                            1 | Kenmore Cashier                                              | 019301            |
*		|                        38049 | Kenmore Complex Chronic Care                                 | 010403            |
*		|                         9459 | Kenmore Dental                                               | 010901            |
*		|                        25012 | Kenmore Dermatology                                          | 011001            |
*		|                           89 | Kenmore Diagnostic Technology Center CT Scan                 | 013903            |
*		|                          169 | Kenmore Diagnostic Technology Center MRI                     | 013902            |
*		|                            1 | Kenmore Diagnostic Technology Center Nuclear Medicine        | 013904            |
*		|                            2 | Kenmore Diagnostic Technology Center Ultrasound              | 013906            |
*		|                        23947 | Kenmore Ears, Nose and Throat                                | 011201            |
*		|                         1535 | Kenmore ECF Rounding                                         | 018601            |
*		|                        54359 | Kenmore Endocrinology                                        | 011101            |
*		|                           72 | Kenmore Endocrinology Complex Chronic Care                   | 011103            |
*		|                         1979 | Kenmore Endocrinology OB/Gyn                                 | 011102            |
*		|                        18023 | Kenmore Endoscopy Suite                                      | 011403            |
*		|                        31730 | Kenmore Fertility and Endocrinology                          | 011301            |
*		|                            2 | Kenmore Flex Sig Program                                     | 011402            |
*		|                        58495 | Kenmore Gastroenterology                                     | 011401            |
*		|                         3313 | Kenmore Genetics                                             | 011501            |
*		|                        17557 | Kenmore Hand Orthopedics                                     | 017501            |
*		|                         2275 | Kenmore Health Management Resources                          | 011806            |
*		|                          602 | Kenmore Intensive Home Based Program                         | 018602            |
	02215	|                       201894 | Kenmore Internal Medicine 4                                  | 011802            |
	02215	|                       194746 | Kenmore Internal Medicine 6E                                 | 011804            |
*		|                          839 | Kenmore Laboratory                                           | 011901            |
*		|                            1 | Kenmore Main Desk 1st Floor                                  | 019403            |
*		|                            1 | Kenmore Main Desk 4th Floor                                  | 019402            |
*		|                            2 | Kenmore Main Desk 5th Floor                                  | 019401            |
*		|                            9 | Kenmore Mammogram                                            | 012001            |
*		|                         7441 | Kenmore Mammography                                          | 012001            |
*		|                          857 | Kenmore Maternal Fetal Medicine                              | 012605            |
*		|                         4032 | Kenmore Medical Records                                      | 018001            |
*		|                            4 | Kenmore Menopause                                            | 011302            |
*		|                         2147 | Kenmore Menopause Consultation                               | 012604            |
*		|                           14 | Kenmore Mental Health Child                                  | 012201            |
*		|                         1228 | Kenmore MH Adult                                             | 012102            |
*		|                         1287 | Kenmore MH-Internal Medicine                                 | 011807            |
*		|                        13893 | Kenmore Nephrology                                           | 012301            |
*		|                          898 | Kenmore Neurology Testing                                    | 016801            |
*		|                        12041 | Kenmore Neurology, Adult                                     | 015901            |
*		|                         3292 | Kenmore Nutrition                                            | 012501            |
*		|                          668 | Kenmore ObGyn Urgent Care                                    | 012603            |
*		|                        57788 | Kenmore Obstetrics and Gynecology                            | 012602            |
*		|                        10313 | Kenmore Occupational Therapy                                 | 012701            |
*		|                        94849 | Kenmore Oncology                                             | 012801            |
*		|                        48790 | Kenmore Ophthalmology                                        | 012901            |
*		|                            3 | Kenmore Optical Services                                     | 019701            |
*		|                        16603 | Kenmore Optometry/Optical Service                            | 013001            |
*		|                        37247 | Kenmore Orthopedics, Combined                                | 015601            |
*		|                            2 | Kenmore Orthopedics, Pediatrics                              | 013201            |
*		|                            7 | Kenmore Pain                                                 | 013301            |
*		|                          344 | Kenmore Palliative Care                                      | 010001            |
	02215	|                       105046 | Kenmore Pediatrics A                                         | 013401            |
*		|                            1 | Kenmore Pharmacy                                             | 018701            |
*		|                        19688 | Kenmore Physical Therapy, Combined                           | 013501            |
*		|                         7873 | Kenmore Podiatry                                             | 013601            |
*		|                         8422 | Kenmore Pulmonary Medicine                                   | 013801            |
*		|                        11618 | Kenmore Radiology                                            | 013901            |
*		|                         5047 | Kenmore Rheumatology                                         | 014001            |
*		|                         4015 | Kenmore Speech Therapy                                       | 014101            |
*		|                          835 | Kenmore Spine Unit                                           | 015602            |
*		|                        28645 | Kenmore Surgery                                              | 014301            |
*		|                            2 | Kenmore Ultrasound                                           | 019101            |
	02215	|                            1 | Kenmore Urgent Care, After Hours, Adult                      | 014701            |
	02215	|                            1 | Kenmore Urgent Care, After Hours, Pediatrics                 | 014801            |
	02215	|                        41789 | Kenmore Urgent Care, Day, Adult                              | 015001            |
	02215	|                        22638 | Kenmore Urgent Care, Weekend/Holiday, Adult                  | 016401            |
	02215	|                        10274 | Kenmore Urgent Care, Weekend/Holiday, Pediatrics             | 016501            |
*		|                        10343 | Kenmore Urology                                              | 015301            |
*		|                            1 | Kingston Administration                                      | 771601            |
*		|                            1 | Kingston Allergy                                             | 770201            |
*		|                         3416 | Kingston Behavioral Health                                   | 775501            |
	02364	|                         4419 | Kingston Family Practice                                     | 771802            |
	02364	|                       204172 | Kingston Internal Medicine                                   | 771801            |
*		|                            5 | Kingston Laboratory                                          | 771901            |
*		|                        11568 | Kingston Medical Records                                     | 778001            |
*		|                        11472 | Kingston Obstetrics and Gynecology                           | 772601            |
*		|                         2795 | Kingston Orthopedics                                         | 775601            |
	02364	|                        59975 | Kingston Pediatrics                                          | 773401            |
*		|                          732 | Kingston Podiatry                                            | 773601            |
*		|                          650 | Kingston Radiology                                           | 773901            |
*		|                            2 | Kingston Surgery                                             | 774301            |
	02364	|                         4641 | Kingston Urgent Care                                         | 775001            |
*		|                           29 | Lab Administration                                           | 351903            |
	02189	|                           60 | Libbey Parkway Internal Medicine                             | 681801            |
*		|                            1 | Libbey Parkway Laboratory                                    | 681901            |
*		|                         1267 | Lynnfield Medical Associates Anticoagulation Program         | 431802            |
*		|                           67 | Lynnfield Medical Associates Case Management                 | 438501            |
	01960	|                       292048 | Lynnfield Medical Associates Internal Medicine               | 431801            |
*		|                            2 | Medford Administration                                       | 051601            |
*		|                         4493 | Medford Allergy                                              | 050201            |
*		|                        24904 | Medford Anticoagulation Program                              | 051803            |
*		|                         8875 | Medford Behavioral Health                                    | 055501            |
*		|                            1 | Medford Bone Density                                         | 053902            |
*		|                         3508 | Medford Cardiology, Combined                                 | 055701            |
*		|                          446 | Medford Case Management                                      | 058501            |
*		|                            9 | Medford Cashier                                              | 059301            |
*		|                         2022 | Medford Complex Chronic Care                                 | 050401            |
*		|                        15400 | Medford Dermatology                                          | 051001            |
*		|                         3845 | Medford Ears, Nose and Throat                                | 051201            |
*		|                          179 | Medford ECF Rounding                                         | 058601            |
*		|                            1 | Medford Endocrinology                                        | 051101            |
*		|                        18739 | Medford Gastroenterology                                     | 051401            |
*		|                          448 | Medford Intensive Home Based Program                         | 058602            |
*		|                          245 | Medford Internal Medicine Anti Coag Program                  | 051802            |
	02155	|                       303134 | Medford Internal Medicine B                                  | 051801            |
*		|                          400 | Medford Laboratory                                           | 051901            |
*		|                            4 | Medford Main Desk                                            | 059401            |
*		|                           34 | Medford Mammogram                                            | 052001            |
*		|                           20 | Medford Mammography                                          | 052001            |
*		|                            1 | Medford Maternal Home Care                                   | 058301            |
*		|                        44987 | Medford Medical Records                                      | 058001            |
*		|                          323 | Medford Menopause Consultation                               | 052603            |
*		|                        38581 | Medford MH,Combined                                          | 055501            |
*		|                         1042 | Medford Nephrology                                           | 052301            |
*		|                         2078 | Medford Nutrition                                            | 052501            |
*		|                        34170 | Medford Obstetrics and Gynecology                            | 052601            |
*		|                        11408 | Medford Ophthalmology                                        | 052901            |
*		|                        11393 | Medford Optometry/Optical Services                           | 053001            |
*		|                          639 | Medford Orthopedics, Combined                                | 055601            |
	02155	|                        74872 | Medford Pediatrics                                           | 053401            |
*		|                         6208 | Medford Podiatry                                             | 053601            |
*		|                          452 | Medford Radiology                                            | 053901            |
*		|                           22 | Medford Rheumatology                                         | 054001            |
*		|                         2309 | Medford Speech Therapy                                       | 054101            |
*		|                         6413 | Medford Surgery, General                                     | 054301            |
	02155	|                          947 | Medford Urgent Care, Day, Adult                              | 055001            |
*		|                         5101 | Medford Urology                                              | 055301            |
*		|                          343 | Medford Urology Gynecology                                   | 052602            |
*		|                           57 | Medical Billing Department                                   | 25                |
*		|                            2 | Medical Billing Department-Chelmsford                        | 30                |
*		|                           10 | Medical Billing Department-Riverside                         | 25                |
*		|                           11 | Meeting House Road OB/GYN Laboratory                         | 482604            |
*		|                        15872 | Meeting House Road Obstetrics and Gynecology                 | 482601            |
*		|                            2 | Mental Health - Providence                                   | 811501            |
*		|                           81 | Milford Medical Records                                      | 738001            |
	01757	|                        27198 | Milford Pediatrics                                           | 733401            |
*		|                           99 | Milford Podiatry                                             | 733601            |
*		|                            7 | Natick Medical Records                                       | 748001            |
*		|                        16095 | Natick Obstetrics and Gynecology                             | 742601            |
*		|                         2574 | Norwell Administration                                       | 781601            |
*		|                         5514 | Norwell Allergy                                              | 780201            |
*		|                          509 | Norwell Behavioral Health                                    | 785501            |
*		|                            1 | Norwell Call Center                                          | 781603            |
*		|                        14852 | Norwell Dermatology                                          | 781001            |
	02061	|                        53868 | Norwell Family Practice                                      | 781802            |
*		|                            2 | Norwell Information Systems                                  | 781602            |
	02061	|                       292452 | Norwell Internal Medicine                                    | 781801            |
*		|                           10 | Norwell Laboratory                                           | 781901            |
*		|                        95458 | Norwell Medical Records                                      | 788001            |
*		|                        19110 | Norwell Obstetrics and Gynecology                            | 782601            |
*		|                        14508 | Norwell Orthopedics                                          | 785601            |
	02061	|                       159423 | Norwell Pediatrics                                           | 783401            |
*		|                         7689 | Norwell Podiatry                                             | 783601            |
*		|                           18 | Norwell Radiology                                            | 783901            |
*		|                         8029 | Norwell Surgery                                              | 784301            |
	02061	|                        34135 | Norwell Urgent Care                                          | 785001            |
*		|                            4 | Norwood Administration                                       | 711601            |
*		|                         3519 | Norwood Dermatology                                          | 711001            |
*		|                            1 | Norwood Information Systems                                  | 711602            |
	02062	|                       206118 | Norwood Internal Medicine                                    | 711801            |
*		|                        16998 | Norwood Laboratory                                           | 711901            |
*		|                           98 | Norwood Medical Records                                      | 718001            |
	02062	|                       126443 | Norwood Pediatrics                                           | 713401            |
*		|                            1 | Norwood Radiology                                            | 713901            |
*		|                            1 | Obstetrics and Gynecology - Providence                       | 811301            |
*		|                            1 | Obstetrics and Gynecology - Swansea                          | 841301            |
*		|                            2 | Obstetrics/Gynecology - Lincoln Center                       | 851301            |
*		|                            1 | Optometry - Warwick                                          | 821661            |
*		|                            1 | Orthopedics - Providence                                     | 813731            |
*		|                         2741 | Peabody Allergy                                              | 070201            |
*		|                        17242 | Peabody Anticaogulation Program                              | 071803            |
*		|                         5251 | Peabody Behavioral Health                                    | 075501            |
*		|                          298 | Peabody Cardiology                                           | 070402            |
*		|                          393 | Peabody Case Management                                      | 078501            |
*		|                          928 | Peabody Complex Chronic Care                                 | 070401            |
*		|                         2315 | Peabody Dental                                               | 070901            |
*		|                         3828 | Peabody Dermatology                                          | 071001            |
*		|                         2216 | Peabody Ears, Nose and Throat                                | 071201            |
*		|                         4066 | Peabody Endocrinolgy Department                              | 071101            |
*		|                            2 | Peabody Extended Care Facility Rounding                      | 078601            |
*		|                         2948 | Peabody General Surgery                                      | 074301            |
*		|                            3 | Peabody Infectious Disease                                   | 075801            |
	01961	|                       154418 | Peabody Internal Medicine A                                  | 071801            |
*		|                         1540 | Peabody Laboratory                                           | 071901            |
*		|                            5 | Peabody Mammography                                          | 072001            |
*		|                           32 | Peabody Medical Records                                      | 078001            |
*		|                        22269 | Peabody MH-Combined                                          | 075501            |
*		|                            5 | Peabody Neonatology                                          | 078401            |
*		|                         2134 | Peabody Neurology                                            | 075901            |
*		|                         1306 | Peabody Nutrition                                            | 072501            |
*		|                         8106 | Peabody Obstetrics and Gynecology                            | 072601            |
*		|                         6246 | Peabody Ophthalmology                                        | 072901            |
*		|                         7749 | Peabody Optometry                                            | 073001            |
*		|                         9557 | Peabody Orthopedics                                          | 075601            |
	01961	|                        49328 | Peabody Pediatrics                                           | 073401            |
*		|                           17 | Peabody Pharmacy                                             | 078701            |
*		|                         8839 | Peabody Physical Therapy Combined                            | 073501            |
*		|                           33 | Peabody Radiology                                            | 073901            |
*		|                            2 | Peabody Resource Department                                  | 070101            |
*		|                        13304 | Peabody Rheumatology                                         | 074001            |
*		|                            7 | Peabody Ultrasound                                           | 079101            |
	01961	|                        15035 | Peabody Urgent Care Weekends, Combined                       | 076101            |
	01961	|                          270 | Peabody Urgent Care Weekends, Pediatrics                     | 076501            |
	01961	|                            1 | Peabody Urgent Care, After Hours, Combined                   | 074901            |
*		|                          173 | Peabody Urology                                              | 075301            |
*		|                        46743 | Pediatric Telecomm - Children''s Hospital                    | 2014801           |
*		|                        19606 | Pediatric Telecomm - Children's Hospital                     | 2014801           |
*		|                            6 | Pediatrics - Lincoln Center                                  | 851201            |
*		|                            1 | Post Office Square Administration                            | 081601            |
*		|                            4 | Post Office Square Adult Cardiology                          | 080401            |
*		|                        13002 | Post Office Square Allergy                                   | 080201            |
*		|                         4190 | Post Office Square Anticoagulation Program                   | 081803            |
*		|                        10127 | Post Office Square Behavioral Health                         | 085501            |
*		|                            2 | Post Office Square Cashier                                   | 089301            |
*		|                         6777 | Post Office Square Contact Lens                              | 080701            |
*		|                        11168 | Post Office Square Dermatology                               | 081001            |
*		|                            1 | Post Office Square Ear, Nose, and Throat                     | 081201            |
	02109	|                       101114 | Post Office Square Internal Medicine 5                       | 081801            |
	02109	|                       122571 | Post Office Square Internal Medicine 6                       | 081802            |
	02109	|                         1756 | Post Office Square Internal Medicine 7                       | 081804            |
*		|                          677 | Post Office Square Laboratory                                | 081901            |
*		|                            3 | Post Office Square Main Desk                                 | 089401            |
*		|                            4 | Post Office Square Medical Records                           | 088001            |
*		|                        38447 | Post Office Square MH                                        | 085501            |
*		|                          935 | Post Office Square Nutrition                                 | 082501            |
*		|                        42349 | Post Office Square Obstetrics and Gynecology                 | 082601            |
*		|                            2 | Post Office Square Ophthalmology                             | 082901            |
*		|                         1433 | Post Office Square Optmetry                                  | 083001            |
*		|                         4919 | Post Office Square Optometry                                 | 083001            |
*		|                         5670 | Post Office Square Orthopedics Combined                      | 085601            |
*		|                         1827 | Post Office Square Surgery                                   | 084301            |
	02109	|                            2 | Post Office Square Urgent Care                               | 085001            |
*		|                            6 | Post Office Square Visual Services                           | 085401            |
*		|                            3 | Post Office Square Vulvar Specialty                          | 082602            |
*		|                            3 | Quincy Administration                                        | 031601            |
*		|                         6761 | Quincy Allergy                                               | 030201            |
*		|                         5179 | Quincy Anticoagulation Program                               | 031802            |
*		|                         8550 | Quincy Behavioral Health                                     | 035501            |
*		|                           72 | Quincy BH-Internal Medicine                                  | 035503            |
*		|                         1846 | Quincy Cardiology, Combined                                  | 035701            |
*		|                          726 | Quincy Case Management                                       | 038501            |
*		|                            1 | Quincy Cashier                                               | 039301            |
*		|                         2058 | Quincy Complex Chronic Care                                  | 030401            |
*		|                          610 | Quincy Contact Lens                                          | 030701            |
*		|                        18892 | Quincy Dermatology                                           | 031001            |
*		|                         3954 | Quincy Ears, Nose and Throat                                 | 031201            |
*		|                            3 | Quincy ECF Rounding                                          | 038601            |
*		|                         7619 | Quincy Fertility and Endocrinology                           | 031301            |
*		|                          179 | Quincy Flexible Sigmoidoscopy                                | 031402            |
*		|                        19872 | Quincy Gastroenterology                                      | 031401            |
*		|                          899 | Quincy Health Promotion                                      | 037801            |
	02170	|                       187597 | Quincy Internal Medicine                                     | 031801            |
*		|                          220 | Quincy Laboratory                                            | 031901            |
*		|                           23 | Quincy Mammogram                                             | 032001            |
*		|                           27 | Quincy Mammography                                           | 032001            |
*		|                          247 | Quincy Maternal Fetal Medicine                               | 032607            |
*		|                        31329 | Quincy MH-Combined                                           | 035501            |
*		|                          124 | Quincy MH-Internal Medicine                                  | 035503            |
*		|                            1 | Quincy Neonatology                                           | 038401            |
*		|                           66 | Quincy Nutrition                                             | 032501            |
*		|                        66851 | Quincy Obstetrics and Gynecology                             | 032605            |
*		|                            4 | Quincy Oncology                                              | 032801            |
*		|                         4085 | Quincy Ophthalmology                                         | 032901            |
*		|                        11105 | Quincy Optometry/Optical Services                            | 033001            |
*		|                         9532 | Quincy Orthopedics, Combined                                 | 035601            |
	02170	|                        75750 | Quincy Pediatrics                                            | 033401            |
*		|                            2 | Quincy Pharmacy                                              | 038701            |
*		|                            1 | Quincy Podiatry                                              | 033601            |
*		|                         1546 | Quincy Pulmonary                                             | 033801            |
*		|                          816 | Quincy Radiology                                             | 033901            |
*		|                            1 | Quincy Special Procedures Unit                               | 037901            |
*		|                         2396 | Quincy Speech Therapy                                        | 034101            |
*		|                         3495 | Quincy Surgery, General                                      | 034301            |
*		|                            3 | Quincy Ultrasound                                            | 039101            |
*		|                         5635 | Quincy Urology                                               | 035301            |
*		|                         3454 | Quincy Urology Gynecology                                    | 032606            |
*		|                           43 | Quincy Uterine Artery Embolization                           | 032608            |
*		|                            1 | Radiology - Warwick                                          | 822201            |
*		|                           14 | Riverside Healthy Living                                     | 307801            |
*		|                        36208 | Somerville Adult Orthopedics                                 | 153101            |
*		|                        36448 | Somerville Adult Physical Therapy                            | 156601            |
*		|                        12537 | Somerville Allergy                                           | 150201            |
*		|                         3579 | Somerville Anticoagulation Program                           | 151802            |
*		|                         3705 | Somerville Behavioral Health                                 | 155501            |
*		|                         1372 | Somerville Cardiology, Combined                              | 155701            |
*		|                           46 | Somerville Case Management                                   | 158501            |
*		|                         1100 | Somerville Complex Chronic Care                              | 150401            |
*		|                        10636 | Somerville Contact Lens                                      | 150701            |
*		|                            2 | Somerville Conversion                                        | 159999            |
*		|                            1 | Somerville Dental                                            | 150901            |
*		|                        11995 | Somerville Dermatology                                       | 151001            |
*		|                         6876 | Somerville Developmental Consultation Services               | 156301            |
*		|                            3 | Somerville Ears, Nose and Throat                             | 151201            |
*		|                           51 | Somerville ECF Rounding                                      | 158601            |
*		|                            1 | Somerville Gastroenterology                                  | 151401            |
*		|                        12384 | Somerville General Surgery                                   | 154301            |
*		|                           79 | Somerville Intensive Home Based Program                      | 158602            |
	02144	|                       140928 | Somerville Internal Medicine                                 | 151801            |
*		|                          224 | Somerville Laboratory                                        | 151901            |
*		|                        14937 | Somerville Laser Surgery                                     | 156201            |
*		|                          520 | Somerville Laser Vision Correction Program                   | 155401            |
*		|                            7 | Somerville Mammogram                                         | 152001            |
*		|                           75 | Somerville Mammography                                       | 152001            |
*		|                            1 | Somerville Maternal Home Care                                | 158301            |
*		|                          620 | Somerville Medical Records                                   | 158001            |
*		|                        15383 | Somerville MH, Combined                                      | 155501            |
*		|                            3 | Somerville Neonatology                                       | 158401            |
*		|                         8239 | Somerville Neurology, Combined                               | 152401            |
*		|                         2420 | Somerville Nutrition                                         | 152501            |
*		|                        32899 | Somerville Obstetrics and Gynecology                         | 152601            |
*		|                        19692 | Somerville Ophthalmology                                     | 152901            |
*		|                            4 | Somerville Optical Services                                  | 159701            |
*		|                        13786 | Somerville Optometry/Optical Service                         | 153001            |
*		|                            1 | Somerville Pediatric Asthma Program                          | 157701            |
*		|                          778 | Somerville Pediatric Immunizations                           | 150101            |
*		|                           23 | Somerville Pediatric Neurology                               | 156001            |
*		|                         1314 | Somerville Pediatric Physical Therapy                        | 156701            |
	02144	|                        47597 | Somerville Pediatrics                                        | 153401            |
*		|                         1145 | Somerville Radiology                                         | 153901            |
*		|                            4 | Somerville Resource Department                               | 150102            |
*		|                        10367 | Somerville Rheumatology                                      | 154001            |
*		|                          908 | Somerville Speech Therapy                                    | 154101            |
*		|                          542 | Somerville Spine Unit                                        | 153102            |
*		|                            8 | Somerville Translator Department                             | 156901            |
*		|                            2 | Somerville Ultrasound                                        | 159101            |
	02144	|                        26724 | Somerville Urgent Care, Weekend/Holiday, Adult               | 156401            |
	02144	|                        16410 | Somerville Urgent Care, Weekend/Holiday, Pediatrics          | 156501            |
*		|                         6000 | Somerville Urology                                           | 155301            |
*		|                          320 | Somerville Urology Gynecology                                | 152603            |
*		|                          258 | Southboro Administration                                     | 751602            |
	01772	|                       216714 | Southboro Adult Medicine                                     | 751801            |
*		|                         5944 | Southboro Allergy                                            | 750201            |
*		|                         8708 | Southboro Business Office                                    | 751601            |
*		|                            3 | Southboro Central Check In                                   | 759401            |
*		|                        26265 | Southboro Counseling Services                                | 755501            |
*		|                         5544 | Southboro Dermatology                                        | 751001            |
*		|                           99 | Southboro Ears Nose and Throat                               | 751201            |
*		|                           17 | Southboro Endocrinology                                      | 751101            |
*		|                            1 | Southboro Hospital                                           | 754301            |
*		|                        45072 | Southboro Laboratory                                         | 751901            |
*		|                          181 | Southboro Mammography                                        | 752001            |
*		|                        23056 | Southboro Medical of Framingham                              | 723401            |
*		|                        39895 | Southboro Medical Records                                    | 758001            |
*		|                        27254 | Southboro Obstetrics and Gynecology                          | 752601            |
*		|                          589 | Southboro Optical Shop                                       | 759701            |
*		|                           14 | Southboro Orthopedics                                        | 755601            |
	01772	|                       115799 | Southboro Pediatrics                                         | 753401            |
*		|                          379 | Southboro Plastic Surgery                                    | 751701            |
*		|                        10188 | Southboro Podiatry                                           | 753601            |
*		|                          189 | Southboro Radiology                                          | 753901            |
*		|                         6936 | Southboro Rheumatology                                       | 754001            |
	01772	|                         3472 | Southboro Urgent Care                                        | 755001            |
*		|                        13561 | Southboro Visual Services                                    | 755401            |
	01776	|                        15398 | Sudbury Internal Medicine                                    | 511801            |
*		|                            1 | Surgery - Providence                                         | 813751            |
*		|                            1 | Urgent Care - Providence                                     | 814711            |
*		|                            1 | Urgent Care - Warwick                                        | 824711            |
*		|                          260 | Watertown Allergy                                            | 120201            |
*		|                        19171 | Watertown Anticoagulation Program                            | 121803            |
*		|                         5630 | Watertown Behavioral Health                                  | 125501            |
*		|                         1699 | Watertown Case Management                                    | 128501            |
*		|                            1 | Watertown Cashier                                            | 129301            |
*		|                          309 | Watertown Complex Chronic Care                               | 120401            |
*		|                           39 | Watertown Dermatology                                        | 121002            |
*		|                           13 | Watertown ECF Rounding                                       | 128601            |
*		|                            3 | Watertown Hand Orthopedics                                   | 127501            |
*		|                           18 | Watertown Intensive Home Based Program                       | 128602            |
	02472	|                       162965 | Watertown Internal Medicine                                  | 121801            |
*		|                          171 | Watertown Laboratory                                         | 121901            |
*		|                           19 | Watertown Main Desk                                          | 129401            |
*		|                          843 | Watertown Menopause Consultation                             | 122602            |
*		|                        20291 | Watertown MH,Combined                                        | 125501            |
*		|                           12 | Watertown Neurology, Combined                                | 122401            |
*		|                         1047 | Watertown Nutrition                                          | 122501            |
*		|                        15801 | Watertown Obstetrics and Gynecology                          | 122601            |
*		|                         3436 | Watertown Optometry/Optical Service                          | 123001            |
*		|                         2790 | Watertown Orthopedics, Combined                              | 125601            |
*		|                            5 | Watertown Pediatric Asthma Program                           | 127701            |
	02472	|                        70528 | Watertown Pediatrics                                         | 123401            |
*		|                            2 | Watertown Pharmacy                                           | 128701            |
*		|                        11015 | Watertown Physical Therapy, Combined                         | 123501            |
*		|                         2205 | Watertown Podiatry                                           | 123601            |
*		|                            2 | Watertown Radiology                                          | 123901            |
*		|                           21 | Watertown Surgery, General                                   | 124301            |
	02472	|                            1 | Watertown Urgent Care, After Hours, Adult                    | 124701            |
*		|                        10799 | Wellesley Allergy                                            | 040201            |
*		|                            6 | Wellesley Andrology                                          | 049601            |
*		|                        24982 | Wellesley Anticoagulation Program                            | 041804            |
*		|                        15006 | Wellesley Behavioral Health                                  | 045501            |
*		|                            6 | Wellesley BH Palliative Care                                 | 045502            |
*		|                         4838 | Wellesley Cardiology, Combined                               | 045701            |
*		|                          566 | Wellesley Care Management                                    | 048501            |
*		|                          801 | Wellesley Complex Chronic Care                               | 040401            |
*		|                         2842 | Wellesley Cosmetic Surgery                                   | 041202            |
*		|                        25849 | Wellesley Dermatology                                        | 041001            |
*		|                        18813 | Wellesley Ear, Nose and Throat                               | 041201            |
*		|                           49 | Wellesley ECF Rounding                                       | 048601            |
*		|                         4671 | Wellesley Endocrinology                                      | 041101            |
*		|                        10449 | Wellesley Fertility and Endocrinology                        | 041301            |
*		|                         8004 | Wellesley Gastroenterology                                   | 041401            |
*		|                         6668 | Wellesley General Surgery                                    | 044301            |
*		|                         1199 | Wellesley Intensive Home Based Program                       | 048602            |
	02481	|                       113081 | Wellesley Internal Medicine A                                | 041801            |
	02481	|                       162985 | Wellesley Internal Medicine B                                | 041802            |
	02481	|                       112791 | Wellesley Internal Medicine C                                | 041803            |
*		|                          691 | Wellesley Laboratory                                         | 041901            |
*		|                           11 | Wellesley Main Reception                                     | 049401            |
*		|                           46 | Wellesley Mammography                                        | 042001            |
*		|                            1 | Wellesley Maternal Home Care                                 | 048301            |
*		|                            1 | Wellesley Medical Records                                    | 048001            |
*		|                            7 | Wellesley Menopause Consultation                             | 042604            |
*		|                            2 | Wellesley Mental Health - Adult                              | 042101            |
*		|                        56033 | Wellesley MH-Combined                                        | 045501            |
*		|                            3 | Wellesley Neonatology                                        | 048401            |
*		|                        17385 | Wellesley Neurology-Adult                                    | 045901            |
*		|                         2451 | Wellesley Nutrition                                          | 042501            |
*		|                        54948 | Wellesley Obstetrics and Gynecology                          | 042601            |
*		|                         7188 | Wellesley Ophthalmology                                      | 042901            |
*		|                        16044 | Wellesley Optometry/Optical Services                         | 043001            |
*		|                        26611 | Wellesley Orthopedics Combined                               | 045601            |
*		|                           43 | Wellesley Orthopedics, Pediatrics                            | 043201            |
*		|                            2 | Wellesley Palliative Care                                    | 040001            |
*		|                            2 | Wellesley Pediatric Asthma Program                           | 047701            |
	02481	|                       106546 | Wellesley Pediatrics                                         | 043401            |
*		|                            1 | Wellesley Physical Therapy Combined                          | 043501            |
*		|                         2813 | Wellesley Podiatry                                           | 043601            |
*		|                          495 | Wellesley Radiology                                          | 043901            |
*		|                            1 | Wellesley Resource Department                                | 040101            |
*		|                          609 | Wellesley Rheumatology                                       | 044001            |
*		|                         1582 | Wellesley Speech Therapy                                     | 044101            |
*		|                           60 | Wellesley Spine Unit                                         | 045602            |
	02481	|                         5452 | Wellesley Urgent Care - Adult After Hours                    | 044701            |
	02481	|                          512 | Wellesley Urgent Care - Pediatrics After Hours               | 044801            |
	02481	|                        25202 | Wellesley Urgent Care - Weekend Adult                        | 046401            |
	02481	|                        16706 | Wellesley Urgent Care - Weekend Pediatrics                   | 046501            |
*		|                         5306 | Wellesley Urology                                            | 045301            |
*		|                         1164 | Wellesley Urology Gynecology                                 | 042603            |
	02115	|                         4704 | Wentworth Urgent Care                                        | 015002            |
*		|                            1 | West Roxbury Administration                                  | 101601            |
*		|                         5074 | West Roxbury Allergy                                         | 100201            |
*		|                        24790 | West Roxbury Anticoagulation Program                         | 101803            |
*		|                         9529 | West Roxbury Behavioral Health                               | 105501            |
*		|                            2 | West Roxbury Cardiology B                                    | 100402            |
*		|                         2230 | West Roxbury Cardiology Department                           | 100401            |
*		|                          515 | West Roxbury Case Management                                 | 108501            |
*		|                         1393 | West Roxbury Complex Chronic Care                            | 100403            |
*		|                         9679 | West Roxbury Dermatology                                     | 101001            |
*		|                           60 | West Roxbury Ears, Nose and Throat                           | 101201            |
*		|                           35 | West Roxbury ECF Rounding                                    | 108601            |
*		|                        14067 | West Roxbury Endocrinology                                   | 101101            |
*		|                            1 | West Roxbury Fertility and Endocrinology                     | 101301            |
*		|                         4558 | West Roxbury Gastroenterology                                | 101401            |
*		|                         6396 | West Roxbury General Surgery                                 | 104301            |
	02467	|                       137436 | West Roxbury Internal Medicine A                             | 101801            |
	02467	|                       114224 | West Roxbury Internal Medicine B                             | 101802            |
*		|                          645 | West Roxbury Laboratory                                      | 101901            |
*		|                           15 | West Roxbury Main Desk                                       | 109401            |
*		|                          105 | West Roxbury Mammography                                     | 102001            |
*		|                          164 | West Roxbury Menopause Consultation                          | 102604            |
*		|                        37172 | West Roxbury MH Combined                                     | 105501            |
*		|                            3 | West Roxbury Neurology, Adult                                | 105901            |
*		|                         1850 | West Roxbury Nutrition                                       | 102501            |
*		|                        39358 | West Roxbury Obstetrics and Gynecology                       | 102601            |
*		|                        13746 | West Roxbury Ophthalmology                                   | 102901            |
*		|                            1 | West Roxbury Optical Services                                | 109701            |
*		|                        13375 | West Roxbury Optometry/Optical Services                      | 103001            |
*		|                        27353 | West Roxbury Orthopedics, Adult                              | 103101            |
*		|                            1 | West Roxbury Palliative Care                                 | 100001            |
*		|                            8 | West Roxbury Pediatric Asthma Program                        | 107701            |
	02467	|                        98397 | West Roxbury Pediatrics                                      | 103401            |
*		|                            3 | West Roxbury Pharmacy                                        | 108701            |
*		|                        19930 | West Roxbury Physical Therapy, Combined                      | 103501            |
*		|                         3007 | West Roxbury Podiatry                                        | 103601            |
*		|                         2396 | West Roxbury Pulmonary Medicine                              | 103801            |
*		|                          116 | West Roxbury Radiology                                       | 103901            |
*		|                            1 | West Roxbury Resource Department                             | 100101            |
*		|                         7371 | West Roxbury Rheumatology                                    | 104001            |
*		|                           87 | West Roxbury Special Procedures Unit                         | 107901            |
*		|                          735 | West Roxbury Spine Unit                                      | 103102            |
	02467	|                            2 | West Roxbury Urgent Care, After Hours, Pediatrics            | 104801            |
*		|                         4718 | West Roxbury Urology                                         | 105301            |
*		|                         2540 | West Roxbury Urology Gynecology                              | 102603            |
*		|                          487 | Westboro Counseling Services                                 | 765501            |
*		|                          767 | Westboro Laboratory                                          | 761901            |
*		|                            9 | Westboro Medical Records                                     | 768001            |
*		|                        13368 | Westboro Obstetrics and Gynecology                           | 762601            |
	01581	|                        45975 | Westboro Pediatrics                                          | 763401            |
*		|                            9 | WEYMOUTH WOODS BONE DENSITY                                  | 523903            |
*		|                          145 | Weymouth Woods CT Scan                                       | 523901            |
*		|                            3 | Weymouth Woods Lab                                           | 671901            |
*		|                          488 | WEYMOUTH WOODS MAMMOGRAPHY                                   | 522001            |
*		|                           51 | WEYMOUTH WOODS NUTRITION                                     | 522501            |
*		|                          235 | Weymouth Woods Radiology Oncology                            | 523902            |
*		|                          148 | WEYMOUTH WOODS ULTRASOUND                                    | 529101            |
*		|                            4 | WEYMOUTH WOODS ULTRASOUND KINGSTON                           | 529102            |
""".split('\n')
localSiteAllSites = [x.split('|') for x in localSiteSites[2:] if len(x.split('|')) > 3] # drop header
localSiteAllSites = [[x[2].strip(),x[3].strip(),x[0].strip()] for x in localSiteAllSites] # name,code,ignore
localSiteAllCodes = [x[1] for x in localSiteAllSites] # code
localSiteAllNames = [x[0] for x in localSiteAllSites] # name
localSiteLookup = dict(zip(localSiteAllCodes,localSiteAllNames))
localSiteUse = [[x[0],x[1],x[2]] for x in localSiteAllSites if (x[2] <> '*')] # name, code, zip all not ignored codes
localSiteUseCodes = [x[1] for x in localSiteUse] # code is second
localSiteUseDict = dict(zip(localSiteUseCodes,localSiteUse)) # can lookup - use only found
localSiteExcludeCodes = [x[1] for x in localSiteAllSites if (x[2] == '*')] # used for volume cleaning
localSiteZ = [x[2] for x in localSiteUse]
localSiteZips = dict(zip(localSiteUseCodes,localSiteZ))


## Fever codes
# List of icd9 codes that indicate a fever event, regardless of measured temperature
ICD9_FEVER_CODES = ['780.6','780.31']


# atrius sites list code,name,ignore

# MDPH definition of ILI
"""
2) One of the following under the conditions specified:
a) Measured fever of at least 100F (in temperature field of database)
OR, if and only if there is no valid measured temperature of any magnitude,
b) ICD9 code of 780.6 (fever)
Note febrile convulsion added sometimes?
ICD9 code 780.31 (Febrile Convulsions)
"""
influenza_like_illness="""079.3	RHINOVIRUS INFECT NOS
079.89	OTHER SPECIFIED VIRAL INFECTION
079.99	UNSPECIFIED VIRAL INFECTION
460	NASOPHARYNGITIS, ACUTE
462	PHARYNGITIS, ACUTE NOS
464.00	LARYNGITIS, AC.W/O OBSTRU
464.01	LARYNGITIS, AC.W/OBSTRUCT
464.10	TRACHEITIS W/O OBSTRUCTIO
464.11	AC TRACHEITIS W OBSTRUCT
464.20	LARYNGOTRACHEITIS W/O OBS
464.21	AC LARYNGOTRACH W OBSTR
465.0	LARYNGOPHARYNGITIS, ACUTE
465.8	URI, OTHER MULT. SITES
465.9	URI, ACUTE  NOS
466.0	BRONCHITIS ACUTE
466.19	BRONCHIOLITIS DUE OTHER ORG'S
478.9	RESPIRATORY TRACT DISEASE
480.8	VIRAL PNEUMONIA NEC
480.9	PNEUMONIA, VIRAL
481	PNEUMOCOCCAL PNEUMONIA (L
482.40	STAPH PNEUMONIA NOS
482.41	PNEUMONIA, STAPHYLOCOC. A
482.49	OTH STAPH PNEUMONIA
484.8	PNEUM IN INFECT DIS NEC
485	BRONCHOPNEUMONIA ORGANISM
486	PNEUMONIA, ORGANISM NOS
487.0	INFLUENZA WITH PNEUMONIA
487.1	INFLUENZA W/OTH. RESP. MA
487.8	INFLUENZA W/OTHR MANIFEST
784.1	PAIN IN THROAT
786.2	COUGH""".split('\n')
influenza_like_illness = [x.split('\t') for x in influenza_like_illness]
influenza_like_illness = [[x[0],True] for x in influenza_like_illness] # always want a fever

haematological="""	ICD9CM	ICD9DESCR	EMA	Hrvd	NCA	Consensus	FeverReq
HEM	287.1	PLATELET DISORDER	129	1	77	1	x	x
HEM	287.2	NONTHROMBOCYTOPENIC PURPU	30	7	60	1	x	x
HEM	287.8	HEMORRHAGIC COND NEC	0	0	3	1	x	x
HEM	287.9	HEMORRHAGIC CONDITIONS UN	96	9	56	1	x	x
HEM	790.01	HEMATOCRIT, PRECIPITOUS D	2	0	1	1	x	x
HEM	790.92	ABNORMAL COAGULATION PROF	166	0	72	1	x	x
HEM	286.9	COAGULATION DEFECTS-UNSPE	1468	0	391	2	x	x
HEM	287.3	THROMBOCYTOPENIA	941	110	828	2	xx	x
HEM	287.4	THROMBOCYTOPENIA SECONDAR	0	0	147	2	x	x
HEM	287.5	THROMBOCYTOPENIA  UNSPEC.	612	37	314	2	x	x
HEM	459.0	HEMORRHAGE  NOS	1120	0	36	2	x	x
HEM	578.0	HEMATEMESIS	1017	7	123	2	*	x	x
HEM	578.1	MELENA	1377	0	2346	2	*	x	x
HEM	578.9	GASTROINTESTINAL HEMORRHA	22191	0	1608	2	*	x	x
HEM	782.7	ECCHYMOSIS,SPONTANEOUS,NO	1110	3	92	2	x	x
HEM	784.7	EPISTAXIS	16613	0	1613	2	*	x	x
HEM	784.8	HEMORRHAGE FROM THROAT	56	0	9	2	*	x	x
HEM	786.3	HEMOPTYSIS	2277	68	313	2	*	x	x
HEM	061	DENGUE	1	0	18	3	x	x
HEM	065.0	CRIMEAN HEMORRHAGIC FEV	0	0	0	3	x	x
HEM	065.1	OMSK HEMORRHAGIC FEVER	0	0	0	3	x	x
HEM	065.2	KYASANUR FOREST DISEASE	0	0	0	3	x	x
HEM	065.3	TICK-BORNE HEM FEVER NEC	0	0	4	3	x
HEM	065.4	MOSQUITO-BORNE HEM FEVER	0	0	1	3	x
HEM	065.8	ARTHROPOD HEM FEVER NEC	0	0	0	3	x	x
HEM	065.9	ARTHROPOD HEM FEVER NOS	0	0	0	3	x	x
HEM	077.4	EPIDEM HEM CONJUNCTIVIT	0	0	5	3	x	x
HEM	078.6	HEM NEPHROSONEPHRITIS	0	0	2	3	x	x
HEM	078.7	ARENAVIRAL HEM FEVER	0	0	0	3	x	x
HEM	084.8	BLACKWATER FEVER	0	0	0	3	x	x
HEM	100.0	LEPTOSPIROSIS, ICTOHEMORRHAGICA				3	x
HEM	283.11	HEMOLYTIC-UREMIC SYNDROME	4	0	6	3	x	x	""".split('\n')
haematological = [x.split('\t') for x in haematological[1:]] # ignore header
haematological = [[x[1].strip(),(x[7].strip()=='*')] for x in haematological]

lesions = """	ICD9CM	ICD9DESCR	EMA	Hrvd	NCA	Consensus
LESION	911.4	Superficial inj/trunk, insect bite non-veno, no infect				3
LESION	911.5	Superficial inj/trunk, insect bite non-veno, infection				3
LESION	912.4	Superficial inj/shoulder/upper arm, insect bite non-veno, no infect				3
LESION	912.5	Superficial inj/shoulder/upper arm, insect bite non-veno, infection				3
LESION	913.4	Superficial inj/elbow,forearm,wrist, insect bite non-veno, no infect				3
LESION	913.5	Superficial inj/elbow,forearm,wrist, insect bite non-veno, infection				3
LESION	915.4	Superficial inj/finger(s), insect bite non-veno, no infect				3
LESION	915.5	Superficial inj/finger(s) insect bite non-veno, infection				3
LESION	916.4	Superficial inj/hip,thigh,leg,ankle, insect bite non-veno, no infect				3
LESION	916.5	Superficial inj/hip,thigh,leg,ankle insect bite non-veno, infection				3
LESION	917.4	Superficial inj/foot, toe(s), insect bite non-veno, no infect				3
LESION	917.5	Superficial inj/foot, toe(s), insect bite non-veno, infection				3
LESION	918	Superficial inj/eyelids, periocular area, insect bite 				3
LESION	919.4	Superficial inj/other,multiple,unspec insect bite non-veno, no infect				3
LESION	919.5	Superficial inj/other, multiple, unspec insect bite non-veno, infection				3
LESION	E906.4	Bite of non-venomous arthropod/insect bite NOS				3""".split('\n')
lesions = [x.split('\t') for x in lesions[1:]] # ignore header
lesions = [[x[1].strip(),False] for x in lesions]



lymphatic = """	ICD9CM	ICD9DESCR	EMA	Hrvd	NCA	Consensus	FeverReq
LYMPH	289.3	LYMPHADENITIS NOS	1498	0	1044	1	*
LYMPH	683	ADENITIS, GANGRENOUS, ACU	275	0	429	1	*
LYMPH	785.6	LYMPH NODE ENLARGEMENT	2294	0	1208	1	*""".split('\n')
lymphatic = [x.split('\t') for x in lymphatic[1:]] # ignore header
lymphatic = [[x[1].strip(),(x[7].strip()=='*')] for x in lymphatic]



lower_gi = """	ICD9CM	ICD9DESCR	EMA	Hrvd	NCA	Consensus	Lower GI
GI-lower	005.89	FOOD POISONING, OTHER BAC	3	0	0	1	L
GI-lower	005.9	FOOD POISONING      NOS	507	3	49	1	L
GI-lower	008.49	INTEST. INFECT BY OTHER B	2	1	0	1	L
GI-lower	008.5	BACTERIAL ENTERITIS  NOS	3	1	13	1	L
GI-lower	008.69	ENTERITIS VIRAL OTHER	4	28	113	1	L
GI-lower	008.8	ENTERITIS VIRAL NOS	1491	760	2066	1	L
GI-lower	009.0	ENTERITIS/COLITIS/GASTRO.	370	48	1678	1	L
GI-lower	009.1	COLITIS ENTERIT,GASTRO,IN	19	8	125	1	L
GI-lower	009.2	DIARRHEA, INFECTIOUS  NOS	192	15	191	1	L
GI-lower	009.3	DIARRHEA OF INFECT ORIG	0	39	365	1	L
GI-lower	555.0	ENTERITIS SMALL INTESTINE	44	0	178	1	L
GI-lower	555.1	REG ENTERITIS, LG INTEST	0	0	317	1	L
GI-lower	555.2	REG ENTERIT SM/LG INTEST	0	0	312	1	L
GI-lower	558.2	GASTROENTERITIS/COLITIS,	11	2	28	1	L
GI-lower	558.9	GASTROENTERITIS/COLITIS N	61130	1923	8581	1	L
GI-lower	569.9	INTESTINAL DISORDER  NOS	113	10	50	1	L
GI-lower	787.91	DIARRHEA	17448	568	4343	1	L
GI-lower	787.4	PERISTALSIS, VISIBLE	7	0	0	3	L""".split('\n')
lower_gi = [x.split('\t') for x in lower_gi[1:]] # ignore header
lower_gi = [[x[1].strip(),False] for x in lower_gi] # no fevers needed



upper_gi = """	ICD9CM	ICD9DESCR	EMA	Hrvd	NCA	Consensus	Upper GI
GI-upper	078.82	EPIDEMIC VOMITING SYND	0	0	32	1	U
GI-upper	535.00	GASTRITIS, ACUTE	16708	351	1277	1	U
GI-upper	535.01	GASTRITIS, WITH HEMORRHAG	0	7	39	1	U
GI-upper	535.40	GASTRITIS,W/O HEM. OTHER	31	19	108	1	U
GI-upper	535.41	GASTRITIS,OTH SPEC. W/HEM	15	0	4	1	U
GI-upper	535.50	GASTRITIS/GASTRODUOD. W/O	3113	298	902	1	U
GI-upper	535.51	.ASTRITIS/DUODEN W/O HEMO	0	1	38	1	U
GI-upper	535.60	DUODENITIS W/O HEMORRHAGE	27	17	59	1	U
GI-upper	535.61	DUODENITIS W/ HEMORRHAGE	0	0	3	1	U
GI-upper	536.2	VOMITING PERSISTENT	563	15	283	1	U
GI-upper	787.01	NAUSEA WITH VOMITING	14583	723	4050	1	U
GI-upper	787.02	NAUSEA ALONE	31307	48	1017	1	U
GI-upper	787.03	VOMITING ALONE	51291	62	797	1	U""".split('\n')
upper_gi = [x.split('\t') for x in upper_gi[1:]] # ignore header
upper_gi = [[x[1].strip(),False] for x in upper_gi] # no fevers needed



neurological = """	ICD9CM	ICD9DESCR	EMA	Hrvd	NCA	Consensus
NEURO	047.8	MENINGITIS, VIRAL NEC	0	0	3	1
NEURO	047.9	MENINGITIS VIRAL NOS	156	1	27	1
NEURO	048	DIS ENTEROVIRAL OF CNS, NEC	0	0	0	1
NEURO	049.9	ENCEPHALITIS VIRAL NOS	1	2	0	1
NEURO	320.9	BACTERIAL MENINGITIS  NOS	7	1	11	1
NEURO	321.2	Meningitis d/t viral diseases NEC	0	0	0	1
NEURO	322.0	MENINGITIS, NONPYOGENIC	0	0	2	1
NEURO	322.1	MENINGITIS, EOSINOPHILIC	0	0	1	1
NEURO	322.9	MENINGITIS  NOS	435	23	244	1
NEURO	323.8	OTHER CAUSES OF ENCEPHALI	1	2	14	1
NEURO	323.9	ENCEPHALITIS NOS	47	11	92	1
NEURO	348.3	ENCEPHALOPATHY NOS	323	50	485	1
NEURO	781.6	MENINGISMUS	15	0	4	1
NEURO	293.0	DELIRIUM, ACUTE	394	19	189	2
NEURO	293.1	CONFUSIONAL STATE(del subacute)	1361	1	29	2
NEURO	780.02	ALTERATION OF AWARENESS/T	11438	0	146	2
NEURO	780.09	ALTERATION OF AWARENESS	425	0	241	2
NEURO	780.39	CONVULSIONS, OTHER	22583	0	730	2
NEURO	323.6	ENCEPHALITIS POSTINFECTIO	0	1	7	3
NEURO	344.04	QUADRIPLE/QUADRIPA.C5-C7	0	0	3	1
NEURO	344.09	QUADRIPLEGIA/QUADRIPARESI	0	0	99	1
NEURO	344.2	DIPLEGIA OF UPPER LIMBS				1
NEURO	344.89	PARALYTIC SYNDROME, OTHR	21	0	1	1
NEURO	344.9	PARALYSIS	111	0	28	1
NEURO	351.9	FACIAL NERVE DISORDER UNS	97	0	27	1
NEURO	352.6	CRANIAL NERVE PALSIES,MUL	18	0	13	1
NEURO	352.9	CRANIAL NERVE DISORDER, U	29	0	82	1
NEURO	357.0	GUILLAIN-BARRE SYNDROME	69	0	1124	1
NEURO	368.2	DIPLOPIA	379	0	230	1
NEURO	374.30	PTOSIS OF EYELID, UNSPECI	32	0	631	1
NEURO	378.51	NERV PALSY 3RD OR OCULOMO, PARTIAL	76	0	6	1
NEURO	378.52	NERV PALSY 3RD OR OCULOMO, TOTAL				1
NEURO	378.53	NERV PALSY 4TH OR TROCHLEAR				1
NEURO	378.54	SIXTH OR ABDUCENS NERVE P	17	0	32	1
NEURO	378.55	RECTUS PALSY (MEDIAL)	14	0	7	1
NEURO	342.90	HEMIPLEGIA/HEMIPARESIS UN	316	0	147	2
NEURO	344.00	QUADRIPLEGIA, UNSPECIFIED	83	0	36	2
NEURO	344.1	PARAPLEGIA	99	0	120	2
NEURO	351.0	BELL'S PALSY	2405	0	436	2
NEURO	351.8	NEURALGIA FACIAL	114	0	31	2
NEURO	787.2	DYSPHAGIA	2530	0	4384	2
NEURO	350.8	TRIGEMINAL NERVE DISORDER, OTHER SPECIFIED	141	0	9	3
NEURO	350.9	TRIGEMINAL NERVE DISORDER, UNSPECIFIED				3
NEURO	352.0	OLFACTORY (1ST) CN DISORDERS				3
NEURO	352.1	GLOSSOPHARYNGEAL NEURALGI	3	0	2	3
NEURO	352.2	GLOSSOPHARYNGEAL, OTHER DISORDERS				3
NEURO	352.3	DISORD. PNEUMOGASTRIC 10T	1	0	0	3
NEURO	352.4	ACCESSORY (11TH) DISORDERS				3
NEURO	352.5	HYPOGLOSSAL NERVE (12TH) DISORDERS				3
NEURO	374.31	PARALYTIC PTOSIS	0	0	5	3
NEURO	378.50	PARALYTIC STRABISMUS, UNSPEC				3
NEURO	378.56	EXTERNAL OPTHALMOPLEGIA				3""".split('\n')
neurological = [x.split('\t') for x in neurological[1:]] # ignore header
neurological = [[x[1].strip(),False] for x in neurological] # no fevers needed


rash = """	ICD9CM	ICD9DESCR	EMA	Hrvd	NCA	Consensus	FeverReq	x
RASH	050.9	SMALLPOX NOS	0	0	0	1	x
RASH	051.0	COWPOX	0	0	0	1	x
RASH	052.7	VARICELLA COMPLICAT NEC	0	0	11	1	x
RASH	052.8	VARICELLA W/UNSPECIFIED C	0	0	31	1	x
RASH	052.9	VARICELLA NOS	2468	0	306	1	x
RASH	057.8	EXANTHEMATA VIRAL OTHER S	105	30	44	1	*	x
RASH	057.9	EXANTHEM VIRAL, UNSPECIFI	1322	54	561	1	*	x
RASH	695.0	ERYTHEMA TOXIC	23	0	5	1	x
RASH	695.1	ERYTHEMA MULTIFORME	477	0	54	1	x
RASH	695.2	ERYTHEMA NODOSUM	94	0	72	1	x
RASH	695.89	ERYTHEMATOUS CONDITIONS O	112	0	29	1	*	x
RASH	695.9	ERYTHEMATOUS CONDITION  N	738	0	17	1	*	x
RASH	051.2	DERMATITIS PUSTULAR, CONT	6	0	7	3	*	x
RASH	051.9	PARAVACCINIA NOS	0	0	0	3	x
RASH	055.79	MEASLES COMPLICATION NEC	0	0	0	3	x
RASH	055.8	MEASLES COMPLICATION NOS	0	0	0	3	x
RASH	055.9	MEASLES UNCOMPLICATED	14	0	2	3	x
RASH	056.79	RUBELLA COMPLICATION NEC	0	0	0	3	x
RASH	056.8	RUBELLA COMPLICATION  NOS	1	0	0	3	x
RASH	056.9	RUBELLA UNCOMPLICATED	97	0	0	3	x
RASH	083.2	RICKETTSIALPOX	0	0	0	3	x""".split('\n')
rash = [x.split('\t') for x in rash[1:]] # ignore header
rash = [[x[1].strip(),(x[7].strip()=='*')] for x in rash]

respiratory = """	ICD9CM	ICD9DESCR	EMA	Hrvd	NCA	Consensus
RESP	020.3	PRIMARY PNEUMONIC PLAGUE	0	0	0	1
RESP	020.4	SECONDARY PNEUMON PLAGUE	0	0	0	1
RESP	020.5	PNEUMONIC PLAGUE NOS	0	0	0	1
RESP	021.2	PULMONARY TULAREMIA	0	0	0	1
RESP	022.1	PULMONARY ANTHRAX	0	0	0	1
RESP	464.10	TRACHEITIS W/O OBSTRUCTIO	87	7	36	1
RESP	464.11	AC TRACHEITIS W OBSTRUCT	0	0	0	1
RESP	464.20	LARYNGOTRACHEITIS W/O OBS	115	6	46	1
RESP	464.21	AC LARYNGOTRACH W OBSTR	0	0	0	1
RESP	464.30	EPIGLOTTITIS ACUTE W/O OB	141	1	4	1
RESP	464.31	AC EPIGLOTTITIS W OBSTR	0	0	0	1
RESP	464.4	CROUP	4569	178	902	1
RESP	464.50	SUPRAGLOTTIS,UNS.W/O OBST	2	0	0	1
RESP	464.51	SUPRAGLOTTIS,UNS.W/ OBST				1
RESP	465.0	LARYNGOPHARYNGITIS, ACUTE	40	5	101	1
RESP	466.0	BRONCHITIS ACUTE	21520	3797	15428	1
RESP	466.11	BRONCHIOLITIS ACUTE DUE T	1086	205	550	1
RESP	466.19	BRONCHIOLITIS DUE TO OT/I	2382	246	928	1
RESP	478.9	RESPIRATORY TRACT DISEASE	51	0	234	1
RESP	480.8	VIRAL PNEUMONIA NEC	0	3	82	1
RESP	480.9	PNEUMONIA, VIRAL	92	58	260	1
RESP	482.9	PNEUMONIA, BACTERIAL  NOS	1628	211	423	1
RESP	483.8	Pneumonia d/t organism NEC	0	1	42	1
RESP	484.5	PNEUMONIA IN ANTHRAX	0	0	0	1
RESP	484.8	PNEUM IN INFECT DIS NEC	0	22	212	1
RESP	485	BRONCHOPNEUMONIA ORGANISM	1420	5	57	1
RESP	486	PNEUMONIA, ORGANISM NOS	46977	1432	6142	1
RESP	490	BRONCHITIS NOS	36799	0	1927	1
RESP	511.0	PLEURISY W/O EFFUSION	1652	0	145	1
RESP	511.1	PLEURAL EFFUSION-VIRAL(NO	0	0	11	1
RESP	511.8	HEMOTHORAX	44	0	17	1
RESP	513.0	ABSCESS LUNG	39	0	38	1
RESP	513.1	ABSCESS OF MEDIASTINUM	0	0	3	1
RESP	518.4	EDEMA LUNG ACUTE  NOS	43	0	12	1
RESP	518.84	RESPIRATORY FAILURE,ACUTE	15	0	0	1
RESP	519.2	MEDIASTINITIS	5	0	5	1
RESP	519.3	MEDIASTINUM, DISEASES NEC	7	0	25	1
RESP	769	RESPIRATORY DISTRESS SYND	23	0	24	1
RESP	786.3	HEMOPTYSIS	2277	68	313	1
RESP	786.52	PAINFUL RESPIRAT./PLEUROD	14661	0	984	1
RESP	511.9	PLEURAL EFFUSION UNSPECIF	4948	0	558	2
RESP	518.81	RESPIRATORY FAILURE, ACUT	4735	3	21	2
RESP	003.22	SALMONELLA PNEUMONIA	0	0	1	3
RESP	031.0	MYCOBACTERIA, PULMONARY	2	31	114	3
RESP	031.8	MYCOBACTERIAL DIS NEC	0	0	1	3
RESP	031.9	MYCOBACTERIA DISEASES/UNS	1	9	77	3
RESP	032.0	FAUCIAL DIPHTHERIA	0	0	0	3
RESP	032.1	NASOPHARYNX DIPHTHERIA	0	0	0	3
RESP	032.2	ANT NASAL DIPHTHERIA	0	0	0	3
RESP	032.3	LARYNGEAL DIPHTHERIA	0	0	0	3
RESP	032.89	DIPHTHERIA NEC	0	0	0	3
RESP	032.9	DIPHTHERIA NOS	0	0	0	3
RESP	033.0	BORDETELLA PERTUSSIS	0	0	12	3
RESP	033.1	BORDETELLA PARAPERTUSSIS	0	0	0	3
RESP	033.8	WHOOPING COUGH NEC	0	0	0	3
RESP	033.9	WHOOPING COUGH(UNSPE.ORGA	5	1	2	3
RESP	052.1	VARICELLA WITH PNEUMONIA	5	0	4	3
RESP	055.2	POSTMEASLES OTITIS MEDIA	0	0	0	3
RESP	073.0	ORNITHOSIS, WITH PNEUMONIA				3
RESP	073.7	ORNITHOSIS, OTHER SPECIF COMPLIC				3
RESP	073.8	ORNITHOSIS, UNSPECIFIED COMPLIC				3
RESP	073.9	ORNITHOSIS, UNSPECIFIED				3
RESP	079.0	ADENOVIRUS INFECT NOS	0	1	13	3
RESP	079.1	ECHO VIRUS INFECT NOS	0	1	0	3
RESP	079.2	COXSACKIE VIRUS	399	3	66	3
RESP	079.6	RESPIRATORY SYNCYTIAL VIR	275	7	25	3
RESP	079.81	HANTAVIRUS INFECTION	2	0	0	3
RESP	114.5	PULM COCCIDIOIDOMYCOS,UN	0	0	2	3
RESP	114.9	COCCIDIOIDOMYCOSIS NOS	0	1	5	3
RESP	115.00	HISTOPLASMOSIS, WITHOUT MENTION OF MANIFESTATION	0	0	0	3
RESP	115.05	HISTOPLASM CAPS PNEUMON	0	0	5	3
RESP	115.09	HISTOPLASMA CAPSULAT NEC	0	0	3	3
RESP	115.10	HISTOPLASMA DUBOISII NOS	0	0	1	3
RESP	115.15	HISTOPLASMA DUBOISII PNEUMONIA	0	0	1	3
RESP	115.90	HISTOPLASMOSIS,W/O MANIFE	2	3	9	3
RESP	115.95	HISTOPLASMOSIS PNEUMONIA	0	0	0	3
RESP	115.99	HISTOPLASMOSIS NEC	0	0	2	3
RESP	116.0	BLASTOMYCOSIS	0	0	0	3
RESP	116.1	PARACOCCIDIOIDOMYCOSIS	0	0	0	3
RESP	117.1	SPOROTRICHOSIS	0	0	5	3
RESP	117.3	PULMONARY ASPERGILLOSIS	7	1	5	3
RESP	117.5	CRYPTOCOCCOSIS	15	0	2	3
RESP	130.4	TOXOPLASMA PNEUMONITIS	0	1	0	3
RESP	136.3	PNEUMOCYSTOSIS	35	0	39	3
RESP	480.0	ADENOVIRAL PNEUMONIA	0	0	0	3
RESP	480.1	PNEUMONIA,RESP.SYNCYTIAL	62	0	38	3
RESP	480.2	PARINFLUENZA VIRAL PNEUM	0	1	18	3
RESP	481	PNEUMOCOCCAL PNEUMONIA (L	132	14	107	3
RESP	482.0	PNEUMONIA-KLEBSIELLA PNEU	16	5	24	3
RESP	482.1	PNEUMONIA DUE TO PSEUDOMO	0	0	9	3
RESP	482.2	H.INFLUENZAE PNEUMONIA	0	2	20	3
RESP	482.30	STREPTOCOCCUS UNSPECIFIED	0	2	52	3
RESP	482.31	PNEUMONIA/STREPTOC GPA	0	0	3	3
RESP	482.32	PHEUMONIA/STREPTO GPB	0	0	2	3
RESP	482.39	PNEUMONIA/OTHER STREPTOC	0	0	6	3
RESP	482.40	STAPH PNEUMONIA NOS	0	0	2	3
RESP	482.41	PNEUMONIA, STAPHYLOCOC. A	0	0	0	3
RESP	482.49	OTH STAPH PNEUMONIA	0	0	1	3
RESP	482.81	PNEUMONIA/ANAEROBES	0	0	12	3
RESP	482.82	PNEUMONIA/E COLI	0	0	0	3
RESP	482.83	PNEUMONIA/OTHER GNEG BAC	0	0	3	3
RESP	482.84	LEGIONNAIRES' DISEASE	0	0	1	3
RESP	482.89	PNEUMONIA/OTHER SPEC BAC	0	16	489	3
RESP	483.0	PNEUMONIA MYCOPLASMA	37	11	77	3
RESP	483.1	PNEUMONIA DUE TO CHLAMYD	0	0	0	3
RESP	484.1	PNEUM W CYTOMEG INCL DIS	0	1	4	3
RESP	484.3	PNEUMONIA IN WHOOP COUGH	0	0	2	3
RESP	484.6	PNEUMONIA IN ASPERGILLOSI	0	0	2	3
RESP	484.7	PNEUM IN OTH SYS MYCOSES	0	0	0	3""".split('\n')
respiratory = [x.split('\t') for x in respiratory[1:]] # ignore header
respiratory = [[x[1].strip(),False] for x in respiratory] # no fevers needed




btzip="""BT Region	Region Name	Zip Code 5	Locality Name	Locality Type	City Name
1	West	01220	Adams	Official	Adams
1	West	01001	Agawam	Official	Agawam
1	West	01002	Amherst	Official	Amherst
1	West	01003	Amherst	Official	Amherst
1	West	01004	Amherst	Official	Amherst
1	West	01330	Ashfield	Official	Ashfield
1	West	01222	Ashley Falls	Unofficial	Sheffield
1	West	01223	Becket	Official	Becket
1	West	01007	Belchertown	Official	Belchertown
1	West	01224	Berkshire	Unofficial	Lanesborough
1	West	01337	Bernardston	Official	Bernardston
1	West	01008	Blandford	Official	Blandford
1	West	01009	Bondsville	Unofficial	Palmer
1	West	01338	Buckland	Official	Buckland
1	West	01339	Charlemont	Official	Charlemont
1	West	01225	Cheshire	Official	Cheshire
1	West	01011	Chester	Official	Chester
1	West	01012	Chesterfield	Official	Chesterfield
1	West	01020	Chicopee	Official	Chicopee
1	West	01022	Chicopee	Official	Chicopee
1	West	01021	Chicopee	Official	Chicopee
1	West	01014	Chicopee	Official	Chicopee
1	West	01013	Chicopee	Official	Chicopee
1	West	01340	Colrain	Official	Colrain
1	West	01341	Conway	Official	Conway
1	West	01026	Cummington	Official	Cummington
1	West	01226	Dalton	Official	Dalton
1	West	01227	Dalton	Official	Dalton
1	West	01342	Deerfield	Official	Deerfield
1	West	01343	Drury	Unofficial	Florida
1	West	01028	East Longmeadow	Official	East Longmeadow
1	West	01029	East Otis	Unofficial	Otis
1	West	01027	Easthampton	Official	Easthampton
1	West	01344	Erving	Official	Erving
1	West	01030	Feeding Hills	Unofficial	Agawam
1	West	01062	Florence	Unofficial	Northampton
1	West	01229	Glendale	Unofficial	Stockbridge
1	West	01032	Goshen	Official	Goshen
1	West	01033	Granby	Official	Granby
1	West	01034	Granville	Official	Granville
1	West	01230	Great Barrington	Official	Great Barrington
1	West	01302	Greenfield	Official	Greenfield
1	West	01301	Greenfield	Official	Greenfield
1	West	01035	Hadley	Official	Hadley
1	West	01036	Hampden	Official	Hampden
1	West	01038	Hatfield	Official	Hatfield
1	West	01039	Haydenville	Unofficial	Williamsburg
1	West	01346	Heath	Official	Heath
1	West	01235	Hinsdale	Official	Hinsdale
1	West	01040	Holyoke	Official	Holyoke
1	West	01041	Holyoke	Official	Holyoke
1	West	01236	Housatonic	Unofficial	Great Barrington
1	West	01050	Huntington	Official	Huntington
1	West	01151	Indian Orchard	Unofficial	Springfield
1	West	01347	Lake Pleasant	Unofficial	Montague
1	West	01237	Lanesborough	Official	Lanesborough
1	West	01238	Lee	Official	Lee
1	West	01053	Leeds	Unofficial	Northampton
1	West	01240	Lenox	Official	Lenox
1	West	01242	Lenox Dale	Unofficial	Lenox
1	West	01054	Leverett	Official	Leverett
1	West	01116	Longmeadow	Official	Longmeadow
1	West	01106	Longmeadow	Official	Longmeadow
1	West	01056	Ludlow	Official	Ludlow
1	West	01243	Middlefield	Official	Middlefield
1	West	01244	Mill River	Unofficial	New Marlborough
1	West	01350	Monroe Bridge	Unofficial	Monroe
1	West	01057	Monson	Official	Monson
1	West	01351	Montague	Official	Montague
1	West	01245	Monterey	Official	Monterey
1	West	01247	North Adams	Official	North Adams
1	West	01059	North Amherst	Unofficial	Amherst
1	West	01252	North Egremont	Unofficial	Egremont
1	West	01066	North Hatfield	Unofficial	Hatfield
1	West	01061	Northampton	Official	Northampton
1	West	01063	Northampton	Official	Northampton
1	West	01060	Northampton	Official	Northampton
1	West	01354	Northfield	Official	Northfield
1	West	01360	Northfield	Official	Northfield
1	West	01253	Otis	Official	Otis
1	West	01069	Palmer	Official	Palmer
1	West	01201	Pittsfield	Official	Pittsfield
1	West	01203	Pittsfield	Official	Pittsfield
1	West	01202	Pittsfield	Official	Pittsfield
1	West	01070	Plainfield	Official	Plainfield
1	West	01254	Richmond	Official	Richmond
1	West	01367	Rowe	Official	Rowe
1	West	01071	Russell	Official	Russell
1	West	01255	Sandisfield	Official	Sandisfield
1	West	01256	Savoy	Official	Savoy
1	West	01369	Shattuckville	Unofficial	Colrain
1	West	01257	Sheffield	Official	Sheffield
1	West	01370	Shelburne Falls	Unofficial	Shelburne
1	West	01072	Shutesbury	Official	Shutesbury
1	West	01373	South Deerfield	Unofficial	Deerfield
1	West	01258	South Egremont	Unofficial	Egremont
1	West	01075	South Hadley	Official	South Hadley
1	West	01260	South Lee	Unofficial	Lee
1	West	01073	Southampton	Official	Southampton
1	West	01077	Southwick	Official	Southwick
1	West	01133	Springfield	Official	Springfield
1	West	01118	Springfield	Official	Springfield
1	West	01119	Springfield	Official	Springfield
1	West	01115	Springfield	Official	Springfield
1	West	01129	Springfield	Official	Springfield
1	West	01108	Springfield	Official	Springfield
1	West	01138	Springfield	Official	Springfield
1	West	01144	Springfield	Official	Springfield
1	West	01199	Springfield	Official	Springfield
1	West	01114	Springfield	Official	Springfield
1	West	01128	Springfield	Official	Springfield
1	West	01109	Springfield	Official	Springfield
1	West	01107	Springfield	Official	Springfield
1	West	01105	Springfield	Official	Springfield
1	West	01104	Springfield	Official	Springfield
1	West	01103	Springfield	Official	Springfield
1	West	01102	Springfield	Official	Springfield
1	West	01152	Springfield	Official	Springfield
1	West	01139	Springfield	Official	Springfield
1	West	01101	Springfield	Official	Springfield
1	West	01111	Springfield	Official	Springfield
1	West	01263	Stockbridge	Official	Stockbridge
1	West	01262	Stockbridge	Official	Stockbridge
1	West	01375	Sunderland	Official	Sunderland
1	West	01079	Thorndike	Unofficial	Palmer
1	West	01080	Three Rivers	Unofficial	Palmer
1	West	01376	Turners Falls	Unofficial	Montague
1	West	01349	Turners Falls	Unofficial	Montague
1	West	01264	Tyringham	Official	Tyringham
1	West	01082	Ware	Official	Ware
1	West	01378	Warwick	Official	Warwick
1	West	01379	Wendell	Official	Wendell
1	West	01380	Wendell Depot	Unofficial	Wendell
1	West	01084	West Chesterfield	Unofficial	Chesterfield
1	West	01088	West Hatfield	Unofficial	Hatfield
1	West	01089	West Springfield	Official	West Springfield
1	West	01090	West Springfield	Official	West Springfield
1	West	01266	West Stockbridge	Official	West Stockbridge
1	West	01086	Westfield	Official	Westfield
1	West	01085	Westfield	Official	Westfield
1	West	01093	Whately	Official	Whately
1	West	01095	Wilbraham	Official	Wilbraham
1	West	01096	Williamsburg	Official	Williamsburg
1	West	01267	Williamstown	Official	Williamstown
1	West	01270	Windsor	Official	Windsor
1	West	01097	Woronoco	Unofficial	Russell
1	West	01098	Worthington	Official	Worthington
1	West	01027	Westhampton	Official	Westhampton
1	West	01034	Tolland	Official	Tolland
1	West	01230	Alford	Official	Alford
1	West	01247	Clarksburg	Official	Clarksburg
1	West	01354	Gill	Official	Gill
1	West	01235	Peru	Official	Peru
1	West	01002	Pelham	Official	Pelham
1	West	01237	Hancock	Official	Hancock
1	West	01339	Hawley	Official	Hawley
1	West	01237	New Ashford	Official	New Ashford
1	West	01258	Mount Washington	Official	Mount Washington
1	West	01085	Montgomery	Official	Montgomery
1	West	01301	Leyden	Official	Leyden
1	West	01233	Washington	Official	Washington
1	West	01230	Egremont	Official	Egremont
1	West	01247	Florida	Official	Florida
1	West	01350	Monroe	Official	Monroe
1	West	01230	New Marlborough	Official	New Marlborough
1	West	01370	Shelburne	Official	Shelburne
2	Central	01430	Ashburnham	Official	Ashburnham
2	Central	01431	Ashby	Official	Ashby
2	Central	01331	Athol	Official	Athol
2	Central	01501	Auburn	Official	Auburn
2	Central	01432	Ayer	Official	Ayer
2	Central	01436	Baldwinsville	Unofficial	Templeton
2	Central	01005	Barre	Official	Barre
2	Central	02019	Bellingham	Official	Bellingham
2	Central	01503	Berlin	Official	Berlin
2	Central	01504	Blackstone	Official	Blackstone
2	Central	01740	Bolton	Official	Bolton
2	Central	01505	Boylston	Official	Boylston
2	Central	01010	Brimfield	Official	Brimfield
2	Central	01506	Brookfield	Official	Brookfield
2	Central	01507	Charlton	Official	Charlton
2	Central	01508	Charlton City	Unofficial	Charlton
2	Central	01509	Charlton Depot	Unofficial	Charlton
2	Central	01611	Cherry Valley	Unofficial	Leicester
2	Central	01510	Clinton	Official	Clinton
2	Central	01516	Douglas	Official	Douglas
2	Central	01571	Dudley	Official	Dudley
2	Central	01827	Dunstable	Official	Dunstable
2	Central	01515	East Brookfield	Official	East Brookfield
2	Central	01517	East Princeton	Unofficial	Princeton
2	Central	01438	East Templeton	Unofficial	Templeton
2	Central	01518	Fiskedale	Unofficial	Sturbridge
2	Central	01420	Fitchburg	Official	Fitchburg
2	Central	02038	Franklin	Official	Franklin
2	Central	01440	Gardner	Official	Gardner
2	Central	01031	Gilbertville	Unofficial	Hardwick
2	Central	01519	Grafton	Official	Grafton
2	Central	01471	Groton	Official	Groton
2	Central	01450	Groton	Official	Groton
2	Central	01470	Groton	Official	Groton
2	Central	01037	Hardwick	Official	Hardwick
2	Central	01451	Harvard	Official	Harvard
2	Central	01520	Holden	Official	Holden
2	Central	01521	Holland	Official	Holland
2	Central	01747	Hopedale	Official	Hopedale
2	Central	01452	Hubbardston	Official	Hubbardston
2	Central	01522	Jefferson	Unofficial	Holden
2	Central	01523	Lancaster	Official	Lancaster
2	Central	01524	Leicester	Official	Leicester
2	Central	01453	Leominster	Official	Leominster
2	Central	01525	Linwood	Unofficial	Uxbridge
2	Central	01462	Lunenburg	Official	Lunenburg
2	Central	01526	Manchaug	Unofficial	Sutton
2	Central	02053	Medway	Official	Medway
2	Central	01756	Mendon	Official	Mendon
2	Central	01757	Milford	Official	Milford
2	Central	01527	Millbury	Official	Millbury
2	Central	01529	Millville	Official	Millville
2	Central	01531	New Braintree	Official	New Braintree
2	Central	01355	New Salem	Official	New Salem
2	Central	01535	North Brookfield	Official	North Brookfield
2	Central	01536	North Grafton	Unofficial	Grafton
2	Central	01537	North Oxford	Unofficial	Oxford
2	Central	01538	North Uxbridge	Unofficial	Uxbridge
2	Central	01532	Northborough	Official	Northborough
2	Central	01534	Northbridge	Official	Northbridge
2	Central	01068	Oakham	Official	Oakham
2	Central	01364	Orange	Official	Orange
2	Central	01540	Oxford	Official	Oxford
2	Central	01612	Paxton	Official	Paxton
2	Central	01463	Pepperell	Official	Pepperell
2	Central	01366	Petersham	Official	Petersham
2	Central	01541	Princeton	Official	Princeton
2	Central	01542	Rochdale	Unofficial	Leicester
2	Central	01368	Royalston	Official	Royalston
2	Central	01543	Rutland	Official	Rutland
2	Central	01464	Shirley	Official	Shirley
2	Central	01546	Shrewsbury	Official	Shrewsbury
2	Central	01545	Shrewsbury	Official	Shrewsbury
2	Central	01074	South Barre	Unofficial	Barre
2	Central	01560	South Grafton	Unofficial	Grafton
2	Central	01561	South Lancaster	Unofficial	Lancaster
2	Central	01550	Southbridge	Official	Southbridge
2	Central	01562	Spencer	Official	Spencer
2	Central	01564	Sterling	Official	Sterling
2	Central	01467	Still River	Unofficial	Harvard
2	Central	01566	Sturbridge	Official	Sturbridge
2	Central	01590	Sutton	Official	Sutton
2	Central	01468	Templeton	Official	Templeton
2	Central	01469	Townsend	Official	Townsend
2	Central	01568	Upton	Official	Upton
2	Central	01569	Uxbridge	Official	Uxbridge
2	Central	01081	Wales	Official	Wales
2	Central	01083	Warren	Official	Warren
2	Central	01570	Webster	Official	Webster
2	Central	01583	West Boylston	Official	West Boylston
2	Central	01585	West Brookfield	Official	West Brookfield
2	Central	01472	West Groton	Unofficial	Groton
2	Central	01586	West Millbury	Unofficial	Millbury
2	Central	01474	West Townsend	Unofficial	Townsend
2	Central	01092	West Warren	Unofficial	Warren
2	Central	01473	Westminster	Official	Westminster
2	Central	01441	Westminster	Official	Westminster
2	Central	01094	Wheelwright	Unofficial	Hardwick
2	Central	01588	Whitinsville	Unofficial	Northbridge
2	Central	01475	Winchendon	Official	Winchendon
2	Central	01477	Winchendon Springs	Unofficial	Winchendon
2	Central	01601	Worcester	Official	Worcester
2	Central	01602	Worcester	Official	Worcester
2	Central	01603	Worcester	Official	Worcester
2	Central	01604	Worcester	Official	Worcester
2	Central	01605	Worcester	Official	Worcester
2	Central	01606	Worcester	Official	Worcester
2	Central	01607	Worcester	Official	Worcester
2	Central	01608	Worcester	Official	Worcester
2	Central	01609	Worcester	Official	Worcester
2	Central	01615	Worcester	Official	Worcester
2	Central	01613	Worcester	Official	Worcester
2	Central	01614	Worcester	Official	Worcester
2	Central	01653	Worcester	Official	Worcester
2	Central	01654	Worcester	Official	Worcester
2	Central	01655	Worcester	Official	Worcester
2	Central	01610	Worcester	Official	Worcester
2	Central	01331	Phillipston	Official	Phillipston
3	Northeast	01913	Amesbury	Official	Amesbury
3	Northeast	01812	Andover	Official	Andover
3	Northeast	01810	Andover	Official	Andover
3	Northeast	05501	Andover	Official	Andover
3	Northeast	05544	Andover	Official	Andover
3	Northeast	01899	Andover	Official	Andover
3	Northeast	01915	Beverly	Official	Beverly
3	Northeast	01821	Billerica	Official	Billerica
3	Northeast	01822	Billerica	Official	Billerica
3	Northeast	01921	Boxford	Official	Boxford
3	Northeast	01922	Byfield	Unofficial	Newbury
3	Northeast	01824	Chelmsford	Official	Chelmsford
3	Northeast	01923	Danvers	Official	Danvers
3	Northeast	01826	Dracut	Official	Dracut
3	Northeast	01929	Essex	Official	Essex
3	Northeast	01833	Georgetown	Official	Georgetown
3	Northeast	01931	Gloucester	Official	Gloucester
3	Northeast	01930	Gloucester	Official	Gloucester
3	Northeast	01834	Groveland	Official	Groveland
3	Northeast	01936	Hamilton	Official	Hamilton
3	Northeast	01937	Hathorne	Unofficial	Danvers
3	Northeast	01831	Haverhill	Official	Haverhill
3	Northeast	01835	Haverhill	Official	Haverhill
3	Northeast	01830	Haverhill	Official	Haverhill
3	Northeast	01832	Haverhill	Official	Haverhill
3	Northeast	01938	Ipswich	Official	Ipswich
3	Northeast	01842	Lawrence	Official	Lawrence
3	Northeast	01841	Lawrence	Official	Lawrence
3	Northeast	01840	Lawrence	Official	Lawrence
3	Northeast	01843	Lawrence	Official	Lawrence
3	Northeast	01853	Lowell	Official	Lowell
3	Northeast	01851	Lowell	Official	Lowell
3	Northeast	01852	Lowell	Official	Lowell
3	Northeast	01850	Lowell	Official	Lowell
3	Northeast	01854	Lowell	Official	Lowell
3	Northeast	01901	Lynn	Official	Lynn
3	Northeast	01910	Lynn	Official	Lynn
3	Northeast	01902	Lynn	Official	Lynn
3	Northeast	01904	Lynn	Official	Lynn
3	Northeast	01903	Lynn	Official	Lynn
3	Northeast	01905	Lynn	Official	Lynn
3	Northeast	01940	Lynnfield	Official	Lynnfield
3	Northeast	02148	Malden	Official	Malden
3	Northeast	01944	Manchester	Official	Manchester
3	Northeast	01945	Marblehead	Official	Marblehead
3	Northeast	02155	Medford	Official	Medford
3	Northeast	02153	Medford	Official	Medford
3	Northeast	02176	Melrose	Official	Melrose
3	Northeast	02177	Melrose	Official	Melrose
3	Northeast	01860	Merrimac	Official	Merrimac
3	Northeast	01844	Methuen	Official	Methuen
3	Northeast	01949	Middleton	Official	Middleton
3	Northeast	01908	Nahant	Official	Nahant
3	Northeast	01951	Newbury	Official	Newbury
3	Northeast	01950	Newburyport	Official	Newburyport
3	Northeast	01845	North Andover	Official	North Andover
3	Northeast	01862	North Billerica	Unofficial	Billerica
3	Northeast	01863	North Chelmsford	Unofficial	Chelmsford
3	Northeast	01864	North Reading	Official	North Reading
3	Northeast	01889	North Reading	Official	North Reading
3	Northeast	01865	Nutting Lake	Unofficial	Billerica
3	Northeast	01960	Peabody	Official	Peabody
3	Northeast	01961	Peabody	Official	Peabody
3	Northeast	01866	Pinehurst	Unofficial	Billerica
3	Northeast	01965	Prides Crossing	Unofficial	Beverly
3	Northeast	01867	Reading	Official	Reading
3	Northeast	01966	Rockport	Official	Rockport
3	Northeast	01969	Rowley	Official	Rowley
3	Northeast	01947	Salem	Official	Salem
3	Northeast	01970	Salem	Official	Salem
3	Northeast	01971	Salem	Official	Salem
3	Northeast	01952	Salisbury	Official	Salisbury
3	Northeast	01906	Saugus	Official	Saugus
3	Northeast	01982	South Hamilton	Unofficial	Hamilton
3	Northeast	02180	Stoneham	Official	Stoneham
3	Northeast	01907	Swampscott	Official	Swampscott
3	Northeast	01876	Tewksbury	Official	Tewksbury
3	Northeast	01983	Topsfield	Official	Topsfield
3	Northeast	01879	Tyngsborough	Official	Tyngsborough
3	Northeast	01880	Wakefield	Official	Wakefield
3	Northeast	01984	Wenham	Official	Wenham
3	Northeast	01885	West Boxford	Unofficial	Boxford
3	Northeast	02156	West Medford	Unofficial	Medford
3	Northeast	01985	West Newbury	Official	West Newbury
3	Northeast	01886	Westford	Official	Westford
4a	Outer Metro Boston	01720	Acton	Official	Acton
4a	Outer Metro Boston	01721	Ashland	Official	Ashland
4a	Outer Metro Boston	01730	Bedford	Official	Bedford
4a	Outer Metro Boston	01719	Boxborough	Official	Boxborough
4a	Outer Metro Boston	01805	Burlington	Official	Burlington
4a	Outer Metro Boston	01803	Burlington	Official	Burlington
4a	Outer Metro Boston	01741	Carlisle	Official	Carlisle
4a	Outer Metro Boston	01742	Concord	Official	Concord
4a	Outer Metro Boston	02030	Dover	Official	Dover
4a	Outer Metro Boston	02032	East Walpole	Unofficial	Walpole
4a	Outer Metro Boston	01745	Fayville	Unofficial	Southborough
4a	Outer Metro Boston	01704	Framingham	Official	Framingham
4a	Outer Metro Boston	01705	Framingham	Official	Framingham
4a	Outer Metro Boston	01703	Framingham	Official	Framingham
4a	Outer Metro Boston	01702	Framingham	Official	Framingham
4a	Outer Metro Boston	01701	Framingham	Official	Framingham
4a	Outer Metro Boston	01731	Hanscom Afb	Unofficial	Bedford
4a	Outer Metro Boston	02646	Harwich Port	Unofficial	Harwich
4a	Outer Metro Boston	01746	Holliston	Official	Holliston
4a	Outer Metro Boston	01748	Hopkinton	Official	Hopkinton
4a	Outer Metro Boston	01749	Hudson	Official	Hudson
4a	Outer Metro Boston	02420	Lexington	Official	Lexington
4a	Outer Metro Boston	02421	Lexington	Official	Lexington
4a	Outer Metro Boston	01773	Lincoln	Official	Lincoln
4a	Outer Metro Boston	01460	Littleton	Official	Littleton
4a	Outer Metro Boston	01752	Marlborough	Official	Marlborough
4a	Outer Metro Boston	01754	Maynard	Official	Maynard
4a	Outer Metro Boston	02052	Medfield	Official	Medfield
4a	Outer Metro Boston	02054	Millis	Official	Millis
4a	Outer Metro Boston	01760	Natick	Official	Natick
4a	Outer Metro Boston	02056	Norfolk	Official	Norfolk
4a	Outer Metro Boston	02455	North Waltham	Unofficial	Waltham
4a	Outer Metro Boston	02067	Sharon	Official	Sharon
4a	Outer Metro Boston	02070	Sheldonville	Unofficial	Wrentham
4a	Outer Metro Boston	01770	Sherborn	Official	Sherborn
4a	Outer Metro Boston	02071	South Walpole	Unofficial	Walpole
4a	Outer Metro Boston	01772	Southborough	Official	Southborough
4a	Outer Metro Boston	01259	Southfield	Unofficial	Marlborough
4a	Outer Metro Boston	01775	Stow	Official	Stow
4a	Outer Metro Boston	01776	Sudbury	Official	Sudbury
4a	Outer Metro Boston	01718	Village Of Nagog Woods	Unofficial	Acton
4a	Outer Metro Boston	02081	Walpole	Official	Walpole
4a	Outer Metro Boston	02451	Waltham	Official	Waltham
4a	Outer Metro Boston	02453	Waltham	Official	Waltham
4a	Outer Metro Boston	02452	Waltham	Official	Waltham
4a	Outer Metro Boston	02454	Waltham	Official	Waltham
4a	Outer Metro Boston	01778	Wayland	Official	Wayland
4a	Outer Metro Boston	01580	Westborough	Official	Westborough
4a	Outer Metro Boston	01581	Westborough	Official	Westborough
4a	Outer Metro Boston	01582	Westborough	Official	Westborough
4a	Outer Metro Boston	02493	Weston	Official	Weston
4a	Outer Metro Boston	01887	Wilmington	Official	Wilmington
4a	Outer Metro Boston	01890	Winchester	Official	Winchester
4a	Outer Metro Boston	01807	Woburn	Official	Woburn
4a	Outer Metro Boston	01801	Woburn	Official	Woburn
4a	Outer Metro Boston	01806	Woburn	Official	Woburn
4a	Outer Metro Boston	01808	Woburn	Official	Woburn
4a	Outer Metro Boston	01813	Woburn	Official	Woburn
4a	Outer Metro Boston	01815	Woburn	Official	Woburn
4a	Outer Metro Boston	01888	Woburn	Official	Woburn
4a	Outer Metro Boston	01784	Woodville	Unofficial	Hopkinton
4a	Outer Metro Boston	02093	Wrentham	Official	Wrentham
4b	Inner Metro Boston	02018	Accord	Unofficial	Norwell
4b	Inner Metro Boston	02474	Arlington	Official	Arlington
4b	Inner Metro Boston	02476	Arlington	Official	Arlington
4b	Inner Metro Boston	02475	Arlington Heights	Unofficial	Arlington
4b	Inner Metro Boston	02466	Auburndale	Unofficial	Newton
4b	Inner Metro Boston	02457	Babson Park	Unofficial	Wellesley
4b	Inner Metro Boston	02478	Belmont	Official	Belmont
4b	Inner Metro Boston	02184	Braintree	Official	Braintree
4b	Inner Metro Boston	02185	Braintree	Official	Braintree
4b	Inner Metro Boston	02446	Brookline	Official	Brookline
4b	Inner Metro Boston	02445	Brookline	Official	Brookline
4b	Inner Metro Boston	02447	Brookline Village	Unofficial	Brookline
4b	Inner Metro Boston	02239	Cambridge	Official	Cambridge
4b	Inner Metro Boston	02138	Cambridge	Official	Cambridge
4b	Inner Metro Boston	02139	Cambridge	Official	Cambridge
4b	Inner Metro Boston	02140	Cambridge	Official	Cambridge
4b	Inner Metro Boston	02238	Cambridge	Official	Cambridge
4b	Inner Metro Boston	02141	Cambridge	Official	Cambridge
4b	Inner Metro Boston	02142	Cambridge	Official	Cambridge
4b	Inner Metro Boston	02021	Canton	Official	Canton
4b	Inner Metro Boston	02150	Chelsea	Official	Chelsea
4b	Inner Metro Boston	02467	Chestnut Hill	Unofficial	Newton
4b	Inner Metro Boston	02025	Cohasset	Official	Cohasset
4b	Inner Metro Boston	02026	Dedham	Official	Dedham
4b	Inner Metro Boston	02027	Dedham	Official	Dedham
4b	Inner Metro Boston	02149	Everett	Official	Everett
4b	Inner Metro Boston	02040	Green Bush	Unofficial	Scituate
4b	Inner Metro Boston	02339	Hanover	Official	Hanover
4b	Inner Metro Boston	02340	Hanover	Official	Hanover
4b	Inner Metro Boston	02043	Hingham	Official	Hingham
4b	Inner Metro Boston	02044	Hingham	Official	Hingham
4b	Inner Metro Boston	02045	Hull	Official	Hull
4b	Inner Metro Boston	02047	Hummarock	Unofficial	Scituate
4b	Inner Metro Boston	02186	Milton	Official	Milton
4b	Inner Metro Boston	02187	Milton Village	Unofficial	Milton
4b	Inner Metro Boston	02492	Needham	Official	Needham
4b	Inner Metro Boston	02494	Needham Heights	Unofficial	Needham
4b	Inner Metro Boston	02456	Newtowne	Unofficial	Cambridge
4b	Inner Metro Boston	02458	Newton	Official	Newton
4b	Inner Metro Boston	02459	Newton Center	Unofficial	Newton
4b	Inner Metro Boston	02461	Newton Highlands	Unofficial	Newton
4b	Inner Metro Boston	02462	Newton Lower Falls	Unofficial	Newton
4b	Inner Metro Boston	02464	Newton Upper Falls	Unofficial	Newton
4b	Inner Metro Boston	02460	Newtonville	Unofficial	Newton
4b	Inner Metro Boston	02495	Nonantum	Unofficial	Newton
4b	Inner Metro Boston	02060	North Scituate	Unofficial	Scituate
4b	Inner Metro Boston	02061	Norwell	Official	Norwell
4b	Inner Metro Boston	02062	Norwood	Official	Norwood
4b	Inner Metro Boston	02269	Quincy	Official	Quincy
4b	Inner Metro Boston	02169	Quincy	Official	Quincy
4b	Inner Metro Boston	02170	Quincy	Official	Quincy
4b	Inner Metro Boston	02171	Quincy	Official	Quincy
4b	Inner Metro Boston	02151	Revere	Official	Revere
4b	Inner Metro Boston	02066	Scituate	Official	Scituate
4b	Inner Metro Boston	02143	Somerville	Official	Somerville
4b	Inner Metro Boston	02145	Somerville	Official	Somerville
4b	Inner Metro Boston	02144	Somerville	Official	Somerville
4b	Inner Metro Boston	02468	Waban	Unofficial	Newton
4b	Inner Metro Boston	02477	Watertown	Official	Watertown
4b	Inner Metro Boston	02472	Watertown	Official	Watertown
4b	Inner Metro Boston	02471	Watertown	Official	Watertown
4b	Inner Metro Boston	02479	Waverley	Unofficial	Belmont
4b	Inner Metro Boston	02482	Wellesley	Official	Wellesley
4b	Inner Metro Boston	02481	Wellesley Hills	Unofficial	Wellesley
4b	Inner Metro Boston	02465	West Newton	Unofficial	Newton
4b	Inner Metro Boston	02090	Westwood	Official	Westwood
4b	Inner Metro Boston	02189	Weymouth	Official	Weymouth
4b	Inner Metro Boston	02191	Weymouth	Official	Weymouth
4b	Inner Metro Boston	02190	Weymouth	Official	Weymouth
4b	Inner Metro Boston	02188	Weymouth	Official	Weymouth
4b	Inner Metro Boston	02152	Winthrop	Official	Winthrop
4c	Boston	02134	Allston	Unofficial	Boston
4c	Boston	02106	Boston	Official	Boston
4c	Boston	02112	Boston	Official	Boston
4c	Boston	02101	Boston	Official	Boston
4c	Boston	02102	Boston	Official	Boston
4c	Boston	02103	Boston	Official	Boston
4c	Boston	02104	Boston	Official	Boston
4c	Boston	02105	Boston	Official	Boston
4c	Boston	02211	Boston	Official	Boston
4c	Boston	02201	Boston	Official	Boston
4c	Boston	02110	Boston	Official	Boston
4c	Boston	02203	Boston	Official	Boston
4c	Boston	02204	Boston	Official	Boston
4c	Boston	02205	Boston	Official	Boston
4c	Boston	02206	Boston	Official	Boston
4c	Boston	02297	Boston	Official	Boston
4c	Boston	02207	Boston	Official	Boston
4c	Boston	02208	Boston	Official	Boston
4c	Boston	02107	Boston	Official	Boston
4c	Boston	02210	Boston	Official	Boston
4c	Boston	02199	Boston	Official	Boston
4c	Boston	02212	Boston	Official	Boston
4c	Boston	02215	Boston	Official	Boston
4c	Boston	02216	Boston	Official	Boston
4c	Boston	02217	Boston	Official	Boston
4c	Boston	02266	Boston	Official	Boston
4c	Boston	02241	Boston	Official	Boston
4c	Boston	02283	Boston	Official	Boston
4c	Boston	02284	Boston	Official	Boston
4c	Boston	02293	Boston	Official	Boston
4c	Boston	02295	Boston	Official	Boston
4c	Boston	02209	Boston	Official	Boston
4c	Boston	02118	Boston	Official	Boston
4c	Boston	02108	Boston	Official	Boston
4c	Boston	02109	Boston	Official	Boston
4c	Boston	02222	Boston	Official	Boston
4c	Boston	02111	Boston	Official	Boston
4c	Boston	02113	Boston	Official	Boston
4c	Boston	02114	Boston	Official	Boston
4c	Boston	02115	Boston	Official	Boston
4c	Boston	02202	Boston	Official	Boston
4c	Boston	02117	Boston	Official	Boston
4c	Boston	02196	Boston	Official	Boston
4c	Boston	02119	Boston	Official	Boston
4c	Boston	02120	Boston	Official	Boston
4c	Boston	02121	Boston	Official	Boston
4c	Boston	02122	Boston	Official	Boston
4c	Boston	02123	Boston	Official	Boston
4c	Boston	02124	Boston	Official	Boston
4c	Boston	02125	Boston	Official	Boston
4c	Boston	02127	Boston	Official	Boston
4c	Boston	02128	Boston	Official	Boston
4c	Boston	02133	Boston	Official	Boston
4c	Boston	02163	Boston	Official	Boston
4c	Boston	02116	Boston	Official	Boston
4c	Boston	02135	Brighton	Unofficial	Boston
4c	Boston	02129	Charlestown	Unofficial	Boston
4c	Boston	02228	East Boston	Unofficial	Boston
4c	Boston	02136	Hyde Park	Unofficial	Boston
4c	Boston	02130	Jamaica Plain	Unofficial	Boston
4c	Boston	02126	Mattapan	Unofficial	Boston
4c	Boston	02137	Readville	Unofficial	Boston
4c	Boston	02131	Roslindale	Unofficial	Boston
4c	Boston	02132	West Roxbury	Unofficial	Boston
5	Southeast	02351	Abington	Official	Abington
5	Southeast	02743	Acushnet	Official	Acushnet
5	Southeast	02702	Assonet	Unofficial	Freetown
5	Southeast	02703	Attleboro	Official	Attleboro
5	Southeast	02763	Attleboro Falls	Unofficial	North Attleborough
5	Southeast	02322	Avon	Official	Avon
5	Southeast	02630	Barnstable	Official	Barnstable
5	Southeast	02779	Berkley	Official	Berkley
5	Southeast	02020	Brant Rock	Unofficial	Marshfield
5	Southeast	02631	Brewster	Official	Brewster
5	Southeast	02325	Bridgewater	Official	Bridgewater
5	Southeast	02324	Bridgewater	Official	Bridgewater
5	Southeast	02302	Brockton	Official	Brockton
5	Southeast	02303	Brockton	Official	Brockton
5	Southeast	02301	Brockton	Official	Brockton
5	Southeast	02304	Brockton	Official	Brockton
5	Southeast	02305	Brockton	Official	Brockton
5	Southeast	02327	Bryantville	Unofficial	Pembroke
5	Southeast	02542	Buzzards Bay	Unofficial	Bourne
5	Southeast	02532	Buzzards Bay	Unofficial	Bourne
5	Southeast	02330	Carver	Official	Carver
5	Southeast	02534	Cataumet	Unofficial	Bourne
5	Southeast	02636	Centerville	Unofficial	Barnstable
5	Southeast	02634	Centerville	Unofficial	Barnstable
5	Southeast	02632	Centerville	Unofficial	Barnstable
5	Southeast	02712	Chartley	Unofficial	Norton
5	Southeast	02633	Chatham	Official	Chatham
5	Southeast	02535	Chilmark	Official	Chilmark
5	Southeast	02635	Cotuit	Unofficial	Barnstable
5	Southeast	02637	Cummaquid	Unofficial	Barnstable
5	Southeast	02713	Cuttyhunk	Unofficial	Gosnold
5	Southeast	02714	Dartmouth	Official	Dartmouth
5	Southeast	02638	Dennis	Official	Dennis
5	Southeast	02639	Dennis Port	Unofficial	Dennis
5	Southeast	02715	Dighton	Official	Dighton
5	Southeast	02331	Duxbury	Official	Duxbury
5	Southeast	02332	Duxbury	Official	Duxbury
5	Southeast	02333	East Bridgewater	Official	East Bridgewater
5	Southeast	02641	East Dennis	Unofficial	Dennis
5	Southeast	02536	East Falmouth	Unofficial	Falmouth
5	Southeast	02717	East Freetown	Unofficial	Freetown
5	Southeast	02031	East Mansfield	Unofficial	Mansfield
5	Southeast	02643	East Orleans	Unofficial	Orleans
5	Southeast	02537	East Sandwich	Unofficial	Sandwich
5	Southeast	02718	East Taunton	Unofficial	Taunton
5	Southeast	02538	East Wareham	Unofficial	Wareham
5	Southeast	02642	Eastham	Official	Eastham
5	Southeast	02334	Easton	Official	Easton
5	Southeast	02539	Edgartown	Official	Edgartown
5	Southeast	02337	Elmwood	Unofficial	East Bridgewater
5	Southeast	02719	Fairhaven	Official	Fairhaven
5	Southeast	02720	Fall River	Official	Fall River
5	Southeast	02721	Fall River	Official	Fall River
5	Southeast	02724	Fall River	Official	Fall River
5	Southeast	02722	Fall River	Official	Fall River
5	Southeast	02723	Fall River	Official	Fall River
5	Southeast	02541	Falmouth	Official	Falmouth
5	Southeast	02540	Falmouth	Official	Falmouth
5	Southeast	02644	Forestdale	Unofficial	Sandwich
5	Southeast	02035	Foxborough	Official	Foxborough
5	Southeast	02041	Green Harbor	Unofficial	Marshfield
5	Southeast	02338	Halifax	Official	Halifax
5	Southeast	02341	Hanson	Official	Hanson
5	Southeast	02645	Harwich	Official	Harwich
5	Southeast	02343	Holbrook	Official	Holbrook
5	Southeast	02601	Hyannis	Unofficial	Barnstable
5	Southeast	02647	Hyannis Port	Unofficial	Barnstable
5	Southeast	02364	Kingston	Official	Kingston
5	Southeast	02347	Lakeville	Official	Lakeville
5	Southeast	02345	Manomet	Unofficial	Plymouth
5	Southeast	02048	Mansfield	Official	Mansfield
5	Southeast	02738	Marion	Official	Marion
5	Southeast	02050	Marshfield	Official	Marshfield
5	Southeast	02051	Marshfield Hills	Unofficial	Marshfield
5	Southeast	02648	Marston Mills	Unofficial	Barnstable
5	Southeast	02649	Mashpee	Official	Mashpee
5	Southeast	02739	Mattapoisett	Official	Mattapoisett
5	Southeast	02552	Menemsha	Unofficial	Chilmark
5	Southeast	02344	Middleborough	Official	Middleborough
5	Southeast	02348	Middleborough	Official	Middleborough
5	Southeast	02349	Middleborough	Official	Middleborough
5	Southeast	02346	Middleborough	Official	Middleborough
5	Southeast	02055	Minot Scituate	Unofficial	Plymouth
5	Southeast	02350	Monponsett	Unofficial	Hanson
5	Southeast	02553	Monument Beach	Unofficial	Bourne
5	Southeast	02584	Nantucket	Official	Nantucket
5	Southeast	02554	Nantucket	Official	Nantucket
5	Southeast	02744	New Bedford	Official	New Bedford
5	Southeast	02740	New Bedford	Official	New Bedford
5	Southeast	02741	New Bedford	Official	New Bedford
5	Southeast	02745	New Bedford	Official	New Bedford
5	Southeast	02742	New Bedford	Official	New Bedford
5	Southeast	02746	New Bedford	Official	New Bedford
5	Southeast	02761	North Attleborough	Official	North Attleborough
5	Southeast	02760	North Attleborough	Official	North Attleborough
5	Southeast	02355	North Carver	Unofficial	Carver
5	Southeast	02650	North Chatham	Unofficial	Chatham
5	Southeast	02747	North Dartmouth	Unofficial	Dartmouth
5	Southeast	02764	North Dighton	Unofficial	Dighton
5	Southeast	02651	North Eastham	Unofficial	Eastham
5	Southeast	02356	North Easton	Unofficial	Easton
5	Southeast	02357	North Easton	Unofficial	Easton
5	Southeast	02556	North Falmouth	Unofficial	Falmouth
5	Southeast	02059	North Marshfield	Unofficial	Marshfield
5	Southeast	02358	North Pembroke	Unofficial	Pembroke
5	Southeast	02652	North Truro	Unofficial	Truro
5	Southeast	02766	Norton	Official	Norton
5	Southeast	02557	Oak Bluffs	Official	Oak Bluffs
5	Southeast	02065	Ocean Bluff	Unofficial	Marshfield
5	Southeast	02558	Onset	Unofficial	Wareham
5	Southeast	02653	Orleans	Official	Orleans
5	Southeast	02655	Osterville	Unofficial	Barnstable
5	Southeast	02359	Pembroke	Official	Pembroke
5	Southeast	02762	Plainville	Official	Plainville
5	Southeast	02360	Plymouth	Official	Plymouth
5	Southeast	02361	Plymouth	Official	Plymouth
5	Southeast	02362	Plymouth	Official	Plymouth
5	Southeast	02367	Plympton	Official	Plympton
5	Southeast	02559	Pocasset	Unofficial	Bourne
5	Southeast	02657	Provincetown	Official	Provincetown
5	Southeast	02368	Randolph	Official	Randolph
5	Southeast	02767	Raynham	Official	Raynham
5	Southeast	02768	Raynham Center	Unofficial	Raynham
5	Southeast	02769	Rehoboth	Official	Rehoboth
5	Southeast	02770	Rochester	Official	Rochester
5	Southeast	02370	Rockland	Official	Rockland
5	Southeast	02561	Sagamore	Unofficial	Bourne
5	Southeast	02562	Sagamore Beach	Unofficial	Bourne
5	Southeast	02563	Sandwich	Official	Sandwich
5	Southeast	02771	Seekonk	Official	Seekonk
5	Southeast	02564	Siasconset	Unofficial	Nantucket
5	Southeast	02565	Silver Beach	Unofficial	Falmouth
5	Southeast	02725	Somerset	Official	Somerset
5	Southeast	02726	Somerset	Official	Somerset
5	Southeast	02366	South Carver	Unofficial	Carver
5	Southeast	02659	South Chatham	Unofficial	Chatham
5	Southeast	02748	South Dartmouth	Unofficial	Dartmouth
5	Southeast	02660	South Dennis	Unofficial	Dennis
5	Southeast	02375	South Easton	Unofficial	Easton
5	Southeast	02661	South Harwich	Unofficial	Harwich
5	Southeast	02662	South Orleans	Unofficial	Orleans
5	Southeast	02663	South Wellfleet	Unofficial	Wellfleet
5	Southeast	02664	South Yarmouth	Unofficial	Yarmouth
5	Southeast	02072	Stoughton	Official	Stoughton
5	Southeast	02777	Swansea	Official	Swansea
5	Southeast	02783	Taunton	Official	Taunton
5	Southeast	02780	Taunton	Official	Taunton
5	Southeast	02666	Truro	Official	Truro
5	Southeast	02568	Vineyard Haven	Unofficial	Tisbury
5	Southeast	02571	Wareham	Official	Wareham
5	Southeast	02667	Wellfleet	Official	Wellfleet
5	Southeast	02668	West Barnstable	Unofficial	Barnstable
5	Southeast	02379	West Bridgewater	Official	West Bridgewater
5	Southeast	02669	West Chatham	Unofficial	Chatham
5	Southeast	02573	West Chop	Unofficial	Tisbury
5	Southeast	02670	West Dennis	Unofficial	Dennis
5	Southeast	02574	West Falmouth	Unofficial	Falmouth
5	Southeast	02671	West Harwich	Unofficial	Harwich
5	Southeast	02672	West Hyannisport	Unofficial	Barnstable
5	Southeast	02575	West Tisbury	Official	West Tisbury
5	Southeast	02576	West Wareham	Unofficial	Wareham
5	Southeast	02673	West Yarmouth	Unofficial	Yarmouth
5	Southeast	02790	Westport	Official	Westport
5	Southeast	02791	Westport Point	Unofficial	Westport
5	Southeast	02381	White Horse Beach	Unofficial	Plymouth
5	Southeast	02382	Whitman	Official	Whitman
5	Southeast	02543	Woods Hole	Unofficial	Falmouth
5	Southeast	02675	Yarmouth Port	Unofficial	Yarmouth
5	Southeast	02535	Aquinnah	Official	Aquinnah
5	Southeast	02532	Bourne	Official	Bourne
5	Southeast	02702	Freetown	Official	Freetown
5	Southeast	02713	Gosnold	Official	Gosnold
5	Southeast	02557	Tisbury	Official	Tisbury
5	Southeast	02664	Yarmouth	Official	Yarmouth
.	Unknown	00000	n/a	Official	n/a
.	Unknown	01434	Fort Devens Station	Unofficial	Ayer""".split('\n')[1:] # drop header
# BT Region	Region Name	Zip Code 5	Locality Name	Locality Type	City Name
btzip = [x.strip().split('\t') for x in btzip]
btzips = [x[2] for x in btzip] # just the zip codes
btcodes = [x[0] for x in btzip]
btzipdict = dict(zip(btzips,btcodes)) # given a 5 digit zip return the bt region code
    
    
