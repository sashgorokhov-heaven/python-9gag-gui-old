import threading


def threaded(function):
    def wrapper(*args):
        threading.Thread(target=function, args=args).start()

    return wrapper