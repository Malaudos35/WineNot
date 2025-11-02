#!/bin/bash

clear && pytest -v test_api_v1.py

# mycli -h localhost -P 3306 -u wine_user -p secure_password wine_cellar
# mycli -h db -P 3306 -u wine_user -p secure_password wine_cellar

