import mimetypes
import os
import re

class HTTPResponse:
    def __init__(self, method, uri, body):
        if method == 'GET':
            self.data = self.get(uri)
        elif method == 'POST':
            self.data = self.post(uri, body)
        else:
            self.data = self.not_implemented()

    def not_found(self):
        response = b'HTTP/1.1 404 Not Found \r\n'
        response += b'Content-Type: text/html'
        response += b'\r\n\r\n'
        response += b'<h1>404 Not Found</h1>'
        response += b'<p>The page you requested could not be found.'

        return response

    def read_file(self, uri):
        file_name = 'site/' + uri.lstrip('/')

        if os.path.exists(file_name):
            with open(file_name, 'rb') as file:
                file_contents = file.read()

            content_type = mimetypes.guess_type(file_name)[0]

            if not content_type:
                content_type = 'text/html'

            return file_contents, content_type
        else:
            return False

    def get(self, uri):
        file = self.read_file(uri)

        if file:
            file_contents, content_type = file
            response = b'HTTP/1.1 200 OK \r\n'
            response += b'Content-Type: '
            response += content_type.encode()
            response += b'\r\n\r\n'
            response += file_contents
        else:
            response = self.not_found()

        return response

    def post(self, uri, body):
        file = self.read_file(uri)

        if file:
            file_contents, content_type = file
            file_contents = file_contents.decode()

            for field, value in body.items():
                # display POST values in page
                match = '{{' + field + '}}'
                file_contents = re.sub(match, value, file_contents)

            response = b'HTTP/1.1 200 OK \r\n'
            response += b'Content-Type: '
            response += content_type.encode()
            response += b'\r\n\r\n'
            response += file_contents.encode()

        else:
            response = self.not_found()

        return response


    def not_implemented(self, method):
        response = 'HTTP/1.1 501 Not Implemented\r\n'
        response += 'Content-Type: text/html'
        response += '\r\n\r\n'
        response += '<h1>501 Not Implemented</h1>'
        response += f'<p>The method {method} has not been implemented yet.</p>'

        return response.encode()