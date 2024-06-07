#!/bin/bash

mkdir /run/shared
chmod 777 /run/shared
mount -t tmpfs -o size=100M tmpfs /run/shared