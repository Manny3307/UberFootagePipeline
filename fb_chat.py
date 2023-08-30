'''import fbchat
from getpass import getpass
ua = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.111 Safari/537.36"
client = fbchat.Client('manmeetarora@gmail.com', 'pikolo@486', user_agent=ua)
print(client)

from messengerapi import SendApi
send_api = SendApi('EAAYx7ZCODuwkBAAzDhJrDWoYURE74qRvgGO3cSucDciVxo81JsYTbbU0FOWUUHZCKC3SpbGOfdZAfbs20UeBZBJLS8hzvQODApLm0eeysZCEvjt0IiFGI18YR48gXa6seFaYthNU1c5l35XCYUCbVKtlvAcYOKMjiiQ9i0ZCNwEmZAj1oSgtiCzZCoKVvJp0ZABok6q7hYbkpfktII5fZBJaZAvi3C8daKxGRF9WZB2yWNowGT1hEFyi7rSY')
resp = send_api.send_text_message('sent from my pc', 'manmeetarora@gmail.com')
print(resp)
'''

#curl -i -X POST "https://graph.facebook.com/v16.0/PAGE-ID/messages?recipient={'id':'5255979991240460'}&messaging_type=RESPONSE&message={'text':'hello,world'}&access_token='EAAM0tPROVmEBACZBJ7fRxGSDmDYVvhgekhXTf2ZB0V7O3EmGpFCeGs89GnYgXABxEn7VNB3tG0lwVDngZBRM5hPZAvQIAUo1xnIbZBOdppnjwHm7igyYlxWAMuIwKVdTIJex4hZBWZBKK97rqDw3bNOo1MrSfdUT6IaXwOHMF1Wn1ZAIyFNCM2ijSnDXuukZAFNEgBxKZCCYgdApZAUJiWVfKZA7m4ydr1DkHZBX5V2vZAITPiJyd2x1aMqpHc'
import facebook as fb
access_token = 'EAAM0tPROVmEBACZBJ7fRxGSDmDYVvhgekhXTf2ZB0V7O3EmGpFCeGs89GnYgXABxEn7VNB3tG0lwVDngZBRM5hPZAvQIAUo1xnIbZBOdppnjwHm7igyYlxWAMuIwKVdTIJex4hZBWZBKK97rqDw3bNOo1MrSfdUT6IaXwOHMF1Wn1ZAIyFNCM2ijSnDXuukZAFNEgBxKZCCYgdApZAUJiWVfKZA7m4ydr1DkHZBX5V2vZAITPiJyd2x1aMqpHc'

temp = fb.GraphAPI(access_token)
temp.put_object('me','message', message='Hey')