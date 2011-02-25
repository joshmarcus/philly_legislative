#will send out daily email for users - first will read all keywords
#create text files, then email text files to all each user subscribed.

from django.core.management.base import BaseCommand, CommandError
import smtplib, poplib
import django
from email.mime.text import MIMEText
from phillyleg.models import Subscription, Keyword, LegFile

class Command(BaseCommand):
	help = "test help"
	
	def send_email(self, you, text, emailbody):
		smtphost = "smtp.gmail.com"
		smtpport = '465'
		me =  'philly.legislative.list'
		msg = MIMEText(emailbody)
		msg['Subject'] = "Philly Legislative Digest: %s"%text
		msg['From'] = me
		msg['To'] = you
		s = smtplib.SMTP_SSL(smtphost, smtpport)
		s.login(me, 'phillydatacamp')
		s.sendmail(me, [you], msg.as_string())
		s.quit()

	def handle(self, *args, **options):
		emails = Subscription.objects.all()
		emailbody = ""
		for em in emails:
			keyw = []
			for k in em.keyword_set.all():
				keyw.append(str(k))
				emailbody += self.makeBillEmail(str(k))
			self.send_email(str(em), keyw, emailbody)
			
	def makeBillEmail(self, keyw):
		bill = LegFile.objects.filter(title__icontains=keyw)
		body =""
		for b in bill:
			body += b.title + "\n"
		return body
	
	