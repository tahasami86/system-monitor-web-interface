#!/bin/bash

# Script to install Lighttpd, PHP, Flask, and InfluxDB dependencies on Raspberry Pi 3B v2
# First ensure we have proper permissions
if [[ $EUID -ne 0 ]]; then
   echo "This script must be run as root or with sudo"
   exit 1
fi

# Update package list and upgrade existing packages
echo "Updating system packages..."
apt-get update && apt-get upgrade -y

# Install essential build tools and dependencies first
echo "Installing essential dependencies..."
apt-get install -y build-essential curl wget gnupg2 lsb-release

# Install Lighttpd and PHP with necessary modules
echo "Installing Lighttpd and PHP..."
apt-get install -y lighttpd php7.4-cgi php7.4-fpm php7.4-gd php7.4-json
# Note: If php7.4 isn't available, the system will use the default version

# Configure Lighttpd with FastCGI
echo "Configuring Lighttpd..."
lighttpd-enable-mod fastcgi
lighttpd-enable-mod fastcgi-php
service lighttpd force-reload

# Install Python3 and pip with required packages
echo "Installing Python and Flask..."
apt-get install -y python3-dev python3-pip
pip3 install --upgrade pip
pip3 install flask psutil influxdb-client

# Install InfluxDB (using the official repository for ARM)
echo "Installing InfluxDB..."
curl -sL https://repos.influxdata.com/influxdb.key | gpg --dearmor | tee /etc/apt/trusted.gpg.d/influxdb.gpg > /dev/null
echo "deb https://repos.influxdata.com/debian $(lsb_release -cs) stable" | tee /etc/apt/sources.list.d/influxdb.list
apt-get update
apt-get install -y influxdb

apt-get update
apt-get install -y influxdb influxdb-client


 Create initial InfluxDB configuration
echo "Setting up InfluxDB configuration..."
cat > /etc/influxdb/influxdb.conf << EOF
[meta]
  dir = "/var/lib/influxdb/meta"

[data]
  dir = "/var/lib/influxdb/data"
  wal-dir = "/var/lib/influxdb/wal"

[http]
  enabled = true
  bind-address = ":8086"
  auth-enabled = false
EOF

# Set proper permissions for InfluxDB directories
chown -R influxdb:influxdb /var/lib/influxdb
chmod -R 755 /var/lib/influxdb

# Restart InfluxDB to apply changes
systemctl restart influxdb

# Verify InfluxDB installation
echo "Verifying InfluxDB installation..."
sleep 5  # Give InfluxDB time to start up
influx -execute "SHOW DATABASES"


# Create necessary directories and set permissions
echo "Setting up web server directories..."
mkdir -p /var/www/html
chown -R www-data:www-data /var/www/html
chmod -R 755 /var/www/html

# Start and enable services
echo "Starting and enabling services..."
systemctl enable influxdb
systemctl start influxdb
systemctl enable lighttpd
systemctl start lighttpd

# Create a basic test PHP file to verify installation
echo "Creating test PHP file..."
cat > /var/www/html/info.php << EOF
<?php
phpinfo();
?>
EOF
chown www-data:www-data /var/www/html/info.php

# Final system checks
echo "Performing final checks..."
systemctl status lighttpd | grep "Active:"
systemctl status influxdb | grep "Active:"

echo "Installation completed!"
echo "You can test PHP by visiting http://[your-pi-ip]/info.php"
echo "Remember to remove info.php in production for security"