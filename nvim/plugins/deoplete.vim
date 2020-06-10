let g:deoplete#enable_at_startup   = 1
let g:neocomplcache_max_list = 6
let g:deoplete#auto_complete_delay = 0
let g:deoplete#auto_complete_start_length = 1
let g:deoplete#enable_camel_case = 0
let g:deoplete#enable_ignore_case = 0
let g:deoplete#enable_refresh_always = 0
let g:deoplete#enable_smart_case = 1
let g:deoplete#file#enable_buffer_path = 1
let g:deoplete#max_list = 10000
set completeopt-=preview
"autocmd InsertLeave,CompleteDone * if pumvisible() == 0 | pclose | endif
