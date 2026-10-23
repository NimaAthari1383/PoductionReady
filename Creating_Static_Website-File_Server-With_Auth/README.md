# Creating a Static Website Nginx and File Server with Authentication

## Table Of Contents

- [Introduction](#introduction)
- [Install Nginx & Move To Destination Server](#install-nginx--move-to-destination-server)
- [Configure Nginx](#configure-nginx)
- [Configuring Web Authentication](#configuring-web-authentication)

---

### Introduction

We want to install nginx, setup a static site setup a web authentication for our static page.

***[🔝 Table Of Contents](#table-of-contents)***

---

### Install Nginx & Move To Destination Server

On destination server install nginx:

```bash
sudo apt install nginx
```

Download your static page and on your host:

```bash
scp -r PATH_TO_YOUR_STATIC_PAGE USERNAME@HOST_IP:/home/USERNAME
```

***[🔝 Table Of Contents](#table-of-contents)***

---

### Configure Nginx

```bash
cd /etc/nginx
ls sites-available
mv sites-available/default conf.d/
rm sites-enabled/default -rf
cd conf.d
vim default
```

Must have this sample config for listen port of nginx service, site's url and sites files:

```bash
server {
    listen 80;
    server_name SUBDOMAIN.DOMAIN.TLD;   # Change `SUBDOMAIN.DOMAIN.TLD` with  your url; Mine here is mysite.domain.local
    root /PATH_TO_YOUR_STATIC_PAGE;     # Change `` with yours; Mine is /var/www/html/mysite.html
    index index.html;

    location / {
        try_files $uri $uri/ =404;
    }
}
```

Then change config file name and test your configurations and restart and check status of nginx service:

```bash
sudo mv default mysite.conf
nginx -t
sudo systemctl restart nginx ; sudo systemctl status nginx
```

Browse your static page url to watch your changes to be ok.

***[🔝 Table Of Contents](#table-of-contents)***

---

### Add Desire Files To Setup File Service

Create a sample file like `test1.txt` and `helloworld.txt` files:

```bash
cd /var/www/html
touch test1.txt
touch helloworld.txt
```

Add a global variable to your system:

```bash
export MAIN_USER=Nima_Athari
```

Then execute command bellow to add content to them for testing:

```bash
echo "Hello World!" >> /var/www/html/helloworld.txt
echo "Hi dear friend! I'm $MAIN_USER. It's my first test file." >> /var/www/html/test1.txt
```

***[🔝 Table Of Contents](#table-of-contents)***

---

### Configuring Web Authentication

For adding web authentication and improve your security of webpage:

```bash
vim mysite.conf
```

Add/Modify these for web authentication:

```bash
server {
    listen 80;
    server_name SUBDOMAIN.DOMAIN.TLD;   # Change `SUBDOMAIN.DOMAIN.TLD` with  your url; Mine here is mysite.domain.local
    root /PATH_TO_YOUR_STATIC_PAGE;     # Change `/PATH_TO_YOUR_STATIC_PAGE` with yours; Mine is /var/www/html/mysite.html
    autoindex on;

    location / {
        auth_basic "Administrator's Area";
        auth_basic_user_file /PATH_TO_YOUR_.HTPASSWD_FILE;       # Change `/PATH_TO_YOUR_.HTPASWD_FILE` with  your `.htpasswd` file; Mine here is `/etc/nginx/conf.d/mysite.htpasswd`.
        try_files $uri $uri/ =404;
    }
}
```

Then give it's location to htpasswd:

```bash
htpasswd -c /PATH_TO_YOUR_.HTPASWD_FILE USERNAME       # Change `/PATH_TO_YOUR_.HTPASWD_FILE` with  your `.htpasswd` file; Mine here is `/etc/nginx/conf.d/mysite.htpasswd`. Change `USERNAME` with your username which want to grant access to static page. Mine is `webadmin`.
ENTER YOUR_DESIRE_PASSWORD
cd /etc/nginx/conf.d/
cat mysite.htpasswd                                     # Must see your hash of your password have been set
```

***[🔝 Table Of Contents](#table-of-contents)***

---
