#!/bin/bash
#install pyenv
git clone git://github.com/yyuu/pyenv.git ~/.pyenv
#install 2 and 3
pyenv install 3.8.5
pyenv install 2.7.18
#make virtualenv
pyenv global 3.8.1
pip install --upgrade pip
pip install virtualenv
virtualenv -p python3 ~/nvim-python3
pyenv global 2.7.18
pip install --upgrade pip
pip install virtualenv
virtualenv -p python ~/nvim-python2
pyenv global system
#install requirement
source ~/nvim-python3/bin/activate
pip install --upgrade pip
pip install pynvim
pip install neovim
deactivate
source ~/nvim-python2/bin/activate
pip install --upgrade pip
pip install pynvim
pip install neovim
deactivate
pip install --upgrade pip
