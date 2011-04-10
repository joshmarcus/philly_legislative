import os
import unittest
import BeautifulSoup as bs

from management.commands.loadlegfiles import scrape_legis_file

class TestLoadLegFiles (unittest.TestCase):
    def setUp(self):
        self.tests_dir = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            'testlegfiles'
        )
        
    def test_RecognizeNotesRow(self):
        # The history on some filings (like key=73) have notes.  These need to
        # be detected.
        html = open(os.path.join(self.tests_dir, 'key73.html')).read()
        soup = bs.BeautifulSoup(html)
        
        file_record, action_records = \
            scrape_legis_file(73, soup)
        
        self.assertEqual(
            len([act_rec for act_rec in action_records
                 if act_rec['notes']]), 2)
        
    
if __name__ == '__main__':
    unittest.main()
