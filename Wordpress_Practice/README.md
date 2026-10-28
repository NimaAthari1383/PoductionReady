# Wordpress Practice

## Table Of Contents

- [HLD](#hld)
- [Pull Images](#pull-images)
- [Create Network](#create-network)
- [Create Volumes](#create-volumes)
- [Run Mysql Container](#run-mysql-container)
- [Run Wordpress Container](#run-wordpress-container)
- [Create Nginx Files & Directories](#create-nginx-files--directories)
- [Nginx Configuration File](#nginx-configuration-file)
- [Get Certificate](#get-certificate)
- [Run Nginx Container](#run-nginx-container)
- [Get Backup](#get-backup)

- [Compose File](#compose-file)

---

## HLD

Wordpress + Mysql + Nginx

***[🔝 Table Of Contents](#table-of-contents)***

---

## Pull Images

Pull images based on your needs or if exists, skip this step:

```bash
docker pull nginx:latest
docker pull wordpress:latest
docker pull mysql:latest
```

***NOTE:*** It's not recommended to use **`latest`** tags. Always try to use sopecsific tags for images.

***[🔝 Table Of Contents](#table-of-contents)***

---

## Create Network

Create networks with bridge driver to connect services:

```bash
docker network create --driver bridge wp-net

# Check Changes
docker network ls
docker network inspect wp-net
```

***[🔝 Table Of Contents](#table-of-contents)***

---

## Create Volumes

Create volumes for services:

```bash
docker volume create --name wp-data
docker volume create --name db-data

# Check Changes
docker volume ls
docker volume inspect wp-data
docker volume inspect db-data
```

***[🔝 Table Of Contents](#table-of-contents)***

---

## Run Mysql Container

Now times for create mysql container and setup our database service based on our needs:

```bash
docker run -d --name mysql --hostname mysql \
--network=wp-net --restart=always \
-v db-data:/var/lib/mysql \
-e MYSQL_ROOT_PASSWORD=sdvfsacsiojoijsaefawefmwervs \
-e MYSQL_DATABASE=DevOps \
-e MYSQL_USER=DevOps \
-e MYSQL_PASSWORD=sdvfsacsiojoijsaefawefmwervs \
mysql:latest

# Check Changes
docker ps
docker stats --no-stream mysql
docker logs -f mysql
docker exec -i mysql mysql -u root -psdvfsacsiojoijsaefawefmwervs  <<< "show databases"
```

***RECOMENDDATION:*** It's really no recommend to use these users and passwords and names. This scenario is for test and check our knowledge for practice. Use keepasses to store your insformation and use these such apps to generate strong users and passwords and either store them.

***[🔝 Table Of Contents](#table-of-contents)***

---

## Run Wordpress Container

Now create wordpress container and setup wordpress service based on your needs:

```bash
docker run -d --name wordpress --hostname wordpress \
--network=wp-net --restart=always \
-v wp-data:/var/www/html/ \
-e WORDPRESS_DB_PASSWORD=sdvfsacsiojoijsaefawefmwervs \
-e WORDPRESS_DB_HOST=mysql:3306 \
-e WORDPRESS_DB_USER=DevOps \
-e WORDPRESS_DB_NAME=DevOps \
wordpress:latest

# Check Changes
docker ps
docker stats --no-stream
docker logs wordpress
```

***RECOMENDDATION:*** It's really no recommend to use these users and passwords and names. This scenario is for test and check our knowledge for practice. Use keepasses to store your insformation and use these such apps to generate strong users and passwords and either store them.

***[🔝 Table Of Contents](#table-of-contents)***

---

## Create Nginx Files & Directories

Create nginx files and directories for saving our configuations and certificates:

```bash
mkdir -p ./nginx/conf.d
mkdir -p ./nginx/certs
tree ./nginx
```

***[🔝 Table Of Contents](#table-of-contents)***

---

## Nginx Configuration File

Add wordpress configuration file to nginx directory recently created:

```bash
cat <<'ROT' > ./nginx/conf.d/wordpress.conf
server {
  listen 443 ssl;
  server_name wp.nima.local;

  # SSL
  ssl_certificate /etc/nginx/certs/cert.pem;
  ssl_certificate_key /etc/nginx/certs/key.pem;

  location / {
    proxy_pass            http://wordpress:80;
    proxy_set_header  Host              $http_host;   # required for docker client's sake
    proxy_set_header  X-Real-IP         $remote_addr; # pass on real client's IP
    proxy_set_header  X-Forwarded-For   $proxy_add_x_forwarded_for;
    proxy_set_header  X-Forwarded-Proto $scheme;
    add_header X-Powered-By "Nima Athari | wp.nima.local";
    }
}

server {
    listen 80;
    server_name wp.nima.local;
    return 301 https://$host$request_uri;
}
ROT
```

***[🔝 Table Of Contents](#table-of-contents)***

---

## Get Certificate

Get certificate for wordpress, or can get certificate for domain wildcard:

```bash
# Define Certificate Location
CERT_LOCATION=./nginx/certs

# Generate Key & Certificate
openssl req -x509 -nodes -newkey \
rsa:4096 -days 365 \
-keyout $CERT_LOCATION/key.pem \
-subj "/C=IR/ST=Iran/L=Tehran/O=NimaAthari/OU=IT/CN=nima.local/emailAddress=athari.nima.99@gmail.com" \
-out $CERT_LOCATION/cert.pem

# Cehck Generated Certificate
openssl x509 -text -noout -in $CERT_LOCATION/cert.pem

# Check `nginx` Directory
tree nginx
```

***[🔝 Table Of Contents](#table-of-contents)***

---

## Run Nginx Container

Create ngix container and setup nginx service based on your needs:

```bash
docker run -d --name nginx --hostname nginx \
--network=wp-net --restart=always \
-v ${PWD}/nginx/conf.d:/etc/nginx/conf.d \
-v ${PWD}/nginx/certs:/etc/nginx/certs \
-p 80:80 -p 443:443 \
nginx:latest

# Check Nginx Services
docker ps
docker stats --no-stream
docker logs nginx
curl -I -L -k http://127.0.0.1
```

***[🔝 Table Of Contents](#table-of-contents)***

---

## Get Backup

```bash
docker exec -i mysql mysqldump -u root -psdvfsacsiojoijsaefawefmwervs --all-databases --single-transaction --quick  > full-backup-$(date +%F).sql

# Check Backup
ls | grep full-backup-*.sql
du -sh full-backup-*.sql
```

***[🔝 Table Of Contents](#table-of-contents)***

---

## Compose File

Compose file is available in "". For skipping all steps and setup scenario, just need to execute this command:

```bash
sh nginx_config.sh ; docker compose up -d
```

It's introduced and detailed at follow.

***[🔝 Table Of Contents](#table-of-contents)***

---

## Dockerfiles

There are some images which defined in custome dockerfiles. In all dockerfiles, first used a base image used **`FROM`**:

```bash
FROM mysql:latest
```

Then maintainer is available as **`LABEL`**:

```bash
LABEL maintainers="Nima Athari"
```

Updated apt repo and installed bash_completion just for test:

```bash
RUN apt update \
    && apt install -y bash-completion 
```

For nginx , also configured logging using below commands:

```bash
RUN ln -sf /dev/stdout /var/log/nginx/access.log \
    && ln -sf /dev/stderr /var/log/nginx/error.log
```

Expose 80 and 443 ports for nginx:

```bash
EXPOSE 80 443
```

Use a process to set nginx state up:

```bash
CMD ["nginx","-g","daemon off;"]
```
