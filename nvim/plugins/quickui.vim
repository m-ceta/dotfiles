" Define menu
call quickui#menu#reset()
call quickui#menu#install("&File", [
                        \ ["&Open\t(leader)o", 'CocCommand explorer --open-action-strategy tab --sources=buffer+,file+ --position floating'],
                        \ ["&Save All\twa", 'wa'],
                        \ [ "--", '' ],
                        \ ["&Quit\tqa", 'qa'],
                        \ ])
call quickui#menu#install("&View", [
                        \ ["Split Window &Vertical\t(leader)V", 'vs'],
                        \ ["Split Window &Horizontal\t(leader)H", 'sp'],
                        \ ["&Close Window \tclo", 'close'],
                        \ [ "--", '' ],
                        \ ["&Function\t(leader)g", 'Tagbar'],
                        \ ["&Explorer\t(leader)n", 'CocCommand explorer'],
                        \ ["&Terminal\tCtrl+t", 'ReuseTerm'],
                        \ ])
call quickui#menu#install('&Edit', [
                        \ [ "&Undo\tu", 'u'],
                        \ [ "--", '' ],
                        \ [ "Go &Definition\tgd", 'CocActionAsync("jumpDefinition")'],
                        \ [ "Go &Type\tgy", 'CocActionAsync("jumpTypeDefinition")'],
                        \ [ "Go &Implementation\tgi", 'CocActionAsync("jumpImplementation")'],
                        \ [ "Go &References\tgr", 'CocActionAsync("jumpReferences")'],
                        \ [ "--", '' ],
                        \ [ "R&ename\t(leader)rn", 'CocActionAsync("rename")' ],
                        \ [ "&Format\t(leader)f", 'CocActionAsync("format")' ],
                        \ [ "--", '' ],
                        \ [ "&Grep\tCtrl+dG", 'Denite grep -buffer-name=search-buffer-denite' ],
                        \ ])
call quickui#menu#install("&Debug", [
                        \ ["&Create Debug Settings", 'CreateVimspectorJson'],
                        \ ["--", ''],
                        \ ["&Start\t(F5)", 'call vimspector#Continue()'],
                        \ ["&Reset\tShift+(F5)", 'call vimspector#Reset()'],
                        \ ["Restart\tShift+Ctrl+(F5)", 'call vimspector#Restart()'],
                        \ ["&Pause\t(F6)", 'call vimspector#Pause()'],
                        \ ["--", ''],
                        \ ["Step &Over\t(F10)", 'call vimspector#StepOver()'],
                        \ ["Step &Into\t(F11)", 'call vimspector#StepInto()'],
                        \ ["Step Out\tShift+(F11)", 'call vimspector#StepOut()'],
                        \ ["---", ''],
                        \ ["&Breakpoint\t(F9)", 'call vimspector#ToggleBreakpoint()'],
                        \ ])
call quickui#menu#install("&Option", [
                        \ ['Set &Spell %{&spell? "Off":"On"}', 'set spell!'],
                        \ ['Set &Cursor Line %{&cursorline? "Off":"On"}', 'set cursorline!'],
                        \ ['Set &Paste %{&paste? "Off":"On"}', 'set paste!'],
                        \ ])
call quickui#menu#install('H&elp', [
                        \ ["&Cheatsheet", 'help index', ''],
                        \ ['T&ips', 'help tips', ''],
                        \ ['--',''],
                        \ ["&Tutorial", 'help tutor', ''],
                        \ ['&Quick Reference', 'help quickref', ''],
                        \ ['&Summary', 'help summary', ''],
                        \ ], 10000)

" enable to display tips in the cmdline
let g:quickui_show_tip = 1

" context menu.
let content = [
            \ ["Grep Cursor Word", 'DeniteCursorWord grep -buffer-name=search-buffer-denite' ],
            \ ]
" set cursor to the last position
let opts = {'index':g:quickui#context#cursor}

" hit space twice to open menu
noremap <space><space> :call quickui#menu#open()<cr>
noremap <RightMouse> :call quickui#context#open(content, opts)<cr>

