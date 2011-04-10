###############################################################################
# This will collect the latest legislative filings released in the city of
# Philadelphia.
###############################################################################

#will send out daily email for users - first will read all keywords
#create text files, then email text files to all each user subscribed.

from django.core.management.base import BaseCommand, CommandError
import smtplib, poplib
import django
from email.mime.text import MIMEText
from BeautifulSoup import BeautifulSoup

from phillyleg.models import LegFile

class Command(BaseCommand):
	help = "test help"
	
	def send_email(self, you, text, emailbody):
		smtphost = "smtp.gmail.com"
		smtpport = '465'
		me =  'philly.legislative.list'
		msg = MIMEText(emailbody)
		msg['Subject'] = "Philly Legislative Digest: %s"%", ".join(text)
		msg['From'] = me
		msg['To'] = you
		s = smtplib.SMTP_SSL(smtphost, smtpport)
		s.login(me, 'phillydatacamp')
		s.sendmail(me, [you], msg.as_string())
		s.quit()

	def handle(self, *args, **options):
        # First, get the latest filings
        last_key = get_latest_key()
        curr_key = last_key

        while True:
            curr_key, soup = check_for_new_content(curr_key)
            
            if soup is None:
                break
            
            record = scrape_legis_file(curr_key, soup)
            save_record(record)
            scraperwiki.datastore.save(['key'], record)
            

			
	def makeBillEmail(self, keyw):
		bill = LegFile.objects.filter(title__icontains=keyw)
		body =""
		for b in bill:
			body += b.title + "\n"
		return body
	
# retrieve a page
starting_url = 'http://legislation.phila.gov/detailreport/?key='
starting_key = 11001 # The highest key was 11001 as of 5 Apr 2011

def scrape_legis_file(key, soup):
    '''Extract a record from the given document (soup). The key is for the
       sake of record-keeping.  It is the key passed to the site URL.'''

    span = soup.find('span', {'id':'lblFileTypeValue'})
    ltype = span.text

    span = soup.find('span', {'id':'lblFileStatusValue'})
    lstatus = span.text

    span = soup.find('span', {'id':'lblTitleValue'})
    ltitle = span.text

    span = soup.find('span', {'id':'lblControllingBodyValue'})
    lbody = span.text

    span = soup.find('span', {'id':'lblIntroDateValue'})
    lintro = span.text

    span = soup.find('span', {'id':'lblFinalActionValue'})
    lfinal = span.text

    span = soup.find('span', {'id':'lblVersionValue'})
    lversion = span.text
    
    span = soup.find('span', {'id':'lblContactValue'})
    lcontact = span.text
    
    span = soup.find('span', {'id':'lblSponsorsValue'})
    lsponsors = span.text
    
    record = {
        'key' : key,
        'url' : starting_url + str(key),
        'type' : ltype,
        'status' : lstatus,
        'title' : ltitle,
        'controlling_body' : lbody,
        'intro_date' : lintro,
        'final_date' : lfinal,
        'version' : lversion,
        'contact' : lcontact,
        'sponsors' : lsponsors
    }
    print record
    return record

def is_error_page(soup):
    '''Check the given soup to see if it represents an error page.'''
    error_p = soup.find('p', 'errorText')

    if error_p is None: return False
    else: return True

def get_latest_key():
    '''Check the datastore for the key of the most recent filing.'''

    max_key = starting_key

    scraperwiki.sqlite.attach('philadelphia_legislative_files') 
    records = scraperwiki.sqlite.select('* from `philadelphia_legislative_files`.swdata')

    for record in records:
        if isinstance(record, basestring):
            continue # If there are no elements, a string will be returned
        max_key = max(max_key, record['key'])
    return int(max_key)

def check_for_new_content(last_key):
    '''Look through the next 10 keys to see if there are any more files.
       10 is arbitrary, but I feel like it's large enough to be safe.'''

    curr_key = last_key
    for _ in xrange(10):
        curr_key = curr_key + 1
        html = scraperwiki.scrape(starting_url + str(curr_key))
        soup = BeautifulSoup(html)
    
        if not is_error_page(soup):
            return curr_key, soup

    return curr_key, None

def save_legis_file(record):
    """
    Take a legislative file record and do whatever needs to be
    done to get it into the database.
    """
    scraperwiki.datastore.save(['key'], record)

