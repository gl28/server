# Concurrent HTTP Sockets Server

I created this simple HTTP server to get a better understanding of the low-level sockets library. I wrote it only using sockets and not any of the standard Python libraries for creating a web server. I also implemented basic concurrency by having each incoming request be handled by a new process.

To try the server, clone the repo and run:
```
python3 server.py
```

By default it will run on localhost at port 8000. You can change these values in server.py.

(Due to the use of a fork() system call, the server is not compatible with Windows.)

## Features

The server is capable of handling GET and POST requests. For any other request, it will return a 501 Not Implemented error.

The server can serve static files, including HTML, Javascript, and CSS. If a request is made for a page which does not exist, the server will respond with a 404 Not Found error.

There is also an optional config file, which allows you to specify redirects (301 Moved Permanently) and forbidden pages (403 Forbidden).
