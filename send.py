from notifiers import get_notifier
from info import token,id

def bet_siska(data):
    telegram = get_notifier('telegram')
    info = "\n".join([i for i in data])
    telegram.notify(token=token,chat_id = id,message = info)
    print("MSG HAS BEEN SENT")


def bet_period(data):
    telegram = get_notifier('telegram')
    info = "\n".join([i for i in data])
    telegram.notify(token=token,chat_id = id,message = info)
    print("MSG HAS BEEN SENT")



def errormsg():
    telegram = get_notifier('telegram')
    message = "RESTART HOCKEY SCRIPT!!!"
    telegram.notify(token=token,chat_id = id,message = message)
    print("INTERRUPTED")


def make_mistake():
    telegram = get_notifier('telegram')
    message = "MISTAKE HOCKEY!!!"
    telegram.notify(token=token,chat_id = id,message = message)
    print("MISTAKE - HOCKEY")


def startmsg():
    telegram = get_notifier('telegram')
    message = "HOCKEY SCRIPT IS RUNNING!"
    telegram.notify(token=token,chat_id = id,message = message)
    print(message)

