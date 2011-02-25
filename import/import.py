import sys
from django.core.management import setup_environ
sys.path.append(".")
import settings
setup_environ(settings)

from phillyleg.models import LegFile

import csv
reader = csv.reader(open("files.csv"))

# status,title,url,sponsors,controlling_body,contact,version,key,final_date,intro_date,type
for row in reader:
    _status = row[0]
    _title = row[1]
    _url = row[2]
    _sponsors = row[3]
    _controlling_body = row[4]
    _contact = row[5]
    _version = row[6]
    _key = int(row[7])
    _final_date = row[8]
    _intro_date = row[9]
    _type = row[10]

    LegFile.objects.get_or_create( status = _status, title = _title, url = _url, sponsors = _sponsors, controlling_body = _controlling_body, contact = _contact, version = _version, key = _key, final_date = _final_date, intro_date = _intro_date, type = _type ) 


