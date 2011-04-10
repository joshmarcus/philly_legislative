from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Subscription(models.Model):
#   user   = models.ForeignKey(User, unique=True)
    email  = models.CharField(max_length=100)
    lastId = models.IntegerField()

    def __unicode__(self):
        return self.email

class Keyword(models.Model):
    subscription = models.ForeignKey(Subscription)
    keyword = models.CharField(max_length=50)
    
    def __unicode__(self):
        return self.keyword

class CouncilMember(models.Model):
    subcription = models.ForeignKey(Subscription)
    name = models.CharField(max_length=100)


class LegFile(models.Model):
    key = models.IntegerField(primary_key=True)
    contact = models.CharField(max_length=1000)
    controlling_body = models.CharField(max_length=1000)
    date_scraped = models.CharField(max_length=1000)
    final_date = models.CharField(max_length=1000)
    intro_date = models.CharField(max_length=1000)
    sponsors = models.CharField(max_length=1000)
    status = models.CharField(max_length=1000)
    title = models.CharField(max_length=1000)
    type = models.CharField(max_length=1000)
    url = models.CharField(max_length=1000)
    version = models.CharField(max_length=100)

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

