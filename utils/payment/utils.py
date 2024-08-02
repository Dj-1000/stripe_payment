import datetime
from utils.exceptions.custom_exceptions import ValidationError
import pycountry
from currency_codes import get_currency_by_code, CurrencyNotFoundError

def check_expiry_month(value):
    if not 1 <= int(value) <= 12:
        raise ValidationError("Invalid expiry month.")


def check_expiry_year(value):
    today = datetime.datetime.now()
    if not int(value) >= today.year:
        raise ValidationError("Invalid expiry year.")


def check_cvc(value):
    if not 3 <= len(value) <= 4:
        raise ValidationError("Invalid cvc number.")


def check_payment_method(value):
    payment_method = value.lower()
    if payment_method not in ["card"]:
        raise ValidationError("Invalid payment_method.")

def check_country_code(value):
    try:
        country = pycountry.countries.lookup(value)
        return country.alpha_2
    except LookupError:
        raise ValidationError(f"Country name '{value}' is not valid or not recognized.")
    

def check_currency_code(value):
    try:
        currency_code = get_currency_by_code(value)
        return currency_code 
    except CurrencyNotFoundError:
        raise ValidationError("Non-existent code have been used")