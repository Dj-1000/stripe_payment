from django.contrib import admin
from .models import PaymentMethod,StripeCustomer,Transaction
admin.site.register(PaymentMethod)
admin.site.register(StripeCustomer)
admin.site.register(Transaction)

