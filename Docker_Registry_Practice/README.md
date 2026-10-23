# Docker Registry Practice

## Table Of Contents

- [Project Directory](#project-directory)
- [Nginx Configuration](#nginx-configuration)
- [User Permission](#user-permission)
- [Generate Certificate](#generate-certificate)
- [Create Network](#create-network)
- [Run Registry Container](#run-registry-container)
- [Run Registry Container](#run-registry-container)

---

## Project Directory

Create projects directory:

```bash
# Create Project Directory
mkdir -p auth data

# Check Changes
tree
```

***[🔝 Table Of Contents](#table-of-contents)***

---

## Nginx Configuration

Add nginx configurations in `nginx.conf` file:

```bash
vim nginx.conf

events {
    worker_connections  1024;
}

http {

  upstream docker-registry {
    server registry:5000;
  }

  ## Set a variable to help us decide if we need to add the
  ## 'Docker-Distribution-Api-Version' header.
  ## The registry always sets this header.
  ## In the case of nginx performing auth, the header is unset
  ## since nginx is auth-ing before proxying.
  map $upstream_http_docker_distribution_api_version $docker_distribution_api_version {
    '' 'registry/2.0';
  }

  server {
    listen 443 ssl;
    server_name repo1.nima.local;

    # SSL Configs
    ssl_certificate /etc/nginx/conf.d/cert.pem;
    ssl_certificate_key /etc/nginx/conf.d/key.pem;

    # Recommendations from https://raymii.org/s/tutorials/Strong_SSL_Security_On_nginx.html
    ssl_protocols TLSv1.1 TLSv1.2;
    ssl_ciphers 'EECDH+AESGCM:EDH+AESGCM:AES256+EECDH:AES256+EDH';
    ssl_prefer_server_ciphers on;
    ssl_session_cache shared:SSL:10m;

    # disable any limits to avoid HTTP 413 for large image uploads
    client_max_body_size 0;

    # required to avoid HTTP 411: see Issue #1486 (https://github.com/moby/moby/issues/1486)
    chunked_transfer_encoding on;

    location /v2/ {
      # Do not allow connections from docker 1.5 and earlier
      # docker pre-1.6.0 did not properly set the user agent on ping, catch "Go *" user agents
      if ($http_user_agent ~ "^(docker\/1\.(3|4|5(?!\.[0-9]-dev))|Go ).*$" ) {
        return 404;
      }

      # To add basic authentication to v2 use auth_basic setting.
      auth_basic "Registry realm";
      auth_basic_user_file /etc/nginx/conf.d/nginx.htpasswd;

      ## If $docker_distribution_api_version is empty, the header is not added.
      ## See the map directive above where this variable is defined.
      add_header 'Docker-Distribution-Api-Version' $docker_distribution_api_version always;

      proxy_pass                          http://docker-registry;
      proxy_set_header  Host              $http_host;   # required for docker client's sake
      proxy_set_header  X-Real-IP         $remote_addr; # pass on real client's IP
      proxy_set_header  X-Forwarded-For   $proxy_add_x_forwarded_for;
      proxy_set_header  X-Forwarded-Proto $scheme;
      proxy_read_timeout                  900;
    }
  }
  server {
      listen 80;
      server_name repo1.nima.local;
      return 301 https://$host$request_uri;
  }
}
```

***[🔝 Table Of Contents](#table-of-contents)***

---

## User Permission

Add a user and choose password using htpasswd for nginx authentication:

```bash
# Create htpasswd File
sudo htpasswd -c auth/nginx.htpasswd nima

# Check Changes
cat auth/nginx.htpasswd
```

***[🔝 Table Of Contents](#table-of-contents)***

---

## Generate Certificate

Generate certificate for your host or for your domain:

```bash
# Define Certificate Location
CERT_LOCATION=./auth/

# Generate Key & Cert
openssl req -x509 -nodes -newkey \
rsa:4096 -days 365 \
-keyout $CERT_LOCATION/key.pem \
-subj "/C=IR/ST=Iran/L=Tehran/O=NimaAthari/OU=IT/CN=nima.local/emailAddress=athari.nima.99@gmail.com" \
-out $CERT_LOCATION/cert.pem 

# Cehck Generated Certificate
openssl x509 -text -noout -in $CERT_LOCATION/cert.pem

# Check Changes
tree
```

***[🔝 Table Of Contents](#table-of-contents)***

---

## Create Network

Create docker network for scenario:

```bash
docker network create hub
docker network ls 
```

***[🔝 Table Of Contents](#table-of-contents)***

---

## Run Registry Container

Create registry container based on our needs:

```bash
# Run Registry Container
docker run -d -v ${PWD}/data:/var/lib/registry --net hub --restart=always --name registry registry:2

# Check Changes
docker ps 
docker logs -f registry
```

***[🔝 Table Of Contents](#table-of-contents)***

---

## Run Nginx Container

Create nginx container based on our needs:

```bash
# run web container
docker run -d -p 443:443 -p 80:80 -v ${PWD}/auth:/etc/nginx/conf.d -v ${PWD}/nginx.conf:/etc/nginx/nginx.conf:ro \
--net hub --restart=always --name web nginx:alpine

# check
docker ps 
docker logs -f web

# check repository
curl -u "nima:1234" -k https://repo1.nima.local/v2/_catalog
```

***[🔝 Table Of Contents](#table-of-contents)***
