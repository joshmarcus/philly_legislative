from django.contrib import admin
from phillyleg.models import Subscription
from phillyleg.models import *

class KeywordInline(admin.StackedInline):
    model = KeywordSubscription
    extra = 3

class SubscriptionAdmin(admin.ModelAdmin):
    inlines = [KeywordInline]    


admin.site.register(Subscription, SubscriptionAdmin)
admin.site.register(KeywordSubscription)
admin.site.register(LegFile)
admin.site.register(CouncilMember)
