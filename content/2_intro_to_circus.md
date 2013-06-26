Title: Introduction to Circus
Date: 2013-06-26 08:13
Slug: introduction-to-circus
Category: Python
Author: Marconi Moreto
Summary: A quick introduction to Circus: The process and socket manager

Whilst the most common way in deploying Python WSGI apps is still via [Gunicorn](http://gunicorn.org/), now adays I prefer using [Circus](http://circus.readthedocs.org) + [Chaussette](http://chaussette.readthedocs.org). The main difference is that, unlike before where you have Gunicorn serving your app and manages your worker processes, Circus on the other hand does all the process and socket management so Chaussette, your WSGI server, does only one thing and that's to serve your app.

You can even run something like Redis inside Circus and let Circus manage it. This should feel familiar if you've used something like [Supervisor](http://supervisord.org/) before as it has an overlapping functionality with Circus.

Alright, enough talk and lets see some code. To start, we're going to server a simple WSGI app in Circus:

    :::python
    def app(environ, start_response):
	    """Simplest possible application object"""
	    data = 'Hello, World!\n'
	    status = '200 OK'
	    response_headers = [
	        ('Content-type', 'text/plain'),
	        ('Content-Length', str(len(data)))
	    ]
	    start_response(status, response_headers)
	    return iter([data])

Our app is very simple, it just outputs the string `Hello World`. Save it as `app.py` and next, our `circus.ini` file:

    [circus]
    check_delay = 5
    endpoint = tcp://127.0.0.1:5555
    pubsub_endpoint = tcp://127.0.0.1:5556
    
    [watcher:myworker]
    cmd = chaussette --fd $(circus.sockets.myworker) --backend gevent wsgi.app
    use_sockets = True
    numprocesses = 2
    copy_env = True
    copy_path = True
    
    [socket:myworker]
    host = 127.0.0.1
    port = 8000

Lets focus on the watcher section, you can lookup what the other config does on the [configuration](http://circus.readthedocs.org/en/0.8.1/configuration/) docs. What the watcher `myworker` does is spawn Chaussette processes and run it over the file descriptor defined on the socket section below. Chaussette supports different kinds of backend, here we're using gevent.

We're also telling our worker to only spawn 2 chaussette processes via `numprocesses` config. The `use_sockets` is what actually allows this worker to use the socket defined below since parent descriptors are closed by default when the child processes (Chaussette) is forked.

If we don't use file descriptor, since we have two workers they will both try to bind on the default host:port of chaussette and the first one will be able to but the second one will throw an error since the port is already taken by the first worker. With file descriptors, they are inherited when forking, hence the file descriptor is shared between worker.

Once circus is running, we can control our worker via `circusctl` command. `circusctl status` will show your worker's status, you can also restart using `circusctl restart myworker` these should be pretty much familiar as its quite similar to other control commands. And if you're using [SaltStack](https://salt.readthedocs.org/en/latest/), you might be interested on the SaltStack module I [wrote](https://github.com/saltstack/salt-contrib/blob/master/modules/circus.py).

That's it, we've used a basic WSGI app here but as you can imagine we can just as easily use the same for Django, Pyramid or any other Python web framework that has a wsgi app. Just replace `wsgi.app` to the relative path where your wsgi app is located.

