import stripe
import os
from django.conf import settings
from django.utils import timezone

class StripeService:
    """Centralized Stripe service for all payment operations"""
    
    def __init__(self):
        self._initialize_stripe()
    
    def _initialize_stripe(self):
        """Initialize Stripe API"""
        try:
            stripe.api_key = os.getenv('STRIPE_SECRET_KEY')
            if not stripe.api_key:
                print("Stripe API key not found")
        except Exception as e:
            print(f"Stripe initialization error: {str(e)}")
    
    def create_payment_intent(self, amount, currency='usd', metadata=None):
        """Create payment intent to receive funds"""
        try:
            intent_data = {
                'amount': int(amount * 100),
                'currency': currency,
                'automatic_payment_methods': {'enabled': True}
            }
            
            if metadata:
                intent_data['metadata'] = metadata
            
            intent = stripe.PaymentIntent.create(**intent_data)
            return True, intent
        except Exception as e:
            return False, f"Payment intent creation error: {str(e)}"
    
    def transfer_to_account(self, amount, destination_account, currency='usd', metadata=None):
        """Transfer funds to connected account"""
        try:
            transfer_data = {
                'amount': int(amount * 100),
                'currency': currency,
                'destination': destination_account
            }
            
            if metadata:
                transfer_data['metadata'] = metadata
            
            transfer = stripe.Transfer.create(**transfer_data)
            return True, transfer
        except Exception as e:
            return False, f"Transfer error: {str(e)}"
    
    def confirm_payment(self, payment_intent_id):
        """Confirm payment status"""
        try:
            intent = stripe.PaymentIntent.retrieve(payment_intent_id)
            return intent.status == 'succeeded', intent
        except Exception as e:
            return False, f"Payment confirmation error: {str(e)}"
    
    def create_customer(self, email, name=None, metadata=None):
        """Create Stripe customer"""
        try:
            customer_data = {'email': email}
            
            if name:
                customer_data['name'] = name
            if metadata:
                customer_data['metadata'] = metadata
            
            customer = stripe.Customer.create(**customer_data)
            return True, customer
        except Exception as e:
            return False, f"Customer creation error: {str(e)}"
    
    def create_account(self, email, country='US', type='express'):
        """Create connected account for service providers"""
        try:
            account = stripe.Account.create(
                type=type,
                country=country,
                email=email
            )
            return True, account
        except Exception as e:
            return False, f"Account creation error: {str(e)}"

stripe_service = StripeService()