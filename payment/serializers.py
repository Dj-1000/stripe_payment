from rest_framework import serializers
from utils.payment.utils import *
from utils.exceptions.custom_exceptions import ValidationError
from product.models import Product
from product.serializers import ProductSerializer
import pycountry
from currency_codes import get_currency_by_code, CurrencyNotFoundError

CURRENCY = [
    ('inr', 'INR'),
    ('usd', 'USD')  # Add more currencies as per your requirement
]
PAYMENT_METHODS = [
    'pm_card_visa',
    'pm_card_visa_debit',
    ##further payment methods
]


class CardInformationSerializer(serializers.Serializer):
    """ Serializer for Card Information """
    product = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all())
    quantity = serializers.IntegerField(required=True)
    state = serializers.CharField(max_length = 50,required=True)
    address = serializers.CharField(max_length = 200,required=True)
    city = serializers.CharField(max_length = 50,required=True)
    zip_code = serializers.CharField(max_length=6,required=True)
    card_number = serializers.CharField(max_length=150, required=True)
    card_holder_name = serializers.CharField(max_length=50, required=True)
    email = serializers.EmailField(required=True)
    currency = serializers.CharField(
        max_length=50, 
        required=True,
        validators = [check_currency_code]
    )
    country = serializers.CharField(
        max_length = 50,
        required=True,
        validators = [check_country_code]
    )
    expiry_month = serializers.CharField(
        max_length=150,
        required=True,
        validators=[check_expiry_month],
    )
    expiry_year = serializers.CharField(
        max_length=150,
        required=True,
        validators=[check_expiry_year],
    )
    cvc = serializers.CharField(
        max_length=150,
        required=True,
        validators=[check_cvc],
    )

    def validate(self, attrs):
        currency = attrs.get('currency').lower()
        product = attrs.get('product')
        country = attrs.get('country')

        try:
            currency_code = get_currency_by_code(currency)
            country = pycountry.countries.lookup(country)
            attrs['country']=country.alpha_2
            attrs['currency'] = currency_code.code  # Ensure the normalized currency code is saved

        except LookupError:
            raise ValidationError(f"Country name '{country}' is not valid or not recognized.")
        
        except CurrencyNotFoundError:
            raise ValidationError("Non-existent currencycode have been used")
        
        if currency != product.currency:
            raise ValidationError("Currency does not match with product currency.")
        attrs['currency'] = currency  # Ensure the normalized currency is saved



        return attrs

    def to_representation(self, attrs):
        representation = super().to_representation(attrs)
        product = attrs.get('product')
        product_serializer = ProductSerializer(product)
        representation['product'] = product_serializer.data
        return representation
