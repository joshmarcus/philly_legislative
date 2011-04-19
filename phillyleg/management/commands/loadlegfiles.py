###############################################################################
# This will collect the latest legislative filings released in the city of
# Philadelphia.
###############################################################################

#will send out daily email for users - first will read all keywords
#create text files, then email text files to all each user subscribed.

import datetime
import sqlite3
import urllib2
from django.core.management.base import BaseCommand, CommandError
import django
from BeautifulSoup import BeautifulSoup

from phillyleg.models import \
    LegFile, LegFileAttachment, LegAction, CouncilMember

class Command(BaseCommand):
    help = "Load new legislative file data from the Legistar city council site."
    
    def handle(self, *args, **options):
        self._get_updated_files()
        self._get_new_files()
    
    def _get_updated_files(self):
        pass
    
    def _get_new_files(self):
        # Create a datastore wrapper object
        ds = CouncilmaticDataStoreWrapper()
        source = ScraperWikiSourceWrapper()

        # Get the latest filings
        curr_key = ds.get_latest_key()

        while True:
            curr_key, soup = source.check_for_new_content(curr_key)
            
            if soup is None:
                break
            
            record, attachments, actions = source.scrape_legis_file(curr_key, soup)
            ds.save_legis_file(record, attachments, actions)
            

STARTING_KEY = 72 # The highest key was 11001 as of 5 Apr 2011
class PhillyLegistarSiteWrapper (object):
    STARTING_URL = 'http://legislation.phila.gov/detailreport/?key='

    def scrape_legis_file(self, key, soup):
        '''Extract a record from the given document (soup). The key is for the
           sake of record-keeping.  It is the key passed to the site URL.'''
        
        span = soup.find('span', {'id':'lblFileNumberValue'})
        lid = span.text
        
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
            'id' : lid,
            'url' : self.STARTING_URL + str(key),
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
        
        attachments = self.scrape_legis_attachments(key, soup)
        actions = self.scrape_legis_actions(key, soup)
        
        print record, attachments, actions
        return record, attachments, actions

    def scrape_legis_attachments(self, key, soup):
        
        attachments = []
        
        attach_div = soup.find('div', {'id' : 'divAttachmentsValue'})
        for cell in attach_div.findAll('a'):
            attachment = {
                'key' : key,
                'description' : cell.text,
                'url' : cell['href'],
            }
            attachments.append(attachment)

        return attachments

    def scrape_legis_actions(self, key, soup):

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
        
        notes = []
        actions = []
        
        action_div = soup.find('div', {'id': 'divScroll'})
        action_rows = action_div.findAll('tr')

        for action_row in action_rows:
            cells = action_row.findAll('td')
            
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
        

    def is_error_page(self, soup):
        '''Check the given soup to see if it represents an error page.'''
        error_p = soup.find('p', 'errorText')

        if error_p is None: return False
        else: return True

    def check_for_new_content(self, last_key):
        '''Look through the next 10 keys to see if there are any more files.
           10 is arbitrary, but I feel like it's large enough to be safe.'''

        curr_key = last_key
        for _ in xrange(10):
            curr_key = curr_key + 1
            html = urllib2.urlopen(self.STARTING_URL + str(curr_key))
            soup = BeautifulSoup(html)
        
            if not self.is_error_page(soup):
                return curr_key, soup

        return curr_key, None

