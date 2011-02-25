from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Subscription(models.Model):
    #user = models.ForeignKey(User, unique=True)
    email = models.CharField(max_length=100)
    def __unicode__(self):
        return self.email

class Keyword(models.Model):
    subscription = models.ForeignKey(Subscription)
    keyword = models.CharField(max_length=50)
    
    def __unicode__(self):
        return self.keyword
