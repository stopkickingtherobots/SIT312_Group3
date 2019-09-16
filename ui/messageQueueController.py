from multiprocessing import Process, Queue

def get_distress():
    with open("distress.txt") as file:
        data = file.read()
        if data:
            return True
    return False


def display_msg(message):
    with open("messages.txt", "r+") as file:
        data = file.read()
        data = message+"\n"+data
        file.seek(0, 0)
        file.write(data)

def main(ui_queue_out, ui_queue_in):
    msg = ui_queue_in.get()
    if msg != None:
        display_msg(msg)

    if get_distress():
        ui_queue_out.put("Distress beacon active")