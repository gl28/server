import os
import socket
import signal
import errno
from http_request import HTTPRequest
from http_response import HTTPResponse

HOST = 'localhost'
PORT = 8000

class Server:
    def __init__(self, host, port):
        self.host = host
        self.port = port

    def handle_request(self, connection):
        request_data = connection.recv(4096)
        print(request_data.decode())
        
        request = HTTPRequest(request_data)
        response = HTTPResponse(request.method, request.uri, request.body)

        connection.sendall(response.data)


    def sigchld_handler(self, signal_num, stack_frame):
        while True:
            # loop will catch all SIGCHLD signals in case many come at once
            
            try:
                # -1 means wait for any child process
                # WNOHANG means return immediately if no child has exited
                pid, status = os.waitpid(-1, os.WNOHANG)
            
            except OSError as e:
                err_code, message = e.args
                if err_code == errno.ECHILD:
                    # ECHILD error means there are no more child processes
                    # handler is finished, so we can return
                    return
                else:
                    raise

    def start_server(self):

        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # allows socket to re-use same address
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind((self.host,self.port))
        server_socket.listen(5) # set the queue size

        # calls sigchld_handler when the child process ends to avoid zombie processes
        signal.signal(signal.SIGCHLD, self.sigchld_handler)

        print(f'Serving HTTP on {self.host} at port {self.port}')
        
        while True:
            client_socket, client_address = server_socket.accept()

            pid = os.fork()
            if pid == 0:
                # child process
                # server socket is being handled by parent process
                server_socket.close()
                self.handle_request(client_socket)
                client_socket.close()

                # exit child process
                os._exit(0)

            else:
                #parent process
                # need to close duplicate connections
                client_socket.close()

if __name__ == '__main__':
    server = Server(HOST, PORT)
    server.start_server()