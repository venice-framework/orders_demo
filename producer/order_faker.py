import random

class OrderFaker:
    """
    Can be used to generate order data.

    Sample usage:
    faker = OrderFaker({
        'customer_id': {'min': 1, 'max': 1000},
        'seller_id': {'min': 1, 'max': 1000},
        'billing_id': {'min': 1, 'max': 5},
        'shipping_address_id': {'min': 1, 'max': 10},
        'product_id': {'min': 1, 'max': 10000},
        'quantity': {'min': 1, 'max': 5},
        'price_in_cents': {'min': 100, 'min': 10000}
    })

    faker.order()

    # returns a dictionary like:
    # {
    #     'customer_id': 5,
    #     'seller_id': 980,
    #     'billing_id': 3, 
    #     'shipping_address_id': 2,
    #     'product_id': 5324, 
    #     'quantity': 2, 
    #     'price_in_cents': 4000 
    # }

    })
    """
    def __init__(self, fields: dict):
        self.fields = fields 

    def order(self):
        order = {}
        for key, value in self.fields.items():
            if not (isinstance(key, str) and isinstance(value, dict)):
                print("Error for key: {}. Key must be a str and value must be a dict".format(key))
                continue
            if not ('min' in value and 'max' in value):
                print('Error for key: {}. Both min and max must be defined'.format(key))
                continue
            if not (isinstance(value["min"], int) and isinstance(value["max"], int)):
                print('Error for key: {}. Both min and max must be integers.'.format(key))
                continue
            # returns a random integer N such that min <= N <= max
            order[key] = random.randint(value["min"], value["max"]) 
        return order
