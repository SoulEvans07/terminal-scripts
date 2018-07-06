class BasicCommunication:
    connected = 0
    conn_type = 'Dummy'

    def __init__(self):
        connected = 0

    def send(self, string):
        return 0

    def receive(self, timeout=0):
        return ''

    def close(self):
        return 0

    def get_conn_info(self):
        return 'Dummy connection'
