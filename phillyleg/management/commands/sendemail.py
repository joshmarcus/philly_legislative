#will send out daily email for users - first will read all keywords
#create text files, then email text files to all each user subscribed.

from django.core.management.base import BaseCommand, CommandError
import smtplib, poplib
import django, datetime
from email.mime.text import MIMEText
from phillyleg.models import Subscription, KeywordSubscription, LegFile

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
			legfile_set = set()
			
			# Collect all the keyword leg files.
			for k in em.keywords.all():
				if not k:
					continue
				
				legfiles = LegFile.objects\
					.filter(title__icontains=k)\
					.filter(last_scraped__gt=em.last_sent)
					
				for legfile in legfiles:
					legfile_set.add(legfile)
			
			# Write emails for all the selected leg files
			emailbody = self.makeBillEmail(
				legfile_set, [str(k) for k in em.keywords.all()])
			
			# Send the email
			self.send_email(str(em), emailbody)
			
	def makeBillEmail(self, bills, keywords=None):
		body = self.DIVIDER
		if keywords:
			body += "Keywords: %s\n" %  (','.join(keywords))
		body += self.DIVIDER +"\n"
		
		for bill in bills:
			bill_body = bill.title + "\n\n"
			bill_body += "Sponsors: %s\n\n" % \
				(', '.join([s.name for s in bill.sponsors.all()]))
			bill_body += "Current Status: %s\n\n" % bill.status
			bill_body += "Full Text and more information: %s\n\n" % bill.url
			body += "\n%s\n%s\n" % (bill_body, self.SINGLE_DIVIDER)
		
		return body
		
	
	
