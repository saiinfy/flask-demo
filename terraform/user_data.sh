#!/bin/bash
# Runs once on first boot (cloud-init). Prepares the server; the pipeline deploys the code.
set -euxo pipefail

export DEBIAN_FRONTEND=noninteractive
apt-get update -y
apt-get install -y python3-venv python3-pip nginx rsync curl

# App directory + virtualenv, owned by the SSH user the pipeline logs in as
mkdir -p /opt/flask-app
chown ubuntu:ubuntu /opt/flask-app
sudo -u ubuntu python3 -m venv /opt/flask-app/venv

# Gunicorn as a systemd service (1 worker so the in-memory demo store stays consistent)
cat > /etc/systemd/system/flask-app.service <<'EOF'
[Unit]
Description=Flask API served by gunicorn
After=network.target

[Service]
User=ubuntu
Group=ubuntu
WorkingDirectory=/opt/flask-app
EnvironmentFile=-/opt/flask-app/.env
ExecStart=/opt/flask-app/venv/bin/gunicorn --workers 1 --threads 4 --bind 127.0.0.1:8000 app.app:app
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
EOF

# nginx reverse proxy: port 80 -> gunicorn on 8000
cat > /etc/nginx/sites-available/flask-app <<'EOF'
server {
    listen 80 default_server;
    server_name _;

    location / {
        proxy_pass         http://127.0.0.1:8000;
        proxy_set_header   Host $host;
        proxy_set_header   X-Real-IP $remote_addr;
        proxy_set_header   X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header   X-Forwarded-Proto $scheme;
    }
}
EOF
ln -sf /etc/nginx/sites-available/flask-app /etc/nginx/sites-enabled/flask-app
rm -f /etc/nginx/sites-enabled/default

# Let the deploy user restart the service without a password
echo "ubuntu ALL=(root) NOPASSWD: /usr/bin/systemctl restart flask-app, /usr/bin/systemctl status flask-app" \
  > /etc/sudoers.d/flask-app
chmod 440 /etc/sudoers.d/flask-app

systemctl daemon-reload
systemctl enable flask-app
systemctl restart nginx
