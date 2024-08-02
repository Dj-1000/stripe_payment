from django.db import models
from accounts.models import AppUser

class StripeCustomer(models.Model):
    stripe_customer_id = models.CharField(max_length=100)
    name = models.CharField(max_length=50)
    email = models.EmailField(max_length=100)

class PaymentMethod(models.Model):
    payment_method_id = models.CharField(max_length=100)
    customer_id = models.CharField(max_length=100,null = True,blank=True)
    type = models.CharField(max_length=50)
    address = models.CharField(max_length=200)
    city = models.CharField(max_length=50)
    state = models.CharField(max_length=50)
    country_code = models.CharField(max_length=10)
    zip_code = models.CharField(max_length=10)

# model for method of all transaction
class Transaction(models.Model):
    transaction_id=models.CharField(max_length=50,null=True,blank=True)
    payment_method = models.ForeignKey(PaymentMethod, on_delete=models.CASCADE)
    customer = models.ForeignKey(StripeCustomer, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3)  # Currency code (e.g., USD, EUR,INR)
    status = models.CharField(max_length=20)  # pending, succeeded, failed
    timestamp = models.DateTimeField(auto_now_add=True)
    description = models.TextField(blank=True, null=True)
    failure_reason = models.TextField(blank=True, null=True)


