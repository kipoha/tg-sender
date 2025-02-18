# START PROJECT

## DEV DOCKER
```bash
sudo docker compose -f devops/docker/docker-compose.yml -f devops/docker/dev/docker-compose-dev.yml up --build -d
```


---
## PROD DOCKER
```bash
sudo docker compose -f devops/docker/docker-compose.yml -f devops/docker/prod/docker-compose-prod.yml up --build -d
```


---
## CERTBOT SSL
installing(Ubuntu/Debian):
```bash
sudo apt update
sudo apt install certbot python3-certbot-nginx
```

get certificate
```bash
sudo certbot certonly --webroot --webroot-path=/var/www/certbot -d your_domain.com --email your_mail@gmail.com --agree-tos --non-interactive --rsa-key-size 4096
```

## REMOVE ALL MIGRATIONS
```bash
find . -path './*/migrations/*' ! -name '__init__.py' -type f -exec rm -f {} +
```
