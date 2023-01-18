#!/usr/bin/env python
# coding: utf-8

# In[10]:





# In[ ]:


import os
import openai
from pyChatGPT import ChatGPT
from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
from pyChatGPT import ChatGPT


session_token = "eyJhbGciOiJkaXIiLCJlbmMiOiJBMjU2R0NNIn0..E8xi7o3cCmGRjVJy.u0jpbi8IGHMOkxC8gTqlmRM8_eVboGAYrikQ1t7_UbjgWjZnjK4aBXIYov04DUuqegVVn5o7xbPU0JuUwVDYOyYkL3DXJr5WC2KmdUHOd_SeYUosCadmgfST0azKUIICt-_VD28mHrPav6kMJLm9i6smWiPmSTOmGIdiBn_yGC8v55XPOwIO_sDXa3J_fkphFjsXl6VeJkCDz7XKPVYvITaszg1J8JfdFyyBAP1Q-sSB1CbE4uINyt9q2w6H2-4AFx1gR5-bRukphHhCKUEYIgtMrAPbibBAagNoA8qAsFpenlc3D8sj_hPykB22fLNUvEeTPJlXpS1HwM_s67dp35zWMeVbdQD0eBHUpNQcrkZEpY0MhN9t5ig_3cWF4Hl6DBkgj6qltXuHf_zLXqarPRgMgbQvHNv_5lOfpSrsW05u5jTFxx6ediPW2qSi0-FKTPufvnqBq9lnE8wsytd0Y6mWw8qQRGDD54drOiYO2qUcG0jAckrdMmKthURnGV3l9jmjDuIoIriRt6LQkvUsdGOuVTxk2dn6pN8QhbwDCpAP4nXDzL49xzXJJepL3RLl9hZHE8Z5aT0u2XRvIEolJatIJoyEoNVojHo3NvhUt8F8PMWAhnjC8QlC9opiS3ow7zBCS8APeUC4w_20VJZw2ZdbZxeIHjnMEb3bw7YljbANPLdJuTM1XnxjPam8sTOs6YzIEotnNMCIdkDZjtSMsXHChhtBhwktTEIYVOLyXtWNZm1zaMrlWAcnnbhoX0f5Uym9puCsEuWKaOM0xBoVUFFwdtE1pzCKXGUJZehL3A3r4kHdOj7147yKyQIMFju7sfIIRpcDWouXR8j1StPPeX0Hm8jxEqYSwHPKJYErZbCrgCdfprmpnTTdsKDNX6qb8FEUCnZO6rviUjQuAcclyWZqY2edcDMDA2qz-8gwFWam9n0SMhZVCbjIXY-u-b1-NdMN5vpUEOd3xB05bOkepRgROJTs_nP8eV3wpu9LwAuUpw0YUWfDix0m5yZUemK2ytgU135bbKPUDiOzLNSJvBXC7HZmvRA5971CrrRUJF5NNIyg48b2Mkqa4BYckmBO3VuVn6QaajLVFOfYhDp8azwWc2sBxpYL7hBBBwLvyoao05M--kIUNm3VZsmTHocI3MH_x3e5NwKOvNbtkC084wbFcpHmWVeQt9pKz9lzbuqiU5vNqkK_9rSSYp5M1k8XCsT9fs7Ka5Zs8zKFBE4obhYwDGlW7mPd_nwNK8Ys4HeFrlYWsCt616ofJ4F_ZWULMQsZJRsMGYKPhgtXIx47X6UTdy_nglYhdJL7ThawZn1o09nKkcOzumZ7KA1uqP4f5PpWNY2gUeISTPOWFAk7iM7ZLWqi_bOUvpY6L1KACTpBMK101ogV4EXEcocYMDbdFz-vswhesJo-4JlfptmN05he1Rtzz-stWOkwqiR4ZKu8pATrQp1rftoNXf-mmukjyfblklLzdbf6tQUtWwD1vBnDQHUeiHlCAgB09tL7R1vpCxkxRtgIeUkzg6KyqciJ0-K3C3E5CBJU5YBgHJZ5Ab9VSytUoNOD4NVBvUOdPNZMCed6BhgGUEy6zPdeIJVHZrbNON5-YYlbPlSWh7Vg0ANQ7-b4tZWtVp-j3qD-2Uk_Vw61-Dalpbng3jCPB7oA110JZsMytKRq_A9u2BYZxTkcMrEZPmJtJhjm8QbrS5EjPs35IBhOB4YVxh5Lw3vcFI2za0uh5WcI900n1cfRJgwg5_mjKJnXOc1kTXlaoaaeMwOgiydxyz9474-kzVjsh1NHGmF4xmDMKUDzKZwjKJnBssnRzf0dma4WW7uVgOmH363paznWTxRZsvE4wXRNrujUB6SPYBVMsBevAl2pyf6GDcP0-zkkeqhmdAlYwJq7DZXI9LNcj3FeqVYg8DD_6Ik-ajTDi0gZW8phX-V387aDfY9llBmJMeMSVRDC1p2Y1ZALj0ENyeJLQtl5IO1wTOCuu0zy9l2wKCJ9hiqrfy5tHrWYwPKLCzoD6bx56ZfdycfJ2a0ekRMi66BKUVPPsRsJ8-qniIdYSdBOe_xax3Sa6z1l6kAmZkOT97QGs94CQtkiiFLtmK82AEyPlEBzyOYAAcNs115jj3thQtiPV3nmXbdK11X80_PcLY-oD_sq2jRZ_kspZrI1QE36pI7zEz06mwH6MPQJykiUCSwvdj4ylOXl85JrG-Phxl7-0kX-_ShDwpuIS38_YXod30IeMM5TXSX42mki5wkq.L_ihH449ZQXoX-AdUZpS-w"

line_bot_api = LineBotApi(os.getenv("LINE_CHANNEL_ACCESS_TOKEN"))
line_handler = WebhookHandler(os.getenv("LINE_CHANNEL_SECRET"))
working_status = os.getenv("DEFALUT_TALKING", default = "true").lower() == "true"

app = Flask(__name__)
chatgpt = ChatGPT(session_token)

# domain root
@app.route('/')
def home():
    return 'Hello, World!'

@app.route("/webhook", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']
    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)
    # handle webhook body
    try:
        line_handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'


@line_handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    global working_status
    if event.message.type != "text":
        return

    if event.message.text == "說話":
        working_status = True
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text="我可以說話囉，歡迎來跟我互動 ^_^ "))
        return

    if event.message.text == "閉嘴":
        working_status = False
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text="好的，我乖乖閉嘴 > <，如果想要我繼續說話，請跟我說 「說話」 > <"))
        return

    if working_status:
        response = chatgpt.send_message(f"HUMAN:{event.message.text}?\n")
        #chatgpt.add_msg(f"HUMAN:{event.message.text}?\n")
        reply_msg = response['message']
        #chatgpt.add_msg(f"AI:{reply_msg}\n")
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=reply_msg))


if __name__ == "__main__":
    app.run()

