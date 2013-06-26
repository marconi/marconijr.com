Title: Deploying Circus
Date: 2013-06-26 14:54
Slug: deploying-circus
Category: Python, Circus, Nginx
Author: Marconi Moreto
Summary: Deploying your circus served app behind nginx.

This post is a continuation from my [previous post](/introduction-to-circus.html) and this time we will deploy our simple WSGI app behind [Nginx](http://nginx.org/). So if you haven't, go ahead and read that one and come back here when you're done.

We will deploying our app using Ubuntu, first we need to install Nginx:

    sudo apt-get install nginx    

and then Circus and Chaussette:

    sudo apt-get install python-pip
    sudo pip install -U circus chaussette

next, lets put our app on `/var/www/app` and we need to add a bit of modification to our `circus.ini` file, add this below your worker section:

    [env:myworker]
    PYTHONPATH = /var/www/app

that env section simply adds the path to our app on the environment so that when chaussette tries to load our app, it'll be able to find it.

Then we need to create our Circus [Upstart](http://upstart.ubuntu.com/getting-started.html) script which handles starting and stopping of circus.

    start on filesystem and net-device-up IFACE=lo
    stop on shutdown
    respawn
    exec /usr/local/bin/circusd --log-output /var/log/circus.log \
                                --pidfile /var/run/circusd.pid \
                                /var/www/app/circus.ini

save it to `/etc/init/circus.conf`, what this does is tells Upstart to start Circus when filesystem and network is ready (which happens when you bootup) and then stop Circus when shutting down. Respawn when the process stops without a clean death (non-zero exit code) and then finally the command to run `circusd` which is the Circus daemon. Notice that the final argument points to `circus.ini` file of our app. The documentation suggest to put it under `/etc/circus.ini` which makes sense specially when you have more than one app relying on Circus but this will do for now.

You need to reboot your system for Upstart to recognize your configuration but iirc there's a way to do that without rebooting I just can't remember. If you do, please feel free to comment below. :)

After reboot, lets make sure that circus is in fact running:

    sudo service circus status

and then try accessing our app:

    $ curl http://localhost:8000
    Hello, World!

already! now we just need let Nginx know to forward all incoming request to our app. Add the following Nginx config to `/etc/nginx/sites-available/myapp.conf`:

    server {
        listen 80 default;
        server_name _;

        location / {
            proxy_pass         http://127.0.0.1:8000;
            proxy_redirect     off;
            proxy_buffering    off;
        }
    }

and then symlink it to `/etc/nginx/sites-enabled/myapp.conf`.

This is a basic config which just proxies all incoming request to our wsgi app. And if we try it again, we should still get the same output as above:

    $ curl http://localhost
    Hello, World!

only this time our request was sent to Nginx and passed down to Circus, you can download the updated app [here](https://dl.dropboxusercontent.com/u/829808/app.tar.gz) and that's it!
