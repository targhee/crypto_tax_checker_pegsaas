import stripe
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from djstripe.models import Subscription
from djstripe.utils import CURRENCY_SIGILS
from djstripe.settings import djstripe_settings

from stripe.api_resources.billing_portal.session import Session as BillingPortalSession
from stripe.api_resources.checkout import Session as CheckoutSession

from .exceptions import SubscriptionConfigError
from apps.users.models import CustomUser
from apps.web.meta import absolute_url


def get_friendly_currency_amount(plan):
    # modified from djstripe's version to only include sigil or currency, but not both
    if plan.amount is None:
        return 'Unknown'
    currency = plan.currency.upper()
    sigil = CURRENCY_SIGILS.get(currency, "")
    if sigil:
        return "{sigil}{amount:.2f}".format(sigil=sigil, amount=plan.amount)
    else:
        return "{amount:.2f} {currency}".format(amount=plan.amount, currency=currency)


def get_subscription_urls(subscription_holder):
    # get URLs for subscription helpers
    url_bases = [
        'subscription_details',
        'create_stripe_portal_session',
        'subscription_demo',
        'subscription_gated_page',
        # checkout urls
        'create_checkout_session',
        'checkout_success',
        'checkout_canceled',
        # elements urls
        'create_customer',
        'subscription_success',
    ]

    def _construct_url(base):
        return reverse(f'subscriptions:{base}')

    return {
        url_base: _construct_url(url_base) for url_base in url_bases
    }


def get_payment_metadata_from_request(request):
    return {
        'user_id': request.user.id,
        'user_email': request.user.email,
    }


def get_stripe_module():
    """Gets the Stripe API module, with the API key properly populated"""
    stripe.api_key = djstripe_settings.STRIPE_SECRET_KEY
    return stripe


def create_stripe_checkout_session(subscription_holder: CustomUser, stripe_price_id: str, customer_email: str) -> CheckoutSession:
    stripe = get_stripe_module()

    subscription_urls = get_subscription_urls(subscription_holder)
    success_url = absolute_url(subscription_urls['checkout_success'])
    cancel_url = absolute_url(subscription_urls['checkout_canceled'])

    checkout_session = stripe.checkout.Session.create(
        success_url=success_url + '?session_id={CHECKOUT_SESSION_ID}',
        cancel_url=cancel_url,
        customer_email=customer_email,
        payment_method_types=['card'],
        mode='subscription',
        client_reference_id=subscription_holder.id,
        line_items=[{
            'price': stripe_price_id,
            # For metered billing, do not pass quantity
            'quantity': subscription_holder.get_quantity(),
        }],
        allow_promotion_codes=True,
    )
    return checkout_session


def create_stripe_portal_session(subscription_holder: CustomUser) -> BillingPortalSession:
    stripe = get_stripe_module()
    if not subscription_holder.subscription or not subscription_holder.subscription.customer:
        raise SubscriptionConfigError(_("Whoops, we couldn't find a subscription associated with your account!"))

    subscription_urls = get_subscription_urls(subscription_holder)
    portal_session = stripe.billing_portal.Session.create(
        customer=subscription_holder.subscription.customer.id,
        return_url=absolute_url(subscription_urls['subscription_details']),
    )
    return portal_session


def provision_subscription(subscription_holder: CustomUser, subscription_id: str) -> Subscription:
    stripe = get_stripe_module()
    subscription = stripe.Subscription.retrieve(subscription_id)
    djstripe_subscription = Subscription.sync_from_stripe_data(subscription)
    subscription_holder.subscription = djstripe_subscription
    subscription_holder.save()
    return djstripe_subscription
