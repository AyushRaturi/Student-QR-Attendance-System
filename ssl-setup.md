# SSL Certificate Setup

## Create SSL Directory
```bash
mkdir ssl
```

## Option 1: Self-Signed Certificate (Development)
```bash
openssl req -x509 -newkey rsa:4096 -keyout ssl/your-domain.key -out ssl/your-domain.crt -days 365 -nodes
```

## Option 2: Let's Encrypt (Production)
```bash
# Install certbot
sudo apt-get install certbot

# Generate certificate
sudo certbot certonly --standalone -d your-domain.com -d www.your-domain.com

# Copy certificates
sudo cp /etc/letsencrypt/live/your-domain.com/fullchain.pem ssl/your-domain.crt
sudo cp /etc/letsencrypt/live/your-domain.com/privkey.pem ssl/your-domain.key
```

## Deploy with SSL
```bash
docker-compose up --build
```

## Access Application
- HTTP: http://your-domain.com (redirects to HTTPS)
- HTTPS: https://your-domain.com