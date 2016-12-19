
import requests
import random
from faker import Faker

fake = Faker()

post_data = {'email': fake.email(),
             'zip': fake.postalcode(),
             'city': fake.city(),
             'phone': fake.phone_number(),
             'firstName': fake.first_name_female(),
             'lastName': fake.last_name_female(),
             'address': fake.street_address(),
             'city': fake.city(),
             'country': "US",'state':'CA'}
url1 = 'http://127.0.0.1:5000/api/lead/'
url2 = 'http://127.0.0.1:5000/api/lead/purchase/'

resp = requests.post(url1,post_data)
print resp.content

post_data2 = {
    'name':'Alexa 1',
    'description':'descriptiondescription description description',
    'amount':999.99,
    'recurring':True,
    'tos':'main_sale',
    'stripeToken':'adsq234213e21312312e12321'}