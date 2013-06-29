Title: WebSockets with Circus and Nginx
Date: 2013-06-30 12:37
Slug: websockets-circus-nginx
Category: Python, Circus, Nginx, Websockets
Author: Marconi Moreto
Summary: Serving websockets with Circus and the new Nginx websocket proxying.

Although we will be talking about WebSockets in general, It'll be concentrated on a shim, [Socket.IO](http://socket.io/) in this case. Socket.IO is a shim that enables you to use WebSocket if your browser supports it or fallback to other mechanism like long-polling, flash, etc. if not.

This is the first of probably a series of posts on how one might serve websockets with Python. As far as I know, there's not a mature solution yet for websockets in the Python world but there are two ways I've tried which works effectively.

### Gevent-SocketIO

This one is a promising project, lots of examples from different frameworks and I've contributed [one of them](https://github.com/abourget/gevent-socketio/commit/af20de07f18267d01430d19374d1e1928cd627f8) myself. [gevent-socketio](https://gevent-socketio.readthedocs.org/en/latest/) is a server implementation of the [Socket.IO protocol](https://github.com/LearnBoost/socket.io-protocol).

### Node

And then there's [Node](http://nodejs.org/), the Javascript framework from where Socket.IO was originally built for. For devs with JS stack, its an easy deicision although there are other variants of a similar shim in the JS world too.

For this post we will concentrate on gevent-socketio, and then Node soon. In the gevent-socketio github repo, there's an example project called [simple_pyramid_chat](https://github.com/abourget/gevent-socketio/tree/master/examples/simple_pyramid_chat) we will be using it instead of building our own from ground up.

First thing is first, lets install all the required dependencies:

    mkvirtualenv websocket_demo
    pip install -U pyramid gevent-socketio circus chaussette

Next there's one thing we need to modify in the simple_pyramid_chat project, in the `serve.py`, move the line outside of the `if` condition so it looks like:

    ...
    
    app = get_app('development.ini')
    
    if __name__ == '__main__':
        ...

The reason is that, that `app` is the Pyramid app we want to be served by Chaussette and since its inside a condition that will only be run if the file is ran as stand-alone, Chaussette won't be able to find it if the module is to be imported which is what we're going to use.

And then we need a `circus.ini` file which you should be familiar if you've been following my other posts:

    [circus]
    check_delay = 5
    endpoint = tcp://127.0.0.1:5555
    pubsub_endpoint = tcp://127.0.0.1:5556
    
    [watcher:socketio]
    cmd = chaussette --fd $(circus.sockets.socketio) --backend socketio serve.app
    singleton = True
    use_sockets = True
    copy_env = True
    copy_path = True
    
    [env:socketio]
    PYTHONPATH = /var/www/simple_pyramid_chat
    
    [socket:socketio]
    host = 127.0.0.1
    port = 6543

Everything should be familiar except that this time we're using `socketio` as our backend for Chaussette and we have a new configuration `singleton` which just means this watcher will have at most 1 process.

We can run this now by running `circusd /var/www/simple_pyramid_chat/circus.ini` and we'll see that the app is being served and the chat is working (You need to open two different browsers if you're testing by yourself).

Then we need to tell Nginx to forward all incoming request to Circus, as of Nginx 1.3.13, Nginx now supports [proxying WebSocket](http://nginx.org/en/docs/http/websocket.html) requests. And here's the Nginx config that we're going to use:

    map $http_upgrade $connection_upgrade {
        default upgrade;
        ''      close;
    }
    
    server {
        listen 80 default;
        server_name _;
    
        location / {
            proxy_pass         http://127.0.0.1:6543;
            proxy_redirect     off;
            proxy_buffering    off;
            proxy_http_version 1.1;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection $connection_upgrade;
        }
    }

Here we're just the http version for proxying to 1.1 which is required for the Nginx WebSocket proxying to work and we're passing some headers to the proxied server. The reason for the headers is that when the client requests for an upgrade, its using a [Hop-by-hop](http://tools.ietf.org/html/rfc2616#section-13.5.1) headers which just means the headers doesn't reach the proxied server only to Nginx so we manually forward them. And the mapping above is just a nice little trick wherein we only set the `Connection` header to `upgrade` if the Upgrade field from the request received from client is present which will be once Socket.IO from client sends a WebSockte handshake.

Now lets restart nginx `sudo service nginx restart` and we should be able to access the chat app at `http://localhost`, note that the port is not specified as it is implied for http.

That's it for now, next post is using Node with Redis as a message bus between your Node and Python app.