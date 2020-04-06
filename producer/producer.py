from confluent_kafka import avro
from confluent_kafka.avro import AvroProducer

import os
import requests
import time

from admin_api import CustomAdmin
from order_faker import OrderFaker

"""
This is an example with fake data intended to demonstrate basic
functionality of the pipeline.

You must set the TOPIC_NAME environment variable.

This image does not have a default TOPIC_NAME set, to avoid
potentially confusing errors.

This version of the producer serializes the key with avro.

For a version that serializes the key as a string, see the repo.
"""

BROKER = os.environ['BROKER']
SCHEMA_REGISTRY_URL = os.environ['SCHEMA_REGISTRY_URL']
TOPIC_NAME = os.environ['TOPIC_NAME']

def delivery_report(err, msg):
    """
    Called once for each message produced to indicate delivery result.
    Triggered by poll() or flush().
    """
    if err is not None:
        print('Message delivery failed: {}'.format(err))
    else:
        print('Message delivered to {} [{}]'.
              format(msg.topic(), msg.partition()))


# Create a topic if it doesn't exist yet
admin = CustomAdmin(BROKER)
if not admin.topic_exists(TOPIC_NAME):
    admin.create_topics([TOPIC_NAME])

# Define schemas
# NOTE: the key is included in the value as a hacky workaround
# because ksql does not recognize avro-encoded keys and
# AvroProducer does not allow a different encoding for keys at the
# time of this writing.
# See https://github.com/confluentinc/confluent-kafka-python/issues/428
value_schema = avro.loads("""
    {
        "namespace": "orders",
        "name": "value",
        "type": "record",
        "fields": [
            {"name": "order_id", "type": "int", "doc": "order_id"},
            {"name": "customer_id", "type": "int", "doc": "customer id"},
            {"name": "seller_id", "type": "int", "doc": "seller id"},
            {"name": "billing_id", "type": "int", "doc": "id of the billing method for the customer"},
            {"name": "shipping_address_id", "type": "int", "doc": "id of the shipping address for the customer"},
            {"name": "product_id", "type": "int", "doc": "product id"},
            {"name": "quantity", "type": "int", "doc": "how much of the product the customer wants"},
            {"name": "price_in_cents", "type": "int", "doc": "price in cents. US currency"}
        ]
    }
""")

key_schema = avro.loads("""
{
   "namespace": "orders",
   "name": "key",
   "type": "record",
   "fields" : [
     {
       "name" : "order_id",
       "type" : "int"
     }
   ]
}
""")

# Initialize producer
avroProducer = AvroProducer(
    {
        'bootstrap.servers': BROKER,
        'on_delivery': delivery_report,
        'schema.registry.url': SCHEMA_REGISTRY_URL
    },
    default_key_schema=key_schema,
    default_value_schema=value_schema
)

# Initialize key and faker
# Key will be implemented, to simulate each order having a unique id
order_id = 1

faker = OrderFaker({
    'customer_id': {'min': 1, 'max': 1000},
    'seller_id': {'min': 1, 'max': 1000},
    'billing_id': {'min': 1, 'max': 5},
    'shipping_address_id': {'min': 1, 'max': 10},
    'product_id': {'min': 1, 'max': 10000},
    'quantity': {'min': 1, 'max': 5},
    'price_in_cents': {'min': 100, 'max': 10000}
})


# Produce events simulating bus movements, forever
count = 1
while True:
    key = {'order_id': order_id}
    value = faker.order() 
    value['order_id'] = order_id 
    avroProducer.produce(topic=TOPIC_NAME, value=value, key=key)
    print("EVENT COUNT: {} key: {} value: {}".format(count, key, value))
    # Polls the producer for events and calls the corresponding callbacks
    # (if registered)
    #
    # `timeout` refers to the maximum time to block waiting for events
    #
    # Since produce() is an asynchronous API this poll() call will most
    # likely not serve the delivery callback for the last produce()d message.
    avroProducer.poll(timeout=0)
    time.sleep(0.3)

    order_id += 1
    count += 1
# Cleanup step: wait for all messages to be delivered before exiting.
avroProducer.flush()
