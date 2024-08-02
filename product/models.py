from django.db import models
CURRENCY = [
    ('inr','INR'),
    ('usd','USD')  # Add more currencies as per your requirement
]

class Product(models.Model):
    name = models.CharField(max_length=200)
    desc = models.TextField(blank=True)
    thumbnail = models.ImageField(upload_to='thumbnails/', blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(choices=CURRENCY,max_length=100,default=CURRENCY[0])
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("-created_at",)

    def __str__(self):
        return self.name