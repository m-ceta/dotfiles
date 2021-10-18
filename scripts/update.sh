#!/bin/sh
user=m-ceta
pass=$(sh ~/dotfiles/scripts/viewtoken.sh)
auth="${user}\n${pass}\n"
cd ~/dotfiles
git add .
git commit -m "anything"
echo $auth
echo $auth | git push origin master
