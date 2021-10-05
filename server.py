import os
import socket
import signal
import errno
import mimetypes

HOST = ''
PORT = 8000

class Server:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.supported_methods = ['GET', 'PUT']
        self.headers = {
            'Content-Type': 'text/html',
        }
        self.status_codes = {
            200: 'OK',
            404: 'Not Found',
            501: 'Not Implemented',
        }
    
    def parse_request(self, request):

        # '\r\n\r\n' separates request and headers from message body 
        chunks = request.decode().split('\r\n\r\n')

        request_and_headers = chunks[0]
        
        body = ''
        if len(chunks) > 1:
            body = chunks[1]

        request_parts = request_and_headers.split('\r\n')
        
        request_line = request_parts[0].split(' ')
        method = request_line[0]
        uri = '/'

        if len(request_line) > 1:
            # request may not include URI if client requests home page
            # in which case request_line[1] would be the HTTP version
            uri = request_line[1]

        if uri[-1] == '/':
            # if URI ends in slash assume it's looking for index.html
            uri += 'index.html'
            
        headers = {}

        for i in range(1, len(request_parts)):
            # everything after index 0 will be a header
            header_parts = request_parts[i].split(':')
            header_key = header_parts[0]
            header_value = header_parts[1].lstrip()
            headers[header_key] = header_value


        return {'method': method, 'uri': uri, 'headers': headers, 'body': body}

    def handle_GET(self, uri):
        file_name = 'site/' + uri.lstrip('/')

        if os.path.exists(file_name):
            with open(file_name, 'rb') as file:
                file_contents = file.read()

            content_type, encoding = mimetypes.guess_type(file_name)

            if not content_type:
                content_type = 'text/html'

            response = b'HTTP/1.1 200 OK \r\n'
            response += b'Content-Type: '
            response += content_type.encode()
            response += b'\r\n\r\n'
            response += file_contents
        else:
            response = b'HTTP/1.1 404 Not Found \r\n'
            response += b'Content-Type: text/html'
            response += b'\r\n\r\n'
            response += b'<h1>404 Not Found</h1>'
            response += b'<p>The page you requested could not be found.'

        return response


    def handle_501(self, method):
        response = f'HTTP/1.1 501 {self.status_codes[501]} \r\n'
        response += 'Content-Type: ' + self.headers['Content-Type']
        response += '\r\n\r\n'
        response += '<h1>501 Not Implemented</h1>'
        response += f'<p>The method {method} has not been implemented yet.</p>'

        return response.encode()


    def handle_request(self, connection):
        request = connection.recv(1024)
        
        parsed = self.parse_request(request)
        method = parsed['method']
        uri = parsed['uri']
        headers = parsed['headers']
        body = parsed['body']

        print(f'Method: {method}. URI: {uri}.')
        print(headers)
        print(body)
        
        response = ''

        if method == 'GET':
            response = self.handle_GET(uri)
        else:
            response = self.handle_501(method)

        connection.sendall(response)

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

        print(f'Access on port {self.port}')
        # print(f'PPID: {os.getppid()}')
        
        while True:
            client_socket, client_address = server_socket.accept()

            pid = os.fork()
            if pid == 0: # child process
                # server socket is being handled by parent process
                server_socket.close()
                self.handle_request(client_socket)
                client_socket.close()

                # exit child process
                os._exit(0)

            else: #parent process
                # need to close duplicate connections
                client_socket.close()

if __name__ == '__main__':
    server = Server(HOST, PORT)
    server.start_server()