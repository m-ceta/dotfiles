nnoremap [denite] <Nop>
nmap <C-d> [denite]
nnoremap <silent> [denite]g :<C-u>DeniteCursorWord grep -buffer-name=search-buffer-denite<CR>
nnoremap <silent> [denite]G :<C-u>Denite grep -buffer-name=search-buffer-denite<CR>
nnoremap <silent> [denite]b :<C-u>Denite buffer<CR>
nnoremap <silent> [denite]f :<C-u>DeniteBufferDir -buffer-name=files file<CR>
nnoremap <silent> [denite]m :<C-u>Denite file_mru<CR>
nnoremap <silent> [denite]y :<C-u>Denite neoyank<CR>

let s:denite_default_options = {}
call extend(s:denite_default_options, {
  \   'highlight_matched_char': 'None',
  \   'highlight_matched_range': 'Search',
  \   'match_highlight': v:true,
  \})

" Define mappings
autocmd FileType denite call s:denite_my_settings()
function! s:denite_my_settings() abort
  nnoremap <silent><buffer><expr> <CR>
  \ denite#do_map('do_action')
  nnoremap <silent><buffer><expr> d
  \ denite#do_map('do_action', 'delete')
  nnoremap <silent><buffer><expr> p
  \ denite#do_map('do_action', 'preview')
  nnoremap <silent><buffer><expr> q
  \ denite#do_map('quit')
  nnoremap <silent><buffer><expr> i
  \ denite#do_map('open_filter_buffer')
  nnoremap <silent><buffer><expr> <Space>
  \ denite#do_map('toggle_select').'j'
endfunction

autocmd FileType denite-filter call s:denite_filter_my_settings()
function! s:denite_filter_my_settings() abort
  imap <silent><buffer> <C-o> <Plug>(denite_filter_quit)
  setlocal statusline=%!denite#get_status('sources')
  inoremap <silent><buffer> <Down> <Esc>
     \:call denite#move_to_parent()<CR>
     \:call cursor(line('.')+1,0)<CR>
     \:call denite#move_to_filter()<CR>A
  inoremap <silent><buffer> <Up> <Esc>
     \:call denite#move_to_parent()<CR>
     \:call cursor(line('.')-1,0)<CR>
     \:call denite#move_to_filter()<CR>A
  inoremap <silent><buffer> <C-j> <Esc>
     \:call denite#move_to_parent()<CR>
     \:call cursor(line('.')+1,0)<CR>
     \:call denite#move_to_filter()<CR>A
  inoremap <silent><buffer> <C-k> <Esc>
     \:call denite#move_to_parent()<CR>
     \:call cursor(line('.')-1,0)<CR>
     \:call denite#move_to_filter()<CR>A
  inoremap <silent><buffer> <C-n> <Esc>
     \:call denite#move_to_parent()<CR>
     \:call cursor(line('.')+1,0)<CR>
     \:call denite#move_to_filter()<CR>A
  inoremap <silent><buffer> <C-p> <Esc>
     \:call denite#move_to_parent()<CR>
     \:call cursor(line('.')-1,0)<CR>
     \:call denite#move_to_filter()<CR>A
  inoremap <silent><buffer> <CR> <Esc>
     \:call denite#move_to_parent()<CR>
     \<CR>
  inoremap <silent><buffer> <C-CR> <Esc>
     \:call denite#move_to_parent()<CR>
     \<CR>
  inoremap <silent><buffer> <C-m> <Esc>
     \:call denite#move_to_parent()<CR>
     \<CR>
endfunction




