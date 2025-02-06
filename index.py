from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
from chatgpt import ChatGPT
import parse_ht
import os

line_bot_api = LineBotApi(os.getenv("LINE_CHANNEL_ACCESS_TOKEN"))
line_handler = WebhookHandler(os.getenv("LINE_CHANNEL_SECRET"))
working_status = os.getenv("DEFALUT_TALKING", default="true").lower() == "true"

app = Flask(__name__)
chatgpt = ChatGPT()


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
    working_status = True

    if event.message.type != "text":
        return

    if event.message.text.lower() in [
            "schedule", "hololive", "jp", "japanese", "holo"
    ]:

        reply_msg = parse_ht.getSchedule()
        line_bot_api.reply_message(event.reply_token,
                                   TextSendMessage(text=reply_msg))
        return

    elif event.message.text.lower() in ["en", "english"]:

        reply_msg = parse_ht.getSchedule(
            "https://schedule.hololive.tv/simple/english")
        line_bot_api.reply_message(event.reply_token,
                                   TextSendMessage(text=reply_msg))
        return

    elif event.message.text.lower() in ["匯率", "rate", "exchange"]:

        reply_msg = parse_ht.exchange_rate()
        line_bot_api.reply_message(event.reply_token,
                                   TextSendMessage(text=reply_msg))
        return

    elif event.message.text.lower() in ["help", "幫助"]:
        reply_msg = "search hololive schedule use \'schedule\' or \'hololive\'\n" + \
                    "search english schedule use \'en\' or \'english\'\n" + \
                    "search exchange rate use \'匯率\' or \'rate\' or \'exchange\'\n"
        line_bot_api.reply_message(event.reply_token,
                                   TextSendMessage(text=reply_msg))
        return

    elif working_status:
        chatgpt.add_msg(f"Human:{event.message.text}?\n")
        reply_msg = chatgpt.get_response().replace("AI:", "", 1)
        chatgpt.add_msg(f"AI:{reply_msg}\n")
        line_bot_api.reply_message(event.reply_token,
                                   TextSendMessage(text=reply_msg))


if __name__ == "__main__":
    app.run()
