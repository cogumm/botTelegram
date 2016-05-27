#!/bin/bash -eux

#VENV_DIR=venv
#PIP=$VENV_DIR/bin/pip3
PIP_PACKAGES="requests pony parse pdfkit pyslack-real python-telegram-bot feedparser"

#virtualenv --no-site-packages --prompt="(granumsalis)" $VENV_DIR

sudo pip3 install $PIP_PACKAGES

#source $VENV_DIR/bin/activate
#deactivate