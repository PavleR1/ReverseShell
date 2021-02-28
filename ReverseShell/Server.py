import socket


class Server:
    host = '0.0.0.0'
    port = 9998
    buffer_size = 1024
    c_socket, c_address = '', ''

    def __init__(self):
        self.socket_creation()
        self.socket_binding()
        self.accepting_connection()
        self.run()

    def socket_creation(self):
        print('Creating socket')
        try:
            self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM, socket.IPPROTO_TCP)
        except socket.error as message:
            print('Error : ' + str(message))

    def socket_binding(self):
        print('Binding socket')
        try:
            self.s.bind((self.host, self.port))
            self.s.listen(5)
        except socket.error as message:
            print('Error : ' + str(message))
            self.socket_binding()

    def accepting_connection(self):
        print('Connection establishing')
        self.c_socket, self.c_address = self.s.accept()
        print(f'Client address: {self.c_address[0]}:{self.c_address[1]}')

    def sending_commands(self, message):
        succ = self.c_socket.send(f'{message}'.encode())
        return succ

    def get_result(self):
        rec_bits = self.c_socket.recv(self.buffer_size)
        rec_msg = rec_bits.decode('utf8')
        print(f'{rec_msg}')

    def run(self):
        while True:
            self.get_result()
            command = input('-->')
            self.sending_commands(command)
            if command.lower() == 'exit':
                self.c_socket.close()
                self.s.close()
                break


if __name__ == '__main__':
    p = Server()
