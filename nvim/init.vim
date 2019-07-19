"" Python environment
"" For Windows
if $OS == 'Windows_NT'
  let g:python3_host_prog = '~/AppData/Local/Programs/Python/Python37-32/python'
endif
"" for only neovim. in pyenv virtualenv named 'nvim-python3'
if has('nvim') && isdirectory( $PYENV_ROOT."/versions/nvim-python3" )
  let g:python3_host_prog = $PYENV_ROOT.'/versions/nvim-python3/bin/python'
endif


"" Option
set nocompatible
syntax on
set history=2000
set viminfo='100,/50,%,<1000,f50,s100,:100,c,h,!
set display=lastline
set notitle
set shortmess+=I
set nobackup
set updatetime=0
set encoding=utf8
set hlsearch
set incsearch
set ignorecase
set smartcase
set nowrapscan
set showmatch
set matchtime=1
set whichwrap=b,s,h,l,<,>,[,]
set backspace=start,eol,indent
set nostartofline
set termguicolors
set expandtab
set tabstop=2
set shiftwidth=2
set cmdheight=1
set laststatus=2
set ruler
set number
set showtabline=2
set autoindent
set cursorline
set clipboard=unnamed
set list listchars=tab:\▸\-
set pastetoggle=<F3>
set runtimepath+=~/.cache/dein/repos/github.com/Shougo/dein.vim
noremap! <S-Insert> <C-R>+


"" Key
let mapleader="\<Space>"
map <Leader>i gg=<S-g><C-o><C-o>zz
noremap <Leader>s :%s/
nnoremap <silent> <leader>tt :<c-u>tabnext<cr>
nnoremap <silent> <leader>tc :<c-u>tabnew<cr>
nnoremap <silent> <leader>ww <C-w>w
nnoremap <silent> <leader>wh :<C-u>sp<CR>
nnoremap <silent> <leader>wv :<C-u>vs<CR>
nnoremap <silent> <leader>bn :bnext<CR>


"" Dein
let s:cache_home = empty($XDG_CACHE_HOME) ? expand('~/.cache') : $XDG_CACHE_HOME
let s:dein_dir = s:cache_home . '/dein'
let s:dein_repo_dir = s:dein_dir . '/repos/github.com/Shougo/dein.vim'
if !isdirectory(s:dein_repo_dir)
  call system('git clone https://github.com/Shougo/dein.vim ' . shellescape(s:dein_repo_dir))
endif

if dein#load_state('~/.cache/dein')
  call dein#begin('~/.cache/dein')
  call dein#load_toml('~/.config/nvim/dein.toml', {'lazy': 0})
  call dein#load_toml('~/.config/nvim/dein_lazy.toml', {'lazy': 1})
  call dein#end()
  call dein#save_state()
endif
if dein#check_install()
  call dein#install()
endif
filetype plugin indent on
syntax enable

:command UP UpdateRemotePlugins
