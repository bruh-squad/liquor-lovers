#!/bin/sh

gunicorn --bind 0.0.0.0:8000 LiquorLovers.wsgi:application
