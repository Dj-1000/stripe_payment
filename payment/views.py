from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import CardInformationSerializer
from rest_framework import status
import stripe
import os
from product.models import Product
from .models import PaymentMethod, StripeCustomer, Transaction
from utils.exceptions.custom_exceptions import ValidationError
import json



class PaymentView(APIView):
    serializer_class = CardInformationSerializer
    def post(self, request):
        serl = self.serializer_class(data=request.data)
        response = {}
        if serl.is_valid():
            payload = serl.data
            card_details = {
                "number": payload['card_number'],
                "exp_month": payload['expiry_month'],
                "exp_year": payload['expiry_year'],
                "cvc": payload['cvc']
            },
            data_dict=dict()
            prod = payload['product']
            data_dict['card_details'] = card_details
            data_dict['product'] = payload['product']
            if payload['card_holder_name'] is not None:
                data_dict['card_holder_name'] = payload['card_holder_name']
            if payload['email'] is not None:
                data_dict['email'] = payload['email']
            if payload['address'] is not None:
                data_dict['address'] = payload['address']
            if payload['city'] is not None:
                data_dict['city'] = payload['city']
            if payload['state'] is not None:
                data_dict['state'] = payload['state']
            if payload['country'] is not None:
                data_dict['country'] = payload['country']
            if payload['zip_code'] is not None:
                data_dict['zip_code'] = payload['zip_code']
            if payload['currency'] is not None:
                data_dict['currency'] = payload['currency']
            if payload['quantity'] is not None:
                data_dict['amount'] = float(prod['price']) * int(payload['quantity'])
            
            '''Extracting the customer from db if exists else create a new one'''
            stripe_customer = self.get_or_create_customer(data_dict)
            data_dict['customer_id'] = stripe_customer.id

            '''Extracting the payment method if exists else create a new one'''
            payment_method = self.get_or_create_payment_method(data_dict)
            data_dict['payment_method'] = payment_method.payment_method_id

            response = self.stripe_card_payment(data_dict=data_dict)
        else:
            response = {
                'status' : status.HTTP_502_BAD_GATEWAY,
                'errorMessage' : serl.errors
            }
                
        return Response(response, status=status.HTTP_200_OK)

    def stripe_card_payment(self, data_dict):
        try:
            payment_method = PaymentMethod.objects.filter(payment_method_id = data_dict['payment_method']).first()
            stripe_customer = StripeCustomer.objects.filter(stripe_customer_id = data_dict['customer_id']).first()
            payment_intent = self.get_or_create_payment_intent(data_dict)
            payment_intent_modified = stripe.PaymentIntent.modify(
                payment_intent['id']
            )
            try:
                payment_confirm = stripe.PaymentIntent.confirm(
                    payment_intent['id']
                )
                payment_intent_modified = stripe.PaymentIntent.retrieve(payment_intent['id'])
            except:
                payment_intent_modified = stripe.PaymentIntent.retrieve(payment_intent['id'])
                payment_confirm = {
                    "stripe_payment_error": "Failed",
                    "code": payment_intent_modified['last_payment_error']['code'],
                    "message": payment_intent_modified['last_payment_error']['message'],
                    'status': "Failed"
                }
            if payment_intent_modified and payment_intent_modified['status'] == 'succeeded':
                Transaction.objects.create(
                    amount=payment_intent_modified['amount'],
                    currency=payment_intent_modified['currency'],
                    status=payment_intent_modified['status'],
                    payment_method=payment_method,
                    org_payment=stripe_customer,
                    transaction_id=payment_intent['id'],
                    description="Payment successful"
                )
                response = {
                    'message': "Card Payment Success",
                    'status': status.HTTP_200_OK,
                    "payment_intent": payment_intent_modified,
                    "payment_confirm": payment_confirm,
                    "payment_data" : data_dict
                }
            else:
                Transaction.objects.create(
                    amount=payment_intent_modified['amount'],
                    currency=payment_intent_modified['currency'],
                    status=payment_intent_modified['status'],
                    payment_method=payment_method,
                    transaction_id=payment_intent['id'],
                    description=payment_confirm['message'],
                    failure_reason= 'Card not accepted by stripe '
                )
                response = {
                    'message': "Card Payment Failed",
                    'status': status.HTTP_400_BAD_REQUEST,
                    "card_details": data_dict['card_details'],
                    "payment_intent": payment_intent_modified,
                    "payment_confirm": payment_confirm
                }
            return response
        except Exception as e:
                response = {
                    'error': "Your card info is incorrect",
                    'status': status.HTTP_400_BAD_REQUEST,
                    "payment_intent": {'id': None},
                    "payment_confirm": {'status': "Failed"}
                }
                return response


    def get_or_create_customer(self,data_dict):
        customer = StripeCustomer.objects.filter(email = data_dict['email']).first()
        if customer:
            stripe_customer = stripe.Customer.retrieve(customer.stripe_customer_id)
        else:
            customer = stripe.Customer.create(
                name=data_dict['card_holder_name'],
                email=data_dict['email'],
                address={
                    'country': data_dict['country'],
                    'state':data_dict['state'],
                    'city':data_dict['city'], 
                    'postal_code':data_dict['zip_code']                   
                },
            )
            if customer:
                stripe_customer = StripeCustomer.objects.create(
                    stripe_customer_id = customer['id'],
                    name = customer['name'],
                    email = customer['email']
                )
            else:
                raise ValidationError("Stripe error while creating customer")
        
        return stripe_customer

    def get_or_create_payment_method(self,data_dict):
        payment_method = PaymentMethod.objects.filter(customer_id = data_dict['customer_id']).first()
        if not payment_method:
            try:
                stripe_paymnt_mthd = stripe.PaymentMethod.create(
                    type='card',
                    card={'token': "tok_visa"},
                    billing_details={
                        "name": data_dict['card_holder_name'],
                        "address": {
                            "line1": data_dict['address'],
                            "city": data_dict['city'],
                            "state": data_dict['state'],
                            "country": data_dict['country']
                        },
                        "email": data_dict['email']
                   }
                )
                stripe.PaymentMethod.attach(
                  stripe_paymnt_mthd.id,
                  customer=data_dict['customer_id'],
                )
                if stripe_paymnt_mthd:
                    payment_method = PaymentMethod.objects.create(
                        payment_method_id = stripe_paymnt_mthd['id'],
                        customer_id = data_dict['customer_id'],
                        type = 'card',
                        address = data_dict['address'],
                        city = data_dict['city'],
                        state = data_dict['state'],
                        country_code = data_dict['country'],
                        zip_code = data_dict['zip_code']
                    )

            except Exception as e:
                    raise ValidationError("Error creating payment method")
        return payment_method

        
    def get_or_create_payment_intent(self,payload):
        customer = stripe.Customer.retrieve(payload['customer_id'])
        try:
            payment_intent = stripe.PaymentIntent.create(
                        amount=int(payload['amount']) *100, 
                        currency=payload['currency'],
                        customer=customer.id, 
                        payment_method=payload['payment_method'],
                        # confirm=True,
                        # off_sesion = True
                    ),
            return payment_intent
        except Exception as e:
            raise ValidationError("Error creating payment intent")