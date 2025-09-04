#!/bin/sh
flask --app app:create_app db upgrade
exec flask --app app:create_app run --host=0.0.0.0 --port=5000
