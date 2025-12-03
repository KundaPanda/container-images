#!/bin/sh
set -e

echo "Checking presence of opencloud.yaml config"
if [ ! -f /etc/opencloud.yaml ]; then
  echo "Creating a new opencloud config"
  /usr/bin/opencloud init --insecure=false 1> /dev/null;
else
  echo "Config exists, continuing";
fi

if [ -d /etc/opencloud-configs && ! find /etc/opencloud-configs/ -type d -empty ]; then
  echo "Copying opencloud config files";
  /bin/cp -aL /etc/opencloud-configs/* /etc/opencloud/;
else
  echo "Config directory /etc/opencloud-configs doesn't exist. Skipping config copy."
fi

echo "Starting Opencloud"

/usr/bin/opencloud server
