from django.contrib import admin
from .models import Transaction,Debit
# Register your models here.
admin.site.register(Transaction)
admin.site.register(Debit)