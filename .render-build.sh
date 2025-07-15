#!/usr/bin/env bash
# Tell Render to use the correct Python version and pip install from requirements.txt

echo "Using Python 3.10"
pyenv global 3.10.13

pip install -r requirements.txt
