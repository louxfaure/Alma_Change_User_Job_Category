#!/usr/bin/python3
# -*- coding: utf-8 -*-
#Modules externes
import os
import re
import logging
import csv
import json
from chardet import detect

#Modules maison
from Alma_Apis_Interface import Alma_Apis_Users
from logs import logs

SERVICE = "Alma_Change_User_Job_Category"

LOGS_LEVEL = 'DEBUG'
LOGS_DIR = os.getenv('LOGS_PATH')

TEST = False

# FILE_NAME = 'test'
IN_REP = '/media/sf_LouxBox/Comptes pro et moniteurs/'
# in_file = '/media/sf_LouxBox/Comptes pro et moniteurs/{}.csv'.format(FILE_NAME)


#Init logger
logs.init_logs(LOGS_DIR,SERVICE,LOGS_LEVEL)
logger = logging.getLogger(SERVICE)

# get file encoding type
def get_encoding_type(file):
    with open(file, 'rb') as f:
        rawdata = f.read()
    return detect(rawdata)['encoding']

logger.debug("DEBUT DU TRAITEMENT")
list_file = os.listdir(IN_REP)
for in_file in list_file :
    parameters = re.search('^(.*?)_(.*?)\.csv', in_file)
    institution = parameters.group(1)
    if parameters.group(2) == 'Professionnels':
        job_cat_type = 'Professionnel'
    else :
        job_cat_type = 'Moniteur étudiant'
    logger.debug("{} : {}".format(institution, job_cat_type))
    if TEST : 
        api_key = os.getenv("TEST_{}_API".format(institution.upper())) 
    else :
        api_key = os.getenv("PROD_{}_USER_API".format(institution.upper())) 
    api = Alma_Apis_Users.AlmaUsers(apikey=api_key, region='EU', service='Alma_Change_User_Job_Category')
    ##Ouverture du fichier
    ###################### 
    from_codec = get_encoding_type("{}{}".format(IN_REP,in_file))
    with open("{}{}".format(IN_REP,in_file), 'r', encoding=from_codec, newline='') as f:
        reader = csv.reader(f, delimiter=';')
        logger.debug("Fichier {} ouvert avec succés".format(in_file))
        for row in reader:
            pid = row[0]
            logger.debug("Début de traitement : {}".format(pid))
            status, user = api.get_user(pid,user_expand='none',user_id_type='PRIMARYIDENTIFIER',user_view='brief',accept='json')
            user["job_category"] = {
                "desc": job_cat_type,
                "value": job_cat_type
            }
            # logger.debug(json.dumps(user, indent=4, sort_keys=True))
            status, response = api.update_user(pid, override='job_category', data=json.dumps(user, indent=4, sort_keys=True) ,accept='json',content_type='json')
            logger.debug("Fin du traitement : {}".format(pid))
            # logger.debug(json.dumps(response, indent=4, sort_keys=True))
logger.debug("FIN DU DEPLACEMENT DES USAGERS")
logger.debug("FIN DU TRAITEMENT")