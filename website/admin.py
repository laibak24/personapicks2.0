from django.contrib import admin

# Register your models here.

#to view our models in admin pannel
from .models import *
admin.site.register(User)
admin.site.register(Movie)   
admin.site.register(Book)  
admin.site.register(Watchlist)   
admin.site.register(Readlist)   
admin.site.register(Feedback)   
admin.site.register(MBTIType)   
admin.site.register(Recommendation)   

