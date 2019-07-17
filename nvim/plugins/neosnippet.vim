imap <expr><CR> 
      \ (pumvisible() && neosnippet#expandable()) ? 
      \ "\<Plug>(neosnippet_expand_or_jump)" : 
      \ pumvisible() ? deoplete#close_popup() : "\<CR>"
imap <expr><TAB> neosnippet#expandable_or_jumpable() ?
      \ "\<Plug>(neosnippet_expand_or_jump)" : "\<TAB>"
