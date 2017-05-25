import sys
import time
from pprint import pprint
import telepot
from telepot.loop import MessageLoop
from telepot.namedtuple import LabeledPrice, ShippingOption
from telepot.delegate import (
    per_invoice_payload, pave_event_space, create_open,
    per_message, call)

"""
Run it by:
$ python3.5 script.py <bot-token> <payment-provider-token>
"""

class OrderProcessor(telepot.helper.InvoiceHandler):
    def __init__(self, *args, **kwargs):
        super(OrderProcessor, self).__init__(*args, **kwargs)

    def on_shipping_query(self, msg):
        query_id, from_id, invoice_payload = telepot.glance(msg, flavor='shipping_query')

        print('Shipping query:')
        pprint(msg)

        bot.answerShippingQuery(
            query_id, True,
            shipping_options=[
                ShippingOption(id='fedex', title='FedEx', prices=[
                    LabeledPrice(label='Local', amount=345),
                    LabeledPrice(label='International', amount=2345)]),
                ShippingOption(id='dhl', title='DHL', prices=[
                    LabeledPrice(label='Local', amount=342),
                    LabeledPrice(label='International', amount=1234)])])

    def on_pre_checkout_query(self, msg):
        query_id, from_id, invoice_payload = telepot.glance(msg, flavor='pre_checkout_query')

        print('Pre-Checkout query:')
        pprint(msg)

        bot.answerPreCheckoutQuery(query_id, True)

    def on_chat_message(self, msg):
        content_type, chat_type, chat_id = telepot.glance(msg)

        if content_type == 'successful_payment':
            print('Successful payment RECEIVED!!!')
            pprint(msg)
        else:
            print('Chat message:')
            pprint(msg)

def send_invoice(seed_tuple):
    msg = seed_tuple[1]

    content_type, chat_type, chat_id = telepot.glance(msg)

    if content_type == 'text':
        sent = bot.sendInvoice(
                   chat_id, "Nick's Hand Cream", "Keep a man's hand like a woman's",
                   payload='a-string-identifying-related-payment-messages-tuvwxyz',
                   provider_token=PAYMENT_PROVIDER_TOKEN,
                   start_parameter='abc',
                   currency='HKD', prices=[
                       LabeledPrice(label='One Case', amount=987),
                       LabeledPrice(label='Package', amount=12)],
                   need_shipping_address=True, is_flexible=True)  # required for shipping query

        print('Invoice sent:')
        pprint(sent)


TOKEN = sys.argv[1]
PAYMENT_PROVIDER_TOKEN = sys.argv[2]

bot = telepot.DelegatorBot(TOKEN, [
    (per_message(flavors=['chat']), call(send_invoice)),
    pave_event_space()(
        per_invoice_payload(), create_open, OrderProcessor, timeout=30,
    )
])

MessageLoop(bot).run_as_thread()

while 1:
    time.sleep(10)
