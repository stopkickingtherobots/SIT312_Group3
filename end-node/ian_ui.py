from multiprocessing import Process, Queue # Used for multiprocessing
import time
import queue
import datetime


def get_distress():
    with open("distress.txt") as file:
        data = file.read()
        if data:
            return True
    return False


def display_msg(message):
    msg_arr = message.split(',')
    result = 'BASE: ' + msg_arr[2] + " at " + str(datetime.datetime.utcfromtimestamp(int(float(msg_arr[1]))))
    with open("messages.txt", "r+") as file:
        data = file.read()
        print('Message.txt: {0:}'.format(result))
        data = result+"\n"+data
        file.seek(0, 0)
        file.write(data)


def main(ui_queue_in, ui_queue_out):

    print('Begin ui')
    
    while(True):

        if get_distress():
            print('Putting Distress on queue')
            ui_queue_out.put("Distress beacon active")
            time.sleep(5)
        try:
            msg = ui_queue_in.get(block=False)
            if msg != None:
                print('Got message from message queue: {0:}'.format(msg))
                display_msg(msg)
        except queue.Empty:
            pass

    print('End ui')
