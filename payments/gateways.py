from core.models import StoreSettings


class BaseGateway:
    """Base class that all payment gateways must implement."""
    def initialize(self, order, callback_url):
        raise NotImplementedError

    def verify(self, reference):
        raise NotImplementedError


class PaystackGateway(BaseGateway):
    def initialize(self, order, callback_url):
        from .services import initialize_paystack_transaction
        return initialize_paystack_transaction(order, callback_url)

    def verify(self, reference):
        from .services import verify_paystack_transaction
        return verify_paystack_transaction(reference)


class FlutterwaveGateway(BaseGateway):
    def initialize(self, order, callback_url):
        return {
            'status': False,
            'message': 'Flutterwave integration is coming soon.',
        }

    def verify(self, reference):
        return {
            'status': False,
            'message': 'Flutterwave verification is coming soon.',
        }


class MonnifyGateway(BaseGateway):
    def initialize(self, order, callback_url):
        return {
            'status': False,
            'message': 'Monnify integration is coming soon.',
        }

    def verify(self, reference):
        return {
            'status': False,
            'message': 'Monnify verification is coming soon.',
        }


class SquadGateway(BaseGateway):
    def initialize(self, order, callback_url):
        return {
            'status': False,
            'message': 'Squad integration is coming soon.',
        }

    def verify(self, reference):
        return {
            'status': False,
            'message': 'Squad verification is coming soon.',
        }


def get_active_gateway():
    """
    Factory that returns the correct gateway instance based on StoreSettings.
    Returns None if no online payment is enabled or keys are missing.
    """
    store = StoreSettings.load()

    if not store.is_payment_enabled:
        return None

    gateway_map = {
        'paystack': PaystackGateway,
        'flutterwave': FlutterwaveGateway,
        'monnify': MonnifyGateway,
        'squad': SquadGateway,
    }

    gateway_class = gateway_map.get(store.active_gateway)
    if not gateway_class:
        return None

    return gateway_class()