class ScraperWikiSourceWrapper (object):
    __cursor = None
    
    def scrape_legis_file(self, key, cursor):
        '''Extract a record from the given document (soup). The key is for the
           sake of record-keeping.  It is the key passed to the site URL.'''
        
        cursor.execute('''select
            id,type,url,status,title,controlling_body,intro_date,final_date,
            version,contact,sponsors from swdata where key=?''', (key,))
        
        row = cursor.fetchone()
        print row
        lid, ltype, lurl, lstatus, ltitle, lbody, lintro, lfinal, \
        lversion, lcontact, lsponsors = row
        
        record = {
            'key' : key,
            'id' : lid,
            'url' : lurl,
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
        
        attachments = self.scrape_legis_attachments(key, cursor)
        actions = self.scrape_legis_actions(key, cursor)
        
        print record, attachments, actions
        return record, attachments, actions

    def scrape_legis_attachments(self, key, cursor):
        
        cursor.execute('''select description,url
            from attachments where key=?''', (key,))
        
        attachments = []
        
        for row in cursor:
            attachment = {
                'key' : key,
                'description' : row[0],
                'url' : row[1],
            }
            attachments.append(attachment)

        return attachments

    def scrape_legis_actions(self, key, cursor):
        
        cursor.execute('''select 
            date_taken,acting_body,description,motion,minutes_url,notes
            from actions where key=?''', (key,))
        
        actions = []
        
        for action_row in cursor:
            action = {
                'key' : key,
                'date_taken' : action_row[0],
                'acting_body' : action_row[1],
                'description' : action_row[2],
                'motion' : action_row[3],
                'minutes_url' : action_row[4],
                'notes' : action_row[5],
            }
            actions.append(action)
        
        return actions
        
    def __download_db(self):
        print "Downloading the database (~20M -- this may take a while)..."
        db_file = urllib2.urlopen('http://scraperwiki.com/scrapers/export_sqlite/philadelphia_legislative_files/')
        db = db_file.read()
        outfile = open('swdata.sqlite3', 'w')
        outfile.write(db)
        outfile.close()
    
    def __connect_to_db(self):
        conn = sqlite3.connect('swdata.sqlite3')
        self.__cursor = conn.cursor()

    def check_for_new_content(self, last_key):
        '''Look through the next 10 keys to see if there are any more files.
           10 is arbitrary, but I feel like it's large enough to be safe.'''
        
        if not self.__cursor:
            self.__download_db()
            self.__connect_to_db()
        
        cursor = self.__cursor
        
        cursor.execute('''select key 
            from swdata 
            where key > ?
            order by key''', (last_key,))
        
        row = cursor.fetchone()
        if row:
            return int(row[0]), cursor

        return curr_key, None

class CouncilmaticDataStoreWrapper (object):
    """
    This is the interface over an arbitrary database where the information is 
    being stored.  I'm using it primarily because I want the scraper code to be
    used on both ScraperWiki and in my Django app on my Django models.  For my
    app, I want local access to the data.  But I love ScraperWiki as a central
    place where you can find data about anything you want, so it's important to
    have the data available on SW as well.
    """
    def get_latest_key(self):
        '''Check the datastore for the key of the most recent filing.'''

        records = LegFile.objects.order_by('-key')
        try:
            return records[0].key
        except IndexError:
            return STARTING_KEY
    
    def save_legis_file(self, file_record, attachment_records, action_records):
        """
        Take a legislative file record and do whatever needs to be
        done to get it into the database.
        """
        file_record = self.__convert_or_delete_date(file_record, 'intro_date')
        file_record = self.__convert_or_delete_date(file_record, 'final_date')
        
        # Don't include the sponsors list, as the model framework doesn't allow
        # batch inserting of lists for a ManyToManyField, and we will need to 
        # insert each sponsor individually.  See below in 'Create the record'.
        sponsor_names = file_record['sponsors']
        del file_record['sponsors']
        
        # Create the record
        legfile = LegFile(**file_record)
        for sponsor_name in sponsor_names.split(','):
            sponsor_name = sponsor_name.strip()
            sponsor = CouncilMember.objects.get_or_create(name=sponsor_name)[0]
            legfile.sponsors.add(sponsor)
        legfile.save()
        
        # Create notes attached to the record
        for attachment_record in attachment_records:
            attachment_record = self.__replace_key_with_legfile(attachment_record)
            self.__save_or_ignore(LegFileAttachment, attachment_record)
        
        # Create actions attached to the record
        for action_record in action_records:
            action_record = self.__replace_key_with_legfile(action_record)
            self.__save_or_ignore(LegAction, action_record)
    
    def __convert_or_delete_date(self, file_record, date_key):
        if file_record[date_key]:
            file_record[date_key] = datetime.datetime.strptime(
                file_record[date_key], '%m/%d/%Y')
        else:
            del file_record[date_key]
        
        return file_record
    
    def __replace_key_with_legfile(self, record):
        legfile = LegFile.objects.get(key=record['key'])
        del record['key']
        record['file'] = legfile
        
        return record
    
    def __save_or_ignore(self, ModelClass, record):
        model_instance = ModelClass(**record)
        try:
            model_instance.save()
            return True
        except:
            # If it's a duplicate, don't worry about it.  Just move on.
            return False


