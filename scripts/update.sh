#!/bin/sh
user=m-ceta
pass=$(sh ~/dotfiles/scripts/viewtoken.sh)
auth="${user}\n${pass}\n"
cd ~/dotfiles
git add .
git commit -m "anything"
git push origin master < echo $auth 
