#!/bin/sh
set -e

echo "Checking presence of opencloud.yaml config"
if [ ! -f /var/lib/opencloud/opencloud.yaml ]; then
  echo "Creating a new opencloud config"
  /usr/bin/opencloud init --insecure=false 1> /dev/null;
  /bin/mv /etc/opencloud/opencloud.yaml /var/lib/opencloud/;
else
  echo "Config already exists";
fi

/bin/ln -sf /var/lib/opencloud/opencloud.yaml /etc/opencloud/opencloud.yaml;

if [ -d /etc/opencloud-configs ] && [ -z "$(find /etc/opencloud-configs/ -type d -empty)" ]; then
  echo "Copying opencloud config files";
  /bin/cp -L /etc/opencloud-configs/*.yaml /etc/opencloud/;
else
  echo "Config directory /etc/opencloud-configs doesn't exist. Skipping config copy."
fi

echo "Starting Opencloud"

/usr/bin/opencloud server
