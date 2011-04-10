###############################################################################
# This will collect the latest legislative filings released in the city of
# Philadelphia.
###############################################################################

#will send out daily email for users - first will read all keywords
#create text files, then email text files to all each user subscribed.

import urllib2
from django.core.management.base import BaseCommand, CommandError
import django
from BeautifulSoup import BeautifulSoup

from phillyleg.models import LegFile, LegAction

class Command(BaseCommand):
    help = "Load new legislative file data from the Legistar city council site."
    
    def handle(self, *args, **options):
        self._get_updated_files()
        self._get_new_files()
    
    def _get_updated_files(self):
        pass
    
    def _get_new_files(self):
        last_key = get_latest_key()
        curr_key = last_key

        while True:
            curr_key, soup = check_for_new_content(curr_key)
            
            if soup is None:
                break
            
            file_record, action_records = scrape_legis_file(curr_key, soup)
            save_legis_file(file_record, action_records)

##
# The following is adapted from the scraper at 
# http://scraperwiki.com/scrapers/philadelphia_legislative_files/
#

starting_url = 'http://legislation.phila.gov/detailreport/?key='
starting_key = 72 # The highest key was 11001 as of 5 Apr 2011

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
    
    actions = scrape_legis_actions(key, soup)
    
    print record, actions
    return record, actions

def scrape_legis_actions(key, soup):

    def get_action_cell_text(cell):
        cell_a = cell.find('a')
        if cell_a:
            return cell_a.text
        else:
            return cell.text
    
    def get_action_cell_resource(cell):
        cell_a = cell.find('a')
        if cell_a:
            return cell_a['href']
        else:
            return ''
    
    actions = []
    notes = []
    
    action_div = soup.find('div', {'id': 'divScroll'})
    action_rows = action_div.findAll('tr')

    for row in action_rows:
        cells = row.findAll('td')
        
        if len(cells) == 2:
            # Sometimes, there are notes interspersed in the history table.
            # Luckily (?) their rows have only two cells instead of four, so
            # we can easily tell that they're there.
            action = actions[-1]
            action['notes'] = cells[1].text
            continue
        
        action = {
            'key' : key,
            'date_taken' : get_action_cell_text(cells[0]),
            'acting_body' : get_action_cell_text(cells[1]),
            'description' : get_action_cell_text(cells[2]),
            'motion' : get_action_cell_text(cells[3]),
            'minutes_url' : get_action_cell_resource(cells[0]),
            'notes' : '',
        }
        actions.append(action)
    
    return actions
    
def is_error_page(soup):
    '''Check the given soup to see if it represents an error page.'''
    error_p = soup.find('p', 'errorText')

    if error_p is None: return False
    else: return True

def get_latest_key():
    '''Check the datastore for the key of the most recent filing.'''

    records = LegFile.objects.order_by('-key')
    try:
        return records[0].key
    except IndexError:
        return starting_key

def check_for_new_content(last_key):
    '''Look through the next 10 keys to see if there are any more files.
       10 is arbitrary, but I feel like it's large enough to be safe.'''

    curr_key = last_key
    for _ in xrange(10):
        curr_key = curr_key + 1
        html = urllib2.urlopen(starting_url + str(curr_key)).read()
        soup = BeautifulSoup(html)
    
        if not is_error_page(soup):
            return curr_key, soup

    return curr_key, None

def save_legis_file(file_record, action_records):
    """
    Take a legislative file record and do whatever needs to be
    done to get it into the database.
    """
    legfile = LegFile(**file_record)
    legfile.save()
    
    for action_record in action_records:
        legfile = LegFile.objects.get(key=action_record['key'])
        del action_record['key']
        action_record['file'] = legfile
        
        legaction = LegAction(**action_record)
        try:
            legaction.save()
        except:
            # If it's a duplicate, don't worry about it.  Just move on.
            continue

