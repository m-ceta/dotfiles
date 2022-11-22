set nocompatible
syntax on
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
  GuiFont! ＭＳ\ ゴシック:h14,Cica:h14,Space\ Mono:h14
  GuiScrollBar 1
else
  set guifont=ＭＳ\ ゴシック:h14,Cica:h14,Space\ Mono:h14
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
nnoremap <silent> <C-l> :tabn<CR>
nnoremap <silent> <C-h> :tabp<CR>
nnoremap <silent> <C-a> :tab<Space>ba<CR>
nnoremap <silent> <C-t> :ReuseTerm<CR>
tnoremap <silent> <C-t> <C-\><C-n>:q<CR>
nnoremap <silent> <F4> :Cheat<CR>
noremap! <S-Insert> <C-R>+
nnoremap <silent> <F7> :<C-u>echo sytem('cargo run')<CR>
nnoremap <silent> <S-F7> :<C-u>echo system('cargo check')<CR>
nnoremap <silent> <F8> :<C-u>echo system('cargo build')<CR>
nnoremap <silent> <S-F8> :<C-u>echo system('cargo build --release')<CR>
nmap <Leader>n :CocCommand explorer<CR>
nmap <Leader>o :CocCommand explorer --open-action-strategy tab --sources=buffer+,file+ --position floating<CR>
nnoremap <silent> <leader>ps :StartIPython<CR>
tnoremap <silent> <leader>ps <C-\><C-n>:q<CR>
nnoremap <silent> <leader>pc :SendCellToIPython<CR>
nnoremap <silent> <leader>pr :SendRegionToIPython<CR>
nnoremap <silent> <leader>pa :SendAllToIPython<CR>

" IM OFF command
if has('win32')
  augroup InsertHook
    autocmd!
    autocmd InsertLeave * :call system('%HOMEPATH%\dotfiles\scripts\imeoff.bat')
  augroup END
else
  augroup InsertHook
    autocmd!
    autocmd InsertLeave * :call system('~/dotfiles/scripts/imeoff')
  augroup END
endif

"" Terminal
function! SearchTermBuffer(shell) abort
  for num in nvim_list_bufs()
    let buf = bufname(num)
    if stridx(buf, 'term:') == 0 && stridx(buf, a:shell) > 0
      return num
    endif
  endfor
  return -1
endfunction

function! YankString(data) abort
  if len(a:data) > 0
    let tmp = @a
    let @a = join(a:data, "\n")
    execute 'normal! "ap'
    let @a = tmp
  endif
endfunction

function! GetCellContents() abort
  let contents = []
  let cline = line(".")
  let ccol = col(".")
  let fline = search("^# %%", "bw") + 1
  let aline = search("^# %%", "w") - 1
  if fline > 0 && aline > 0 && aline - fline > 0
    let contents = getline(fline, aline)
  endif
  call cursor(cline, ccol)
  return contents
endfunction

function! GetRegionContents() abort
  let first = a:firstline
  let end   = a:lastline
  if first == 0
    let first = 1
  endif
  if end == 0
    let end = line("$")
  endif
  let contents = getline(first, end)
  return contents
endfunction

function! ReuseTerm(reuse_only, change_term, shell) abort
  let shellname = '/bin/bash'
  if strlen(a:shell) > 0
    let shellname = a:shell
  endif
  let buf = bufname()
  if stridx(buf, 'term:') == 0 && stridx(buf, shellname) > 0
    quit
  else
    let num = SearchTermBuffer(shellname)
    if num  >= 0
      let wnr = win_findbuf(num)
      if len(wnr) > 0
        call win_gotoid(wnr[0])
        if a:change_term == 1
          startinsert
        else
          quit
        endif
        return 3
      else
        botright new
        let cbn = bufnr('%')
        execute num.'buffer'
        execute 'bwipeout '.cbn
        if a:change_term == 1
          startinsert
        endif
        return 2
      endif
    elseif a:reuse_only != 1
      botright new
      call termopen(shellname)
      if a:change_term == 1
        startinsert
      endif
      return 1
    endif
  endif
  return 0
endfunction
command! ReuseTerm :call ReuseTerm(0, 1, $SHELL)

function! SendToIPython(cmd)
  "let num = bufnr()
  "let wnr = win_findbuf(num)
  let contents = []
  if a:cmd == 0
    let contents = GetCellContents()
  elseif a:cmd == 1
    let contents = GetRegionContents()
  elseif a:cmd == 2
    let first = 1
    let end = line("$")
    let contents = getline(first, end)
  endif
  if len(contents) > 0
    let ret = ReuseTerm(1, 1, "ipython3")
    if ret != 0
      sleep 100m
      call YankString(contents)
      "stopinsert
    else
      echo "Please run ipython !"
    endif
    "if len(wnr) > 0
    "  call win_gotoid(wnr[0])
    "endif
  endif
endfunction
command! SendCellToIPython :call SendToIPython(0)
command! -range=% SendRegionToIPython :call SendToIPython(1)
command! SendAllToIPython :call SendToIPython(2)

function! StartIPython()
  let num = bufnr()
  let wnr = win_findbuf(num)
  call ReuseTerm(0, 0, "ipython3")
  if len(wnr) > 0
    call win_gotoid(wnr[0])
  endif
endfunction
command! StartIPython :call StartIPython()

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
