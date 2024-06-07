#!/bin/bash

mkdir shared
chmod 777 shared
mount -t tmpfs -o size=100M tmpfs ./shared