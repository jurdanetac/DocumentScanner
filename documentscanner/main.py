#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TOKEN_PATH = f"{ROOT_DIR}/token"

try:
    with open(TOKEN_PATH, 'r') as file:
        TOKEN = file.read().strip()
except FileNotFoundError:
    print("Bot token file not found")
    sys.exit(1)

print("Hello, world!")
print(TOKEN)
