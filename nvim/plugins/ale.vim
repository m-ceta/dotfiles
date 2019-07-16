let g:ale_linters = {'python': ['flake8'], }
let g:ale_fixers = {'python': ['autopep8', 'black', 'isort'], }
let g:ale_python_flake8_executable = g:python3_host_prog
let g:ale_python_flake8_options = '-m flake8'
let g:ale_python_autopep8_executable = g:python3_host_prog
let g:ale_python_autopep8_options = '-m autopep8'
let g:ale_python_isort_executable = g:python3_host_prog
let g:ale_python_isort_options = '-m isort'
let g:ale_python_black_executable = g:python3_host_prog
let g:ale_python_black_options = '-m black'

nmap <silent> <Leader>x <Plug>(ale_fix)

let g:ale_fix_on_save = 1
