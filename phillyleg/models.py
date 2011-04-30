from django.db import models
from django.contrib.auth.models import User

# Create your models here.

#
# Legislative File models
#

class CouncilMember(models.Model):
    name = models.CharField(max_length=100)
    
    def __unicode__(self):
        return self.name.lstrip("Councilmember")


class LegFile(models.Model):
    key = models.IntegerField(primary_key=True)
    id = models.CharField(max_length=100, null=True)
    contact = models.CharField(max_length=1000)
    controlling_body = models.CharField(max_length=1000)
    date_scraped = models.DateTimeField(auto_now_add=True)
    last_scraped = models.DateTimeField(auto_now=True)
    final_date = models.DateField(null=True)
    intro_date = models.DateField(null=True)
    sponsors = models.ManyToManyField(CouncilMember)
    status = models.CharField(max_length=1000)
    title = models.TextField()
    type = models.CharField(max_length=1000)
    url = models.CharField(max_length=1000)
    version = models.CharField(max_length=100)
    
    def __unicode__(self):
        return "(%s) %s%s" % (self.key, self.title[:100], 
            '...' if len(self.title) > 100 else '')

class LegFileAttachment(models.Model):
    file = models.ForeignKey(LegFile)
    description = models.CharField(max_length=1000)
    url = models.CharField(max_length=1000)
    
    class Meta:
        unique_together = (('file','url'),)

class LegAction(models.Model):
    file = models.ForeignKey(LegFile)
    date_taken = models.CharField(max_length=1000)
    description = models.CharField(max_length=1000)
    minutes_url = models.CharField(max_length=1000)
    motion = models.CharField(max_length=1000)
    acting_body = models.CharField(max_length=1000)
    notes = models.TextField()
    
    class Meta:
        unique_together = (('file','date_taken','description','notes'),)


#
# Subscription models
#

class Subscription(models.Model):
#   user   = models.ForeignKey(User, unique=True)
    email  = models.CharField(max_length=100)
    last_sent = models.DateField(auto_now_add=True)
#    lastId = models.IntegerField()

    def __unicode__(self):
        return self.email

class KeywordSubscription(models.Model):
    subscription = models.ForeignKey(Subscription, related_name='keywords')
    keyword = models.CharField(max_length=50)
    
    def __unicode__(self):
        return self.keyword

class CouncilMemberSubscription(models.Model):
    subscription = models.ForeignKey(Subscription, related_name='councilmembers')
    councilmember = models.ForeignKey(CouncilMember)
    
    def __unicode__(self):
        return councilmember


