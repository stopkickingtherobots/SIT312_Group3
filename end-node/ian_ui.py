from multiprocessing import Process, Queue # Used for multiprocessing
import time

def get_distress():

    # Place code here to poll distress button/ attach interupt logic.
    # Return type may vary, str type used for demonstration

    msg = 'SOS - Save our souls'

    return msg


def display_msg(msg):

    # Place code here to display strings on the screen. 
    # Input will be a single line str value (unsure of inline \n, \t etc)
    # Print method used for demonstration

    print('UI: {0:}'.format(msg))


def main(ui_queue_out, ui_queue_in):

    print('Begin ui')

    distress_msg = get_distress()

    ui_queue_out.put(distress_msg)

    response = ui_queue_in.get(2)

    display_msg(response)

    print('End ui')