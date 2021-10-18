#!/bin/sh
pass=$(sh ~/dotfiles/scripts/viewtoken.sh)
echo $pass | xsel --clipboard --input
cd ~/dotfiles
git add .
git commit -m "anything"
git push origin master
