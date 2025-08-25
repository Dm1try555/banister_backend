import os
import logging
import stripe
from decimal import Decimal
from django.conf import settings

logger = logging.getLogger(__name__)

class StripeService:
    """Centralized Stripe service for payment operations"""
    
    def __init__(self):
        self._initialize_stripe()
    
    def _initialize_stripe(self):
        """Initialize Stripe API"""
        try:
            # Use test key if production key is not specified
            stripe.api_key = os.getenv('STRIPE_SECRET_KEY')
            
            if not stripe.api_key:
                # Fallback to test key
                stripe.api_key = os.getenv('STRIPE_TEST_SECRET_KEY')
                if not stripe.api_key:
                    # Fallback to test key
                    raise ValueError("Stripe API key not found")
            
            # Check mode (test/production)
            if stripe.api_key.startswith('sk_test_'):
                self.test_mode = True
                logger.info("Stripe initialized in TEST mode")
            elif stripe.api_key.startswith('sk_live_'):
                self.test_mode = False
                logger.info("Stripe initialized in PRODUCTION mode")
            else:
                logger.warning("Unknown Stripe API key format")
                self.test_mode = True
                
        except Exception as e:
            logger.error(f"Stripe initialization error: {str(e)}")
            raise
    
    def create_payment_intent(self, amount, currency='usd', metadata=None):
        """Create payment intent to receive funds"""
        try:
            # Ensure amount is Decimal or float
            if not isinstance(amount, (Decimal, float, int)):
                raise ValueError("Amount must be a number")
            
            payment_intent = stripe.PaymentIntent.create(
                amount=int(amount * 100),  # Stripe requires cents
                currency=currency,
                metadata=metadata or {}
            )
            logger.info(f"Payment intent created: {payment_intent.id} for ${amount}")
            return True, payment_intent
        except stripe.error.StripeError as e:
            logger.error(f"Stripe payment intent error: {str(e)}")
            return False, f"Payment intent creation error: {str(e)}"
        except Exception as e:
            logger.error(f"Unexpected error in create_payment_intent: {str(e)}")
            return False, f"Unexpected error: {str(e)}"
    
    def transfer_to_account(self, amount, destination_account, currency='usd'):
        """Transfer funds to connected account"""
        try:
            # Ensure amount is Decimal or float
            if not isinstance(amount, (Decimal, float, int)):
                raise ValueError("Amount must be a number")
            
            transfer_data = {
                'amount': int(amount * 100),  # Stripe requires cents
                'currency': currency,
                'destination': destination_account
            }
            
            transfer = stripe.Transfer.create(**transfer_data)
            logger.info(f"Transfer created: {transfer.id} for ${amount} to {destination_account}")
            return True, transfer
        except stripe.error.StripeError as e:
            logger.error(f"Stripe transfer error: {str(e)}")
            return False, f"Transfer error: {str(e)}"
        except Exception as e:
            logger.error(f"Unexpected error in transfer_to_account: {str(e)}")
            return False, f"Unexpected error: {str(e)}"
    
    def confirm_payment(self, payment_intent_id):
        """Confirm payment status"""
        try:
            intent = stripe.PaymentIntent.retrieve(payment_intent_id)
            logger.info(f"Payment intent retrieved: {intent.id} - status: {intent.status}")
            return intent.status == 'succeeded', intent
        except stripe.error.StripeError as e:
            logger.error(f"Stripe payment confirmation error: {str(e)}")
            return False, f"Payment confirmation error: {str(e)}"
        except Exception as e:
            logger.error(f"Unexpected error in confirm_payment: {str(e)}")
            return False, f"Unexpected error: {str(e)}"


stripe_service = StripeService()