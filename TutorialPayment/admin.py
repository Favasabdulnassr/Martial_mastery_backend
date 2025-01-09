from django.contrib import admin
from .models import TutorWallet,Payment,TutorialAccess

# Register your models here.
admin.site.register(TutorialAccess)
admin.site.register(Payment)
admin.site.register(TutorWallet)
