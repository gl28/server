import re

class HTTPRequest:
    def __init__(self, request):
        self.parse_request(request)
    
    def decode(self, encoded):
        # replaces any percent-encoded characters with ASCII
        
        def replace(match):
            # ASCII code is specified by hex value
            hex = match[1:]
            dec = int(hex, 16)
            return chr(dec)

        decoded = encoded.replace('+', ' ')
        decoded = re.sub('%..', lambda m: replace(m.group()), decoded)
    
        return decoded

    def parse_request(self, request):
        """
        HTTP request format:

        Request       = Request-Line
                        *(( general-header
                         | request-header
                         | entity-header ) CRLF)
                        CRLF
                        [ message-body ]  

        Request-Line = Method SP Request-URI SP HTTP-Version CRLF
        """

        chunks = request.decode().split('\r\n\r\n')
        request_and_headers = chunks[0]
        request_parts = request_and_headers.split('\r\n')
        request_line = request_parts[0].split(' ')
        method = request_line[0]
        uri = '/'

        if len(request_line) > 1:
            # request may not include URI if client requests home page
            # in which case request_line[1] would be the HTTP version
            uri = self.decode(request_line[1])

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

        # request body is formatted as 'field1=value1&field2=value2'
        if len(chunks) > 1:
            body_raw = chunks[1]
        else:
            body_raw = ''

        body_parts = body_raw.split('&')
        body = {}

        for part in body_parts:
            pairs = part.split('=')
            if len(pairs) > 1:
                field = self.decode(pairs[0])
                value = self.decode(pairs[1])

                body[field] = value
        
        self.method = method
        self.uri = uri
        self.header = headers
        self.body = body
