#!/bin/bash

docker run -d -p 1178:1178 -v ./features/:/app/features/ alex-server
