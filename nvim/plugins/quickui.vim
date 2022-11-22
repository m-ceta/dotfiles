" Define Function
function CreateNewFile()
  let f = input("File(dir=" . getcwd() . "): ")
  if strlen(f) > 0
    execute "tabe " . f
  endif
endfunction

function CreateNewRustProject()
  let f = input("Project(dir=" . getcwd() . "): ")
  let cmd = "cargo new " . f . " --bin"
  if strlen(f) > 0
    call system(cmd)
    execute "tabe ". f . "/src/main.rs"
    execute "tabe ". f . "/Cargo.toml"
  endif
endfunction


" Define menu
call quickui#menu#reset()
call quickui#menu#install("&File", [
                        \ ["&Open\t(leader)o", 'CocCommand explorer --open-action-strategy tab --sources=buffer+,file+ --position floating'],
                        \ ["&Save All\twa", 'wa!'],
                        \ [ "--", '' ],
                        \ ["&Create New File", 'call CreateNewFile()'],
                        \ ["&Create New Rust Project", 'call CreateNewRustProject()'],
                        \ [ "--", '' ],
                        \ ["&Quit\tqa", 'qa!'],
                        \ ])
call quickui#menu#install("&View", [
                        \ ["Split Window &Vertical\t(leader)V", 'vs'],
                        \ ["Split Window &Horizontal\t(leader)H", 'sp'],
                        \ ["&Close Window \tclo", 'close'],
                        \ ["&Move Window \twincw", 'winc w'],
                        \ [ "--", '' ],
                        \ [ "Resize window (&+5)\t:vertical resize +5", 'vertical resize +5' ],
                        \ [ "Resize window (&-5)\t:vertical resize -5", 'vertical resize -5' ],
                        \ [ "--", '' ],
                        \ ["&Function\t(leader)g", 'Tagbar'],
                        \ ["&Explorer\t(leader)n", 'CocCommand explorer'],
                        \ ["&Terminal\tCtrl+t", 'ReuseTerm'],
                        \ [ "--", '' ],
                        \ ["&Buffer List", 'call quickui#tools#list_buffer("e")'],
                        \ ["F&unction List", 'call quickui#tools#list_function()'],
                        \ ])
call quickui#menu#install('&Edit', [
                        \ [ "&Undo\tu", 'u'],
                        \ [ "--", '' ],
                        \ [ "Go &Definition\tgd", 'call CocActionAsync("jumpDefinition")'],
                        \ [ "Go &Type\tgy", 'call CocActionAsync("jumpTypeDefinition")'],
                        \ [ "Go &Implementation\tgi", 'call CocActionAsync("jumpImplementation")'],
                        \ [ "Go &References\tgr", 'call CocActionAsync("jumpReferences")'],
                        \ [ "--", '' ],
                        \ [ "Toggle &Comment\tgc(has range) or gcc", 'Commentary' ],
                        \ [ "--", '' ],
                        \ [ "R&ename Code\t(leader)rn", 'call CocActionAsync("rename")' ],
                        \ [ "&Format Code\t(leader)f", 'call CocActionAsync("format")' ],
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
call quickui#menu#install("&Rust", [
                        \ ["&Run\t(F7)", 'echo system("cargo run")'],
                        \ ["&Check\tShift+(F7)", 'echo system("cargo check")'],
                        \ [ "--", '' ],
                        \ ["&Build\t(F8)", 'echo system("cargo build")'],
                        \ ["Build &Release\tShift+(F8)", 'echo system("cargo build --release")'],
                        \ ], '<auto>', 'rust')
call quickui#menu#install("&Python", [
                        \ ["Send &cell to ipython\t(leader)pc", 'SendCellToIPython'],
                        \ ["Send &region to ipython\t(leader)pr", 'SendRegionToIPython'],
                        \ ["Send &all to ipython\t(leader)pa", 'SendAllToIPython'],
                        \ ["---", ''],
                        \ ["Start &ipython\t(leader)ps", 'StartIPython'],
                        \ ], '<auto>', 'python')
call quickui#menu#install("&Git", [
                        \ ['&Add', 'Git add %'],
                        \ ['&Commit', 'Git commit'],
                        \ ['&Remove', 'Git rm'],
                        \ ['&Push', 'Git push'],
                        \ ['P&ull', 'Git pull'],
                        \ [ "--", '' ],
                        \ ['&Status', 'Git status'],
                        \ ['&Diff', 'Git diff'],
                        \ ['&Grep', 'Git grep'],
                        \ ['&Blame', 'Git blame'],
                        \ [ "--", '' ],
                        \ ['B&ranch', 'Git branch'],
                        \ ['C&heckout', 'Git checkout'],
                        \ ['&Merge', 'Git merge'],
                        \ [ "--", '' ],
                        \ ['&Yank m-ceta pashphrase', 'let @+ = trim(system("sh ~/dotfiles/scripts/viewtoken.sh"))'],
                        \ ])
call quickui#menu#install("&Option", [
                        \ ['Set &Spell %{&spell? "Off":"On"}', 'set spell!'],
                        \ ['Set &Cursor Line %{&cursorline? "Off":"On"}', 'set cursorline!'],
                        \ ['Set &Paste %{&paste? "Off":"On"}', 'set paste!'],
                        \ ])
call quickui#menu#install('H&elp', [
                        \ ["&Cheatsheet", 'help index'],
                        \ ['T&ips', 'help tips'],
                        \ ['--',''],
                        \ ["&Tutorial", 'help tutor'],
                        \ ['&Quick Reference', 'help quickref'],
                        \ ['&Summary', 'help summary'],
                        \ ])

" enable to display tips in the cmdline
let g:quickui_show_tip = 1
let g:quickui_border_style = 2
let g:quickui_color_scheme = 'papercol dark'

" context menu.
let content = [
            \ ["&Grep Cursor Word", 'DeniteCursorWord grep -buffer-name=search-buffer-denite' ],
            \ ['--',''],
            \ ["To &Lower", 'silent normal vawu' ],
            \ ["To &Upper", 'silent normal vawU' ],
            \ ]
" set cursor to the last position
let opts = {'index':g:quickui#context#cursor}

" hit space twice to open menu
noremap <space><space> :<C-u>call quickui#menu#open()<cr>
noremap <RightMouse> :<C-u>call quickui#context#open(content, opts)<cr>


