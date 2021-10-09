import mimetypes
import os
import re

class HTTPResponse:
    def __init__(self, method, uri, body):
        self.redirect_paths = dict()
        self.forbidden_paths = set()
        self.load_config()

        if method == 'GET':
            self.data = self.get(uri)
        elif method == 'POST':
            self.data = self.post(uri, body)
        else:
            self.data = self.not_implemented()

    def load_config(self):
        # loads forbidden file paths and redirects
        with open('config.txt', 'r') as file:
            config_data = file.read()
        config_lines = config_data.split('\n')
        
        for line in config_lines:
            if line[0] == '#':
                # if line begins with a hash, treat it as a comment
                continue
            config_parts = line.split(' ')
            if config_parts[0] == '301':
                self.redirect_paths[config_parts[1]] = config_parts[2]
            elif config_parts[0] == '403':
                self.forbidden_paths.add(config_parts[1])

    def get(self, uri):
        file = self.read_file(uri)

        if file == 'Not Found':
            return self.not_found()
        elif file == 'Forbidden':
            return self.forbidden(uri)
        elif file == 'Redirect':
            return self.redirect(uri)
        elif file:
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

    def read_file(self, uri):
        relative_path = uri.lstrip('/')
        absolute_path = 'site/' + relative_path

        if relative_path in self.forbidden_paths:
            return 'Forbidden'
        elif relative_path in self.redirect_paths:
            return 'Redirect'
        elif os.path.exists(absolute_path):
            with open(absolute_path, 'rb') as file:
                file_contents = file.read()

            content_type = mimetypes.guess_type(absolute_path)[0]

            if not content_type:
                content_type = 'text/html'

            return file_contents, content_type
        else:
            return 'Not Found'

    
    def redirect(self, uri):
        file_path = uri.lstrip('/')
        response = 'HTTP/1.1 301 Moved Permanently\r\n'
        response += f'Location: {self.redirect_paths[file_path]}\r\n\r\n'

        return response.encode()

    def forbidden(self, uri):
        file_path = uri.lstrip('/')
        response = 'HTTP/1.1 403 Forbidden\r\n'
        response += 'Content-Type: text/html'
        response += '\r\n\r\n'
        response += '<h1>403 Forbidden</h1>'
        response += f'<p>You are forbidden from accessing the following page: <code>{file_path}</code>.</p>'

        return response.encode()

    def not_implemented(self, method):
        response = 'HTTP/1.1 501 Not Implemented\r\n'
        response += 'Content-Type: text/html'
        response += '\r\n\r\n'
        response += '<h1>501 Not Implemented</h1>'
        response += f'<p>The method {method} has not been implemented yet.</p>'

        return response.encode()

    def not_found(self):
        response = b'HTTP/1.1 404 Not Found \r\n'
        response += b'Content-Type: text/html'
        response += b'\r\n\r\n'
        response += b'<h1>404 Not Found</h1>'
        response += b'<p>The page you requested could not be found.'

        return response