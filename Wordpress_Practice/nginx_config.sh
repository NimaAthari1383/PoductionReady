# Create nginx files and directories for saving our configuations and certificates:
mkdir -p ./nginx/conf.d
mkdir -p ./nginx/certs
tree ./nginx

# Add wordpress configuration file to nginx directory recently created:

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

# Get certificate for wordpress, or can get certificate for domain wildcard:

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
