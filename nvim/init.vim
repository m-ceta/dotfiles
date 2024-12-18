set nocompatible
syntax on
set encoding=utf-8
set fileencodings=iso-2022-jp,euc-jp,sjis,utf-8
set fileformats=unix,dos,mac
set history=2000
set viminfo='100,/50,%,<1000,f50,s100,:100,c,h,!
set display=lastline
set title
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
set numberwidth=5
set showtabline=2
set autoindent
set cursorline
set clipboard=unnamed
set autochdir
set list listchars=tab:\▸\-
set pastetoggle=<F3>
set runtimepath+=~/.cache/dein/repos/github.com/Shougo/dein.vim
if has('unix')
  set sh=bash
endif
set mouse=a
if exists('g:GuiLoaded')
  GuiTabline 0
  GuiPopupmenu 0
  GuiFont! ＭＳ\ ゴシック:h14
  GuiScrollBar 1
else
  set guifont=ＭＳ\ ゴシック:h14
  set guioptions+=r
endif

"" Key
let mapleader="\<Space>"
map <Leader>I gg=<S-g><C-o><C-o>zz
noremap <Leader>s :%s/
nnoremap <silent> <leader>H :<C-u>sp<CR>
nnoremap <silent> <leader>V :<C-u>vs<CR>
tnoremap <silent> <ESC> <C-\><C-n>
tnoremap <silent> <C-[> <C-\><C-n>
nnoremap <silent> <C-l> :bprev<CR>
nnoremap <silent> <C-h> :bnext<CR>
nnoremap <silent> <F4> :Cheat<CR>
noremap! <S-Insert> <C-R>+
nmap <Leader>n :CocCommand explorer ~<CR>
nmap <Leader>o :CocCommand explorer --sources=buffer+,file+ --position floating ~<CR>

" Toggle Terminal
autocmd TermEnter term://*toggleterm#*
      \ tnoremap <silent><c-t> <Cmd>exe v:count1 . "ToggleTerm"<CR>
nnoremap <silent><c-t> <Cmd>exe v:count1 . "ToggleTerm"<CR>
inoremap <silent><c-t> <Esc><Cmd>exe v:count1 . "ToggleTerm"<CR>

" IM OFF command
if exists("g:neovide")

  set linespace=0
  let g:neovide_padding_top = 2
  let g:neovide_padding_bottom = 2
  let g:neovide_padding_right = 5
  let g:neovide_padding_left = 5
  let g:neovide_transparency = 0.95
  let g:neovide_remember_window_size = v:true
  let g:neovide_cursor_antialiasing = v:true
  let g:neovide_cursor_vfx_mode = "railgun"

  augroup start_nvim
    autocmd!
    autocmd VimEnter * execute ":cd ~"
  augroup END

  augroup ime_input
    autocmd!
    autocmd InsertLeave * execute "let g:neovide_input_ime=v:false"
    autocmd InsertEnter * execute "let g:neovide_input_ime=v:true"
    autocmd CmdlineLeave [/\?] execute "let g:neovide_input_ime=v:false"
    autocmd CmdlineEnter [/\?] execute "let g:neovide_input_ime=v:true"
  augroup END

endif

"" 
let s:cache_home = empty($XDG_CACHE_HOME) ? expand('~/.cache') : $XDG_CACHE_HOME
let s:dein_dir = s:cache_home . '/dein'
let s:dein_repo_dir = s:dein_dir . '/repos/github.com/Shougo/dein.vim'
if !isdirectory(s:dein_repo_dir)
  call system('git clone https://github.com/Shougo/dein.vim ' . shellescape(s:dein_repo_dir))
endif
if isdirectory(s:dein_repo_dir)
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
endif

filetype plugin indent on
syntax enable

:command UP UpdateRemotePlugins
