from flask import request, jsonify, session,render_template
from application import app, logger, cache

from application import app
from application.models import *
from forms import *
from models import Customer
import stripeview


@app.before_first_request
def before_first_request():
    logger.info("-------------------- initializing everything ---------------------")
    db.create_all()


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@app.errorhandler(500)
def server_error(e):
    return render_template('500.html'), 500


def add_lead(request):
    logger.info("Entering add lead function")

    email_address = request.form['email']
    fname = request.form['first_name']
    lname = request.form['last_name']
    billing_address = request.form['billing_address']
    city = request.form['city']
    state = request.form['state']
    country = request.form['country']
    zip_code = request.form['zip_code']
    logger.info("Entering Reqests part")
    customer = Customer(fname=fname, lname=lname, billing_address=billing_address, city=city, state=state,
                        country=country, zip_code=zip_code)
    logger.info(customer.id)
    db.session.add(customer)
    db.session.commit()
    return customer.id


@app.route('/api/leads/',methods=['GET', 'POST'])
def create_lead():
    logger.info(request)

    logger.info(request.form)
    lead_form = BaseApiLeadForm(request.form)
    if lead_form.validate():
        lead_id = add_lead(request)
        logger.info("lead generated"+str(lead_id))
        session['customer_id']  = int(lead_id)

        message = {'result': "succcess"}

    else:
        logger.info(lead_form.errors)
        message = {'result': 'failurd'}
    return jsonify(message)


@app.route('/leads/leads/purchase/',methods=['GET', 'POST'])
def charge_customer():
    if 'customer_id' in session:
        customer = db.Query(Customer).where(id=session['customer_id']).one()
        if request.form['tos'] == 'main_sale':
            orderform = InitialOrderForm(request.form)
            if orderform.validate():
                stripe_customer_id = stripeview.create_stripe_customer(customer.id, customer.email,
                                                                       request.form['stripeToken'])
                if stripe_customer_id:
                    customer.stripe_customer_id = stripe_customer_id
                    db.session.add(customer)
                    db.session.commit()

        orderform = OrderForm(request.form)
        if orderform.validate():
            if request.form['recurring']:
                subscription_id = stripeview.subscribe_customer(request.form['name'], request.form['amount'],
                                                                customer.stripe_customer_id)
                result = True
                message = "Subscription placeholder"
            else:
                result, message = stripeview.stripe_charge(customer.stripe_customer_id, request.form['amount'],
                                                           request.form['description'])
            if result:  # message = charge.receipt_number, if true
                transaction = Transaction()
                transaction.stripe_transaction = message
                transaction.amount = request.form['amount']
                transaction.recurring = request.form['recurring']
                transaction.sale_type = request.form['tos']
                transaction.purchaser = customer
                db.session.add(transaction)
                db.session.commit()
                return jsonify({"result": 'success'})
            else:
                return jsonify({'result': message})

        else:
            return jsonify({'result': 'failed', 'errors': orderform.errors})




'''
@app.route('/api/purchase/'):
def one_page_purchase():
    lead_form = BaseApiLeadForm(request.form)
    if lead_form.validate():
        session['id']=add_lead()
        customer = db.Query(Customer).where(id=session['id']).one()
    else:
        return {'form '}
        if request.form['tos']=='main_sale':
            orderform = InitialOrderForm(request.form)
            if orderform.validate():
                stripe_customer_id = stripeview.create_stripe_customer(customer.id,customer.email,request.form['stripeToken'])
                if stripe_customer_id:
                    customer.stripe_customer_id = stripe_customer_id
                    db.session.add(customer)
                    db.session.commit()

        else:
            orderform = OrderForm(request.form)
            if orderform.validate():
                result = True
            else:
                json_dict = {'result':request.form}
                return jsonify(json_dict)
        if request.form['recurring']:
                subscription_id = stripeview.subscribe_customer(request.form['name'],request.form['amount'],customer.stripe_customer_id)
                result = True
                print(subscription_id)

            else:
                result,message = stripeview.stripe_charge(customer.stripe_customer_id, request.form['amount'], request.form['description'])
                if result: #message = charge.receipt_number, if true
                    transaction = Transaction()
                    transaction.stripe_transaction = message
                    transaction.amount = request.form['amount']
                    transaction.recurring =request.form['recurring']
                    transaction.sale_type = request.form['tos']
                    transaction.customer_id = customer.id
                    db.session.add(transaction)
                    db.session.commit()

@app.route('/api/upsell1'):
def create_lead():
    pass

@app.route('/api/upsell2'):
def create_lead():
    pass




@app.route('/index')
@app.route('/index/<int:page>')
'''
