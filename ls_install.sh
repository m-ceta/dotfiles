#!/bin/sh

# c/c++
sudo apt install clang-10 clang-format-10 clang-tidy-10 clang-tools-10 clangd-10

# rust
#curl https://sh.rustup.rs -sSf | sh
rustup component add rls rust-analysis rust-src

# go
#sudo add-apt-repository ppa:longsleep/golang-backports
#sudo apt update
#sudo apt install golang
go get -u github.com/sourcegraph/go-langserver

# python
#sudo apt install python3-pip
pip3 install python-language-server
pip3 install pyls-isort
pip3 install pyls-black
pip3 install pyflakes

# fortran
pip3 install fortran-language-server

