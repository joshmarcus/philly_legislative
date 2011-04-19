Councilmatic!
=============
Philly City Council Legislative Subscription Service.

Contact Us
----------
- Join the mailing list at https://groups.google.com/group/councilmatic/
- Find us on irc.freenode.net in the #councilmatic room

Getting Started
---------------
To work on your own instance of Councilmatic, you should first get Python
installed. Follow the instructions for doing so on your platform. Next, install
Django (we recommend working in a virtual environment, but it's not strictly
necessary).

    $ pip install Django

Now check out the project code.

    $ git clone git://github.com/codeforamerica/philly_legislative.git

Set up the project database and populate it with city council data (when the
syncdb command prompts you to create an administrative user, go ahead and do
so). There is a lot of data to be loaded, so downloading it all may take a
while. If you're familiar with this routine, you can skip that step.

    $ cd philly_legislative
    $ python manage.py syncdb
    $ python manage.py loadlegfiles

Finally, to run the server:

    $ python manage.py runserver

Now, check that everything is working by browsing to http://localhost:8000/.  Now browse to http://localhost:8000/admin and enter the admin username and password you supplied and you should have access to all of the legislative files!

Usage Examples
--------------
    import likeminded
    
    api = likeminded.Api(key='yourapikey')
    
    # Search resources and projects
    results = api.search(query='search term')
    
    # Iterate through search results
    for reference in results:
        print reference

Copyright
---------
Copyright (c) 2010 Code for America Laboratories
See [LICENSE](https://github.com/cfalabs/open311/blob/master/LICENSE.mkd) for details.
