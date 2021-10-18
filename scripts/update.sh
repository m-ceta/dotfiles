#!/bin/sh
pass=$(sh ~/dotfiles/scripts/viewtoken.sh)
echo $pass | pbcopy
cd ~/dotfiles
git add .
git commit -m "anything"
git push origin master
