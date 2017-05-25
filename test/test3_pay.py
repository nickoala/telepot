import sys
import time
from pprint import pprint
import telepot
from telepot.namedtuple import (
    LabeledPrice, Invoice, PreCheckoutQuery, ShippingQuery, ShippingOption,
    SuccessfulPayment)
from telepot.loop import MessageLoop

"""
This script tests the payment process:
1. Send an invoice
2. Receive a shipping query, respond with answerShippingQuery()
3. Receive a pre-checkout query, respond with answerPreCheckoutQuery()
4. Receive a successful payment

Run it by:
$ python3.5 script.py <bot-token> <payment-provider-token>
"""

def on_chat_message(msg):
    content_type, chat_type, chat_id = telepot.glance(msg)
    print(content_type, chat_type, chat_id)

    if content_type != 'successful_payment':
        sent = bot.sendInvoice(
                   chat_id, "Nick's Hand Cream", "Keep a man's hand like a woman's",
                   payload='a-string-identifying-related-payment-messages-tuvwxyz',
                   provider_token=PAYMENT_PROVIDER_TOKEN,
                   start_parameter='abc',
                   currency='HKD', prices=[
                       LabeledPrice(label='One Case', amount=987),
                       LabeledPrice(label='Package', amount=12)],
                   need_shipping_address=True, is_flexible=True)  # required for shipping query
        # 'Pay' button appears automatically

        pprint(sent)
        print(Invoice(**sent['invoice']))

    else:
        print('Successful payment RECEIVED!!!')
        pprint(msg)
        print(SuccessfulPayment(**msg['successful_payment']))

def on_shipping_query(msg):
    query_id, from_id, invoice_payload = telepot.glance(msg, flavor='shipping_query')

    print('Shipping query:')
    print(query_id, from_id, invoice_payload)
    pprint(msg)
    print(ShippingQuery(**msg))

    bot.answerShippingQuery(
        query_id, True,
        shipping_options=[
            ShippingOption(id='fedex', title='FedEx', prices=[
                LabeledPrice(label='Local', amount=345),
                LabeledPrice(label='International', amount=2345)]),
            ShippingOption(id='dhl', title='DHL', prices=[
                LabeledPrice(label='Local', amount=342),
                LabeledPrice(label='International', amount=1234)])])

def on_pre_checkout_query(msg):
    query_id, from_id, invoice_payload, currency, total_amount = telepot.glance(msg, flavor='pre_checkout_query', long=True)

    print('Pre-Checkout query:')
    print(query_id, from_id, invoice_payload, currency, total_amount)
    pprint(msg)
    print(PreCheckoutQuery(**msg))

    bot.answerPreCheckoutQuery(query_id, True)

TOKEN = sys.argv[1]
PAYMENT_PROVIDER_TOKEN = sys.argv[2]

bot = telepot.Bot(TOKEN)
MessageLoop(bot, {'chat': on_chat_message,
                  'shipping_query': on_shipping_query,
                  'pre_checkout_query': on_pre_checkout_query}).run_as_thread()

while 1:
    time.sleep(10)
