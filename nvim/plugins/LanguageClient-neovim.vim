set hidden

let g:LanguageClient_serverCommands = {}
if executable('clangd')
  let g:LanguageClient_serverCommands['cpp'] = ['clangd']
  let g:LanguageClient_serverCommands['c'] = ['clangd']
endif
if executable('pyls')
  let g:LanguageClient_serverCommands['python'] = ['pyls']
endif
if executable($GOPATH.'/bin/go-langserver')
  let g:LanguageClient_serverCommands['go'] = [$GOPATH.'/bin/go-langserver','-format-tool','gofmt','-lint-tool','golint']
endif
if executable('rls')
  let g:LanguageClient_serverCommands['rust'] = ['rustup', 'run', 'stable', 'rls']
endif
if executable('fortls')
  let g:LanguageClient_serverCommands['fortran'] = ['fortls', '--notify_init', '--incrmental_sync', '--autocomplete_no_prefix']
endif

augroup LanguageClient_config
  autocmd!
  autocmd User LanguageClientStarted setlocal signcolumn=yes
  autocmd User LanguageClientStopped setlocal signcolumn=auto
augroup END

augroup LCHighlight
  autocmd!
  autocmd CursorHold,CursorHoldI *.py,*.c,*.cpp,*.go,*.rs call LanguageClient#textDocument_documentHighlight()
augroup END

let g:LanguageClient_autoStart = 1
nnoremap <Leader>lh :call LanguageClient_textDocument_hover()<CR>
nnoremap <Leader>ld :call LanguageClient_textDocument_definition()<CR>
nnoremap <Leader>lr :call LanguageClient_textDocument_rename()<CR>
nnoremap <Leader>lf :call LanguageClient_textDocument_formatting()<CR>
nnoremap <F2> :call LanguageClient_contextMenu()<CR>

