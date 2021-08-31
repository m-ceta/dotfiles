"nmap <Leader>n :NERDTreeToggle<CR>
let g:NERDTreeWinSize = 80
let g:NERDTreeQuitOnOpen=1
let g:NERDTreeShowHidden = 0
let g:NERDTreeMapOpenInTab = 'e'
let g:NERDTreeMapOpenExpl = 'w'
let g:NERDTreeCustomOpenArgs = {'file':{'where':'t'}}
"autocmd VimEnter * if argc() == 0 && !exists("s:std_in") | NERDTree | endif
"autocmd bufenter * if (winnr("$") == 1 && exists("b:NERDTree") && b:NERDTree.isTabTree()) | q | endif
