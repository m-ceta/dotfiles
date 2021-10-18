#!/bin/sh
user=m-ceta\n
pass=$(sh ~/dotfiles/scripts/viewtoken.sh)\n
cd ~/dotfiles
git add .
git commit -m "anything"
git push origin master < $user < $pass
