import sys
from django.core.management.base import BaseCommand, CommandError
import smtplib, poplib
import django
from email.mime.text import MIMEText
from phillyleg.models import Subscription, Keyword, LegFile
import csv

class Command(BaseCommand):
    help = "python manage.py csvimport CSVFILE"
    def handle(self,  *args, **options):
        csvpath = args[0]
        reader = csv.reader(open(csvpath, 'r'))
        reader.next()
        for row in reader:
            d = {
                'status': row[0],
                'title': row[1],
                'url': row[2],
                'sponsors': row[3],
                'controlling_body': row[4],
                'contact': row[5],
                'version': row[6],
                'key': row[7],
                'final_date': row[8],
                'intro_date': row[9],
                'type': row[10],
            }
        
            LegFile.objects.get_or_create(**d)
