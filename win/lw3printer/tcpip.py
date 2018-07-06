import socket
import select
import communication


class TcpIp(communication.BasicCommunication):
    s = 0
    connected = 0
    conn_type = 'Tcp'

    def __init__(self, dest_addr='192.168.2.120', dest_port=10001, connectTimeout=10, utf8=False):
        self.needsPolling = True
        self.utf8_receive = utf8
        self.connectTimeout = connectTimeout
        self.dest_addr = dest_addr
        self.dest_port = dest_port
        self.s = socket.create_connection((self.dest_addr, self.dest_port), self.connectTimeout)
        self.connected = 1
        self.s.setblocking(0)

    def send(self, s):
        if (self.connected == 1):
            self.s.sendall(bytes(s, 'ascii'))

    def receive(self, timeout=1):
        if (self.connected == 0):
            return ''
        ready_to_read, ready_to_write, in_error = select.select([self.s], [], [], timeout)
        if (len(ready_to_read) == 0):
            return ''
        rx = self.s.recv(1024)
        if self.utf8_receive:
            return str(rx, 'utf-8')
        else:
            return str(rx, 'ascii', 'ignore')

    def close(self, shutdown=False):
        self.connected = 0
        if shutdown:
            self.s.shutdown(socket.SHUT_RDWR)
        self.s.close()
        return self.connected

    def flush(self):
        """Dummy function, to maintain interface compatibility with Rs232"""
        pass

    def get_conn_info(self):
        return '%s:%s' % (self.dest_addr, str(self.dest_port))
