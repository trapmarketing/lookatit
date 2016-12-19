from flask import request, render_template
import stripe

from application import app, db
from models import Customer, Transaction


def create_stripe_customer(cid, email, stripe_token):
    """

    :rtype : object
    """
    customer_info = db.query(Customer).filter({"id": cid})
    user = Customer.query.filter_by(id=cid).first()
    if user:
        stripe_customer = stripe.Customer.create(email=email, source=stripe_token)
        if stripe_customer.id:
            return stripe_customer.id
        else:
            return None
    else:
        return None

def subscribe_customer(verbose_name,amount,customer_id,interval="month",currency="usd"):
    unique_id = verbose_name.replace(" ","_")
    unique_id = unique_id.replace("'","")
    unique_id = unique_id.lower()
    current_plans = stripe.Plan.list()
    subscribe_id = ''
    for plan in current_plans.data:
        if plan.id==unique_id:
            subscribe_id = plan.id
    stripe.Plan.create(name=verbose_name,id=unique_id,interval=interval, currency=currency, amount=amount)
    subscribe_id = unique_id

    return stripe.Subscription.create( customer=customer_id.id,plan=subscribe_id)




def stripe_charge(cid, charge_amount, charge_descripton):
    insufficient_message = 'Your transaction was declined due to insufficient. Please try a different card.'
    issuer_not_available = 'Please wait a few minutes and try this order again. If you still have trouble with your transaction' \
                           ', please try a different card or calling your bank.'
    generic_decline = 'Please try a different card or call your bank to find out why out why this transaction was declined.'

    customer_info = db.query(Customer).filter({"id": cid})
    if customer_info:
        if customer_info.stripe_customer_id:
            try:
                charge = stripe.Charge.create(
                    customer=customer_info.stripe_customer_id,
                    amount=charge_amount,
                    currency='usd',
                    description=charge_descripton)
                if charge.outcome.network_status == "approved_by_network":
                    return True, charge.receipt_number
                elif charge.outcome.network_status == 'issuer_not_available':
                    return False, issuer_not_available
                elif charge.outcome.network_status == "insufficient_funds":
                    return False, insufficient_message
                else:
                    return False,
            except stripe.CardError as e:
                return False, e
        else:
            e = "User Does Not Have Payment Method on File"
            return False, e
    else:
        e = "Customer not found"
        return False, e


