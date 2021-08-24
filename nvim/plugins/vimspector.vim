let g:vimspector_install_gadgets = [ 'debugpy', 'CodeLLDB' ]

nmap <F9> <Plug>VimspectorToggleBreakpoint
xmap <F9> <Plug>VimspectorToggleBreakpoint
nmap <S-F9> <Plug>VimspectorAddFunctionBreakpoint
xmap <S-F9> <Plug>VimspectorAddFunctionBreakpoint
nmap <F10> <Plug>VimspectorStepOver
xmap <F10> <Plug>VimspectorStepOver
nmap <F11> <Plug>VimspectorStepInto
xmap <F11> <Plug>VimspectorStepInto
nmap <S-F11> <Plug>VimspectorStepOut
xmap <S-F11> <Plug>VimspectorStepOut
nmap <F5> :CreateVimspectorJson<CR><Plug>VimspectorContinue
xmap <F5> :CreateVimspectorJson<CR><Plug>VimspectorContinue
nmap <S-F5> :VimspectorReset<CR>
xmap <S-F5> :VimspectorReset<CR>
nmap <S-C-F5> <Plug>VimspectorRestart
xmap <S-C-F5> <Plug>VimspectorRestart
nmap <F6> <Plug>VimspectorPause
xmap <F6> <Plug>VimspectorPause

function! CreateVimspectorJson()
  if ! has('unix')
    return 1
  endif
  let ext = expand("%:e")
  let file = expand("%:p")
  if ext == "rs"
    let cmdlst = []
    let pathlst = split(file, "/")
    for item in pathlst
      if item == "src"
        break
      endif
      call add(cmdlst, item)
    endfor
    if len(cmdlst) > 1
      let root = "/" . join(cmdlst, "/")
      let json = root . "/" . ".vimspector.json"
      let cmd = root . "/" . "target" . "/" . "debug" . "/" . cmdlst[len(cmdlst) - 1]
      if ! filereadable(json)
        let file_contents = []
        call add(file_contents, '{')
        call add(file_contents, '  "configurations": {')
        call add(file_contents, '    "launch": {')
        call add(file_contents, '      "adapter": "CodeLLDB",')
        call add(file_contents, '      "configuration": {')
        call add(file_contents, '        "request": "launch",')
        call add(file_contents, printf('        "program": "%s"', cmd))
        call add(file_contents, '      }')
        call add(file_contents, '    }')
        call add(file_contents, '  }')
        call add(file_contents, '}')
        call writefile(file_contents, json)
      endif
    endif
  elseif ext == "py" 
    let root = fnamemodify(file, ':p:h')
    let json = root . "/" . ".vimspector.json"
    if ! filereadable(json)
      let file_contents = []
      call add(file_contents, '{')
      call add(file_contents, '  "configurations": {')
      call add(file_contents, '    "Python_Launch": {')
      call add(file_contents, '      "adapter": "debugpy",')
      call add(file_contents, '      "configuration": {')
      call add(file_contents, '        "name": "Python_Launch",')
      call add(file_contents, '        "type": "python",')
      call add(file_contents, '        "request": "launch",')
      call add(file_contents, '        "cwd": "${fileDirname}",')
      call add(file_contents, '        "python": "python3",')
      call add(file_contents, '        "stopOnEntry": true,')
      call add(file_contents, '        "console": "externalTerminal",')
      call add(file_contents, '        "debugOptions": [],')
      call add(file_contents, '        "program": "${file}"')
      call add(file_contents, '      }')
      call add(file_contents, '    }')
      call add(file_contents, '  }')
      call add(file_contents, '}')
      call writefile(file_contents, json)
    endif
  else
    echo "Not compatible !"
  endif
endfunction
command! CreateVimspectorJson :call CreateVimspectorJson()

