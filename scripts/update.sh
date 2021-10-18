#!/bin/sh
user=m-ceta
pass=$(sh ~/dotfiles/scripts/viewtoken.sh)
cd ~/dotfiles
git add .
git commit -m "anything"
git push origin master < $user < $pass
