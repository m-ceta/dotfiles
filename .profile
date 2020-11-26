# ~/.profile: executed by the command interpreter for login shells.
# This file is not read by bash(1), if ~/.bash_profile or ~/.bash_login
# exists.
# see /usr/share/doc/bash/examples/startup-files for examples.
# the files are located in the bash-doc package.

# the default umask is set in /etc/profile; for setting the umask
# for ssh logins, install and configure the libpam-umask package.
#umask 022

# if running bash
if [ -n "$BASH_VERSION" ]; then
  # include .bashrc if it exists
  if [ -f "$HOME/.bashrc" ]; then
    . "$HOME/.bashrc"
  fi
fi

# set PATH so it includes user's private bin if it exists
if [ -d "$HOME/bin" ] ; then
  PATH="$HOME/bin:$PATH"
fi

# set PATH so it includes user's private bin if it exists
if [ -d "$HOME/.local/bin" ] ; then
  PATH="$HOME/.local/bin:$PATH"
fi
if [ -d "$HOME/go" ] ; then
  export GOPATH=$HOME/go
  if [ -d "$GOPATH/bin" ] ; then
    PATH="$GOPATH/bin:$PATH"
  fi
fi
if [ -d "$HOME/.cargo/bin" ] ; then
  PATH="$HOME/.cargo/bin:$PATH"
fi

# Proxy
if [ -e /proc/sys/fs/binfmt_misc/WSLInterop ]; then
  if [ -e $HOME/.bussiness ]; then
    export http_proxy=http://192.168.109.170:8080
    export https_proxy=http://192.168.109.170:8080
    export GTK_IM_MODULE=fcitx
    export QT_IM_MODULE=fcitx
    export XMODIFIERS="@im=fcitx"
    export DefaultIMModule=fcitx
    xset -r 49
  fi
fi

# Pyenv
export PYENV_ROOT="$HOME/.pyenv"
export PATH="$PYENV_ROOT/bin:$PATH"
if command -v pyenv 1>/dev/null 2>&1; then
  eval "$(pyenv init -)"
fi
eval "$(pyenv virtualenv-init -)"
if [ -d "$HOME/mypypkg" ] ; then
  export PYTHONPATH="$HOME/mypypkg:$PYTHONPATH"
fi
if [ -d "$HOME/vitesse" ] ; then
  export PYTHONPATH="$HOME/vitesse/Hull:$HOME/vitesse/Lib:$HOME/vitesse/Ext:$PYTHONPATH"
fi

# Android
export PATH=$PATH:~/Android/sdk/platform-tools
export ANDROID_SDK_ROOT=~/Android/Sdk
export ANDROID_HOME=$ANDROID_SDK_ROOT
export ANDROID_NDK_ROOT=~/Android/android-ndk-r21d
export NDK_HOME=$ANDROID_NDK_ROOT

# Neovim
export XDG_CONFIG_HOME=$HOME/.config
export XDG_CACHE_HOME=$HOME/.cache
