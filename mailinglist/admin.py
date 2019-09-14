from django.contrib import admin
from mailinglist.models import MailingList,Subscriber,Message
# Register your models here.
admin.site.register(Subscriber)
admin.site.register(MailingList)
admin.site.register(Message)
