#!/usr/bin/bash
DIR="kofnet-bot"

if [[ -d "$DIR" ]]; then
   rm $DIR -rf
fi

git clone https://github.com/Simatwa/kofnet-bot.git
cp .env $DIR/
cd $DIR
pip install -U pip
pip install git+https://github.com/Simatwa/kofnet.git
pip install -r requirements.txt
python run.py
