#will send out daily email for users - first will read all keywords
#create text files, then email text files to all each user subscribed.

from django.core.management.base import BaseCommand, CommandError
import smtplib, poplib
import django, datetime
from email.mime.text import MIMEText
from phillyleg.models import Subscription, Keyword, LegFile

class Command(BaseCommand):
	help = "This script sends daily digests out to subscribers."
	EMAIL_TITLE = "PHILLY COUNCILMATIC " + datetime.date.today().__str__()
	DIVIDER = "====================================\n"
	SINGLE_DIVIDER = "-----------------------------------------------------------------"
	
	def send_email(self, you, emailbody):
		smtphost = "smtp.gmail.com"
		smtpport = '465'
		me =  'philly.legislative.list'
		msg = MIMEText(emailbody)
		msg['Subject'] = self.EMAIL_TITLE
		msg['From'] = me
		msg['To'] = you
		s = smtplib.SMTP_SSL(smtphost, smtpport)
		s.login(me, 'phillydatacamp')
		s.sendmail(me, [you], msg.as_string())
		s.quit()

	def handle(self, *args, **options):
		emails = Subscription.objects.all()
		emailbody = self.EMAIL_TITLE+"\n"
		for em in emails:
			for k in em.keyword_set.all():
				emailbody += self.makeBillEmail(str(k))
			self.send_email(str(em), emailbody)
			
	def makeBillEmail(self, keyw):
		bill = LegFile.objects.filter(title__icontains=keyw)
		body = self.DIVIDER
		body += "Keyword: "+ keyw + "\n"
		body += self.DIVIDER +"\n"
		
		for b in bill:
			body += b.title + "\n\n"
			body += "Sponsors: "+b.sponsors + "\n\n"
			body += "Current Status: "+b.status + "\n\n"
			body += "Full Text and more information: "+b.url + "\n\n"
		return "\n"+body + "\n" + self.SINGLE_DIVIDER + "\n"
		
	
	