-- =========================
-- 基本設定
-- =========================
local opt = vim.opt
opt.encoding = 'utf-8'
opt.fileencodings = { 'iso-2022-jp', 'euc-jp', 'sjis', 'utf-8' }
opt.fileformats = { 'unix', 'dos', 'mac' }
opt.history = 2000
opt.shada = [[!,'100,<1000,s100,:100,h]]
opt.display = 'lastline'
opt.title = true
opt.shortmess:append('I')
opt.backup = false
opt.updatetime = 0
opt.hlsearch = true
opt.incsearch = true
opt.ignorecase = true
opt.expandtab = true
opt.tabstop = 2
opt.shiftwidth = 2
opt.cmdheight = 1
opt.laststatus = 2
opt.ruler = true
opt.number = true
opt.numberwidth = 5
opt.autoindent = true
opt.cursorline = true
opt.clipboard = 'unnamed'
opt.autochdir = true
opt.list = true
opt.listchars = { tab = '▸-' }
if vim.g.GuiLoaded then
  -- nvim-qt 等の GUI コマンドは :Gui* 系をそのまま叩く
  vim.cmd([[
    GuiTabline 1
    GuiPopupmenu 0
    GuiFont! ＭＳ\ ゴシック:h14
    GuiScrollBar 1
  ]])
else
  -- 端末UIや他GUIのためのフォント指定
  vim.opt.guifont = "ＭＳ ゴシック:h14"
end

-- =========================
-- キーマップ
-- =========================
local map = vim.keymap.set
local cmd = vim.cmd

-- 1) インデント整形：ファイル全体を再インデント → 元位置へ2回ジャンプ戻し → 画面中央揃え
map('n', '<Leader>I', 'gg=<S-g><C-o><C-o>zz', { noremap = true, silent = true, desc = 'Reindent whole buffer & recenter' })

-- 2) 置換（:%s/ をコマンドラインに出す）
map({ 'n', 'x', 'o' }, '<Leader>s', ':%s/', { noremap = true, silent = false, desc = ':%s/ …' })

-- 3) 分割系
map('n', '<leader>H', '<Cmd>sp<CR>', { noremap = true, silent = true, desc = 'Horizontal split' })
map('n', '<leader>V', '<Cmd>vs<CR>', { noremap = true, silent = true, desc = 'Vertical split' })

-- 4) ターミナル → ノーマルへ戻る（<Esc>, <C-[>）
map('t', '<Esc>', [[<C-\><C-n>]], { noremap = true, silent = true, desc = 'Terminal: exit to normal' })
map('t', '<C-[>', [[<C-\><C-n>]], { noremap = true, silent = true, desc = 'Terminal: exit to normal' })

-- 5) バッファ移動（注意: 一般慣習では h=prev, l=next だが、元設定に忠実に）
map('n', '<C-l>', '<Cmd>bprev<CR>', { noremap = true, silent = true, desc = 'Prev buffer' })
map('n', '<C-h>', '<Cmd>bnext<CR>', { noremap = true, silent = true, desc = 'Next buffer' })

-- 6) F4: :Cheat
map('n', '<F4>', '<Cmd>Cheat<CR>', { noremap = true, silent = true, desc = ':Cheat' })

-- 7) Shift+Insert でクリップボード貼り付け（挿入/コマンドライン）
map({ 'i', 'c' }, '<S-Insert>', '<C-R>+', { noremap = true, silent = true, desc = 'Paste from clipboard' })

-- 8) coc-explorer 起動
map('n', '<Leader>n', '<Cmd>CocCommand explorer ~<CR>', { noremap = false, silent = true, desc = 'coc-explorer home' })
map('n', '<Leader>o', '<Cmd>CocCommand explorer --sources=buffer+,file+ --position floating ~<CR>', { noremap = false, silent = true, desc = 'coc-explorer floating' })

-- 9) ToggleTerm トグル
--   ノーマル／挿入は常時、ターミナルは対象バッファ入室時のみ（元設定に準拠）
map('n', '<C-t>', function() cmd([[exe v:count1 . "ToggleTerm"]]) end, { noremap = true, silent = true, desc = 'ToggleTerm (v:count1 aware)' })
map('i', '<C-t>', [[<Esc><Cmd>exe v:count1 . "ToggleTerm"<CR>]], { noremap = true, silent = true, desc = 'ToggleTerm (insert)' })

-- TermEnter のときだけ、そのターミナルバッファにローカルマップを張る
local aug = vim.api.nvim_create_augroup('toggleterm_local_map', { clear = true })
vim.api.nvim_create_autocmd('TermEnter', {
  group = aug,
  pattern = 'term://*toggleterm#*',
  callback = function()
    -- このバッファ限定（buffer=true）で tnoremap <C-t>
    map('t', '<C-t>', function() cmd([[exe v:count1 . "ToggleTerm"]]) end,
      { noremap = true, silent = true, buffer = true, desc = 'ToggleTerm (terminal buffer local)' })
  end,
})

-- =========================
-- Leader
-- =========================
vim.g.mapleader = ' '

-- =========================
-- Plugins
-- =========================
-- lazy.nvim bootstrap installation
local lazypath = vim.fn.stdpath("data") .. "/lazy/lazy.nvim"
if not (vim.uv).fs_stat(lazypath) then
  vim.fn.system({
    "git",
    "clone",
    "--filter=blob:none",
    "https://github.com/folke/lazy.nvim.git",
    "--branch=stable", -- latest stable release
    lazypath,
  })
end
vopt.rtp:prepend(lazypath)

require("lazy").setup {

  { "cohama/lexima.vim", event = "InsertEnter" },

  {
    "raphamorim/lucario",
    priority = 1000,
    lazy = false,
    config = function()
      vim.cmd.colorscheme("lucario")
    end,
  },

  {
    "osyo-manga/vim-anzu",
    config = function()
      vim.keymap.set('n', 'n', '<Plug>(anzu-n-with-echo)', { silent = true, desc = 'anzu next match with echo' })
      vim.keymap.set('n', 'N', '<Plug>(anzu-N-with-echo)', { silent = true, desc = 'anzu prev match with echo' })
      vim.keymap.set('n', '*', '<Plug>(anzu-star)',        { silent = true, desc = 'anzu search *' })
      vim.keymap.set('n', '#', '<Plug>(anzu-sharp)',       { silent = true, desc = 'anzu search #' })
    end,
  },

  { "Shougo/context_filetype.vim" },

  {
    "vim-airline/vim-airline",
    dependencies = { "vim-airline/vim-airline-themes" },
    init = function()
      vim.g.airline_theme = "molokai"
    end,
  },

  { "tpope/vim-commentary" },

  {
    "majutsushi/tagbar",
    config = function()
      -- キーマップ
      vim.keymap.set('n', '<Leader>g', ':Tagbar<CR>', { noremap = true, silent = true, desc = 'Open Tagbar' })
      -- Tagbar 設定
      vim.g.tagbar_width = 30
      vim.g.tagbar_autoshowtag = 1
      -- Rust 用の Tagbar 設定
      vim.g.tagbar_type_rust = {
        ctagstype = 'rust',
        kinds = {
          'T:types,type definitions',
          'f:functions,function definitions',
          'g:enum,enumeration names',
          's:structure names',
          'm:modules,module names',
          'c:consts,static constants',
          't:traits',
          'i:impls,trait implementations',
        }
      }
    end,
  },

  { "thinca/vim-quickrun" },

  {
    "simeji/winresizer",
    init = function()
      vim.g.winresizer_vert_resize = 1
      vim.g.winresizer_horiz_resize = 1
    end,
  },

  {
    "mattn/sonictemplate-vim",
    init = function()
      vim.g.sonictemplate_vim_template_dir = { vim.fn.expand("~/.config/nvim/template") }
    end,
  },

  {
    "reireias/vim-cheatsheet",
    init = function()
      vim.g["cheatsheet#cheat_file"] = vim.fn.expand("~/.cheatsheet.md")
    end,
  },

  { "alvan/vim-closetag" },

  { "kana/vim-operator-user" },

  {
    "kana/vim-operator-replace",
    config = function()
      vim.keymap.set({ "n", "x" }, "R", "<Plug>(operator-replace)", { silent = true })
    end,
  },

  {
    "neoclide/coc.nvim",
    branch = "release",
    event = "InsertEnter",
    -- coc.nvim needs Node.js; build step depends on your env
    build = "yarn install --frozen-lockfile",
    config = function()
      -- statusline 末尾に CoC ステータスと現在関数名を追加
      vim.o.statusline = vim.o.statusline .. "%{coc#status()}%{get(b:,'coc_current_function','')}"

      local map = vim.keymap.set
      local cmd = vim.cmd
      local fn  = vim.fn
      local api = vim.api

      -- ---- ユーティリティ ----
      local function check_back_space()
        local col = fn.col('.') - 1
        if col == 0 then return true end
        local line = fn.getline('.')
        return line:sub(col, col):match('%s') ~= nil
      end

      local function show_documentation()
        local ft = vim.bo.filetype
        if ft == 'vim' or ft == 'help' then
          cmd('h ' .. fn.expand('<cword>'))
        else
          fn.CocAction('doHover')
        end
      end

      -- ---- 挿入モード補完操作 ----
      -- <Tab>: ポップアップ可視 → 次候補、直前が空白 → Tab 挿入、その他 → 補完トリガ
      map('i', '<Tab>', function()
        if fn.pumvisible() == 1 then
          return '<C-n>'
        elseif check_back_space() then
          return '<Tab>'
        else
          return fn['coc#refresh']()
        end
      end, { expr = true, silent = true, desc = 'CoC: Tab completion / trigger' })

      -- <S-Tab>: ポップアップ可視 → 前候補、不可視 → バックスペース
      map('i', '<S-Tab>', function()
        return (fn.pumvisible() == 1) and '<C-p>' or '<C-h>'
      end, { expr = true, silent = true, desc = 'CoC: Shift-Tab completion' })

      -- <C-Space>: 明示的に補完トリガ
      map('i', '<C-Space>', function()
        return fn['coc#refresh']()
      end, { expr = true, silent = true, desc = 'CoC: trigger completion' })

      -- <CR>: ポップアップ可視 → coc#_select_confirm()、不可視 → 改行 + on_enter()
      map('i', '<CR>', function()
        if fn.pumvisible() == 1 then
          return fn['coc#_select_confirm']()
        else
          return [[<C-g>u<CR><c-r>=coc#on_enter()<CR>]]
        end
      end, { expr = true, silent = true, desc = 'CoC: confirm or newline' })

      -- ---- 診断/定義/参照など ----
      map('n', '[g', '<Plug>(coc-diagnostic-prev)', { silent = true, desc = 'CoC: prev diagnostic' })
      map('n', ']g', '<Plug>(coc-diagnostic-next)', { silent = true, desc = 'CoC: next diagnostic' })
      map('n', 'gd', '<Plug>(coc-definition)',      { silent = true, desc = 'CoC: goto definition' })
      map('n', 'gy', '<Plug>(coc-type-definition)', { silent = true, desc = 'CoC: goto type definition' })
      map('n', 'gi', '<Plug>(coc-implementation)',  { silent = true, desc = 'CoC: goto implementation' })
      map('n', 'gr', '<Plug>(coc-references)',      { silent = true, desc = 'CoC: references' })

      -- K: ドキュメント表示（help/vim なら :help、それ以外は CoC hover）
      map('n', 'K', show_documentation, { silent = true, desc = 'CoC: hover / help' })

      -- リネーム / フォーマット / コードアクション / クイックフィックス
      map('n', '<leader>rn', '<Plug>(coc-rename)',             { silent = true, desc = 'CoC: rename symbol' })
      map('x', '<leader>f',  '<Plug>(coc-format-selected)',    { silent = true, desc = 'CoC: format selection' })
      map('n', '<leader>f',  '<Plug>(coc-format-selected)',    { silent = true, desc = 'CoC: format selection' })
      map('x', '<leader>a',  '<Plug>(coc-codeaction-selected)',{ silent = true, desc = 'CoC: code action (sel)' })
      map('n', '<leader>a',  '<Plug>(coc-codeaction-selected)',{ silent = true, desc = 'CoC: code action (sel)' })
      map('n', '<leader>ac', '<Plug>(coc-codeaction)',         { silent = true, desc = 'CoC: code action (cursor)' })
      map('n', '<leader>qf', '<Plug>(coc-fix-current)',        { silent = true, desc = 'CoC: quickfix current' })

      -- ---- :command 置き換え ----
      api.nvim_create_user_command('Format', function()
        fn.CocAction('format')
      end, { nargs = 0 })

      api.nvim_create_user_command('Fold', function(opts)
        -- :Fold または :Fold <level>
        if #opts.fargs > 0 then
          fn.CocAction('fold', opts.fargs[1])
        else
          fn.CocAction('fold')
        end
      end, { nargs = '?' })

      api.nvim_create_user_command('OR', function()
        fn.CocAction('runCommand', 'editor.action.organizeImport')
      end, { nargs = 0 })

      -- ---- autocmd ----
      -- カーソル停止時にシンボルハイライト
      api.nvim_create_autocmd('CursorHold', {
        pattern = '*',
        callback = function()
          fn.CocActionAsync('highlight')
        end,
      })

      -- filetype 別設定 & プレースホルダジャンプ時のシグネチャ
      local grp = api.nvim_create_augroup('mygroup', { clear = true })

      api.nvim_create_autocmd('FileType', {
        group = grp,
        pattern = { 'typescript', 'json' },
        callback = function()
          -- VimScript: setl formatexpr=CocAction('formatSelected')
          vim.bo.formatexpr = "CocAction('formatSelected')"
        end,
      })

      api.nvim_create_autocmd('User', {
        group = grp,
        pattern = 'CocJumpPlaceholder',
        callback = function()
          fn.CocActionAsync('showSignatureHelp')
        end,
      })
    end,
  },

  { "mechatroner/rainbow_csv" },

  { "lambdalisue/gina.vim" },

  {
    "skywind3000/vim-quickui",
    config = function()
      local fn  = vim.fn
      local cmd = vim.cmd
      local map = vim.keymap.set

      -- ---- CreateNewFile (VimScript関数のLua実装) ----
      local function CreateNewFile()
        local prompt = ("File(dir=%s): "):format(fn.getcwd())
        local f = fn.input(prompt)
        if #f > 0 then
          -- パスに空白などがある場合に備えて fnameescape
          cmd("tabe " .. fn.fnameescape(f))
        end
      end

      -- ---- quickui メニュー初期化 ----
      fn['quickui#menu#reset']()

      -- ---- &File ----
      fn['quickui#menu#install']("&File", {
        { "&Open\t(leader)o", 'CocCommand explorer --open-action-strategy tab --sources=buffer+,file+ --position floating' },
        { "&Save All\twa",    'wa!' },
        { "--",               '' },
        { "&Create New File", function() CreateNewFile() end }, -- 関数呼び出しをLuaで
        { "--",               '' },
        { "&Quit\tqa",        'qa!' },
      })

      -- ---- &View ----
      fn['quickui#menu#install']("&View", {
        { "Split Window &Vertical\t(leader)V", 'vs' },
        { "Split Window &Horizontal\t(leader)H", 'sp' },
        { "&Close Window \tclo", 'close' },
        { "&Move Window \tCtrl+w w", 'winc w' },
        { "--", '' },
        { "Resize window (&+5)\t:vertical resize +5", 'vertical resize +5' },
        { "Resize window (&-5)\t:vertical resize -5", 'vertical resize -5' },
        { "--", '' },
        { "&Function\t(leader)g", 'Tagbar' },
        { "&Explorer\t(leader)n", 'CocCommand explorer' },
        { "&Terminal\tCtrl+t", 'ToggleTerm' },
        { "--", '' },
        { "&Buffer List",   'call quickui#tools#list_buffer("e")' },
        { "F&unction List", 'call quickui#tools#list_function()' },
      })

      -- ---- &Edit ----
      fn['quickui#menu#install']("&Edit", {
        { "&Undo\tu", 'u' },
        { "--", '' },
        { "Go &Definition\tgd",          'call CocActionAsync("jumpDefinition")' },
        { "Go &Type\tgy",                'call CocActionAsync("jumpTypeDefinition")' },
        { "Go &Implementation\tgi",      'call CocActionAsync("jumpImplementation")' },
        { "Go &References\tgr",          'call CocActionAsync("jumpReferences")' },
        { "--", '' },
        { "Toggle &Comment\tgc(has range) or gcc", 'Commentary' },
        { "--", '' },
        { "R&ename Code\t(leader)rn", 'call CocActionAsync("rename")' },
        { "&Format Code\t(leader)f",  'call CocActionAsync("format")' },
        { "--", '' },
        { "&Grep\tCtrl+dG", 'Denite grep -buffer-name=search-buffer-denite' },
      })

      -- ---- &Debug ----
      -- 第3引数に '<auto>'、第4引数に filetype フィルタを渡せる
      fn['quickui#menu#install']("&Debug", {
        { "&Create Debug Settings", 'CreateVimspectorJson' },
        { "--", '' },
        { "&Start\t(F5)",            'call vimspector#Continue()' },
        { "&Reset\tShift+(F5)",      'call vimspector#Reset()' },
        { "Restart\tShift+Ctrl+(F5)",'call vimspector#Restart()' },
        { "&Pause\t(F6)",            'call vimspector#Pause()' },
        { "--", '' },
        { "Step &Over\t(F10)",       'call vimspector#StepOver()' },
        { "Step &Into\t(F11)",       'call vimspector#StepInto()' },
        { "Step Out\tShift+(F11)",   'call vimspector#StepOut()' },
        { "---", '' },
        { "&Breakpoint\t(F9)",       'call vimspector#ToggleBreakpoint()' },
      }, '<auto>', 'rust,python')

      -- ---- &Git ----
      fn['quickui#menu#install']("&Git", {
        { '&Add',     'Git add %' },
        { '&Commit',  'Git commit' },
        { '&Remove',  'Git rm' },
        { '&Push',    'Git push' },
        { 'P&ull',    'Git pull' },
        { '--', '' },
        { '&Status',  'Git status' },
        { '&Diff',    'Git diff' },
        { '&Grep',    'Git grep' },
        { '&Blame',   'Git blame' },
        { '--', '' },
        { 'B&ranch',  'Git branch' },
        { 'C&heckout','Git checkout' },
        { '&Merge',   'Git merge' },
      })

      -- ---- &Option ----
      fn['quickui#menu#install']("&Option", {
        { 'Set &Spell %{&spell? "Off":"On"}',           'set spell!' },
        { 'Set &Cursor Line %{&cursorline? "Off":"On"}','set cursorline!' },
        { 'Set &Paste %{&paste? "Off":"On"}',           'set paste!' },
      })

      -- ---- H&elp ----
      fn['quickui#menu#install']("H&elp", {
        { "&Cheatsheet",   'help index' },
        { "T&ips",         'help tips' },
        { '--',            '' },
        { "&Tutorial",     'help tutor' },
        { '&Quick Reference','help quickref' },
        { '&Summary',      'help summary' },
      })

      -- ---- quickui 外観オプション ----
      vim.g.quickui_show_tip     = 1
      vim.g.quickui_border_style = 2
      vim.g.quickui_color_scheme = 'papercol dark'

      -- ======================
      -- Context Menu (右クリック)
      -- ======================

      -- VimScriptの `let content = [...]` 相当（LuaテーブルでOK）
      local ctx_content = {
        { "&Grep Cursor Word", 'DeniteCursorWord grep -buffer-name=search-buffer-denite' },
        { '--', '' },
        { "To &Lower", 'silent normal vawu' },
        { "To &Upper", 'silent normal vawU' },
      }

      -- VimScriptの `let opts = {'index':g:quickui#context#cursor}`
      local ctx_opts = {
        index = vim.g['quickui#context#cursor'],  -- quickui が提供するカーソル位置
      }

      -- ラッパ関数（Lua側の配列/辞書を渡す）
      local function OpenQuickUIMenu()
        fn['quickui#menu#open']()
      end

      local function OpenQuickUIContext()
        fn['quickui#context#open'](ctx_content, ctx_opts)
      end

      -- マッピング（スペース二回、右クリック）
      map('n', '<Space><Space>', OpenQuickUIMenu, { noremap = true, silent = true, desc = 'QuickUI: open menu' })
      map('n', '<RightMouse>', OpenQuickUIContext,{ noremap = true, silent = true, desc = 'QuickUI: open context menu' })
    end,
  },

  {
    "rust-lang/rust.vim",
    init = function()
      vim.g.rustfmt_autosave = 1
    end,
  },

  { "airblade/vim-gitgutter" },

  { "tpope/vim-fugitive" },

  {
    "petertriho/nvim-scrollbar",
    config = function()
      require("scrollbar").setup({
          handle = {
              color = "#292e42",
          },
          marks = {
            Search = { color = "#ff9e64" },
            Error = { color = "#db4b4b" },
            Warn = { color = "#e0af68" },
            Info = { color = "#0db9d7" },
            Hint = { color = "#1abc9c" },
            Misc = { color = "#9d7cd8" },
            GitAdd = { text = "+", color="#ffffff" },
            GitChange = { text = "~", color="#ffffff" },
            GitDelete = { text = "-", color="#ffffff" },
        }
      })
    end,
  },

  {
    "akinsho/toggleterm.nvim",
    version = "*",
    config = function()
      require("toggleterm").setup()
    end,
  },

  {
    "puremourning/vimspector",
    ft = { "python", "go", "c", "cpp", "rust" },
    build = "./install_gadget.py --enable-c --enable-python --enable-go --force-enable-rust",
    config = function()
      -- 使用するアダプタ
      vim.g.vimspector_install_gadgets = { 'debugpy', 'CodeLLDB' }

      local fn  = vim.fn
      local api = vim.api
      local map = vim.keymap.set

      -- --------------------------------
      -- .vimspector.json 自動生成関数
      -- --------------------------------
      local function create_vimspector_json()
        -- VimScript: if !has('unix') | return 1 | endif
        if fn.has('unix') ~= 1 then
          return 1
        end

        local ext  = fn.expand('%:e')
        local file = fn.expand('%:p')

        if ext == 'rs' then
          -- Rust: プロジェクトルートを src の手前まで辿る
          local cmdlst  = {}
          local pathlst = vim.split(file, '/', { plain = true })
          for _, item in ipairs(pathlst) do
            if item == 'src' then break end
            table.insert(cmdlst, item)
          end

          if #cmdlst > 1 then
            local root = '/' .. table.concat(cmdlst, '/')
            local json = root .. '/.vimspector.json'
            local exe  = root .. '/target/debug/' .. cmdlst[#cmdlst]

            if fn.filereadable(json) == 0 then
              local lines = {
                '{',
                '  "configurations": {',
                '    "launch": {',
                '      "adapter": "CodeLLDB",',
                '      "configuration": {',
                '        "request": "launch",',
                string.format('        "program": "%s"', exe),
                '      }',
                '    }',
                '  }',
                '}',
              }
              fn.writefile(lines, json)
            end
          end

        elseif ext == 'py' then
          -- Python: カレントファイルのディレクトリに生成
          local root = fn.fnamemodify(file, ':p:h')
          local json = root .. '/.vimspector.json'
          if fn.filereadable(json) == 0 then
            local lines = {
              '{',
              '  "configurations": {',
              '    "Python_Launch": {',
              '      "adapter": "debugpy",',
              '      "configuration": {',
              '        "name": "Python_Launch",',
              '        "type": "python",',
              '        "request": "launch",',
              '        "cwd": "${fileDirname}",',
              '        "python": "python3",',
              '        "stopOnEntry": true,',
              '        "console": "externalTerminal",',
              '        "debugOptions": [],',
              '        "program": "${file}"',
              '      }',
              '    }',
              '  }',
              '}',
            }
            fn.writefile(lines, json)
          end

        else
          vim.notify('Not compatible !', vim.log.levels.WARN)
        end
      end

      -- :CreateVimspectorJson コマンド
      api.nvim_create_user_command('CreateVimspectorJson', create_vimspector_json, {})

      -- -------------
      -- キーマップ群
      -- -------------
      -- Breakpoint
      map('n', '<F9>',      '<Plug>VimspectorToggleBreakpoint',      { silent = true, desc = 'Toggle Breakpoint' })
      map('x', '<F9>',      '<Plug>VimspectorToggleBreakpoint',      { silent = true, desc = 'Toggle Breakpoint (visual)' })
      map('n', '<S-F9>',    '<Plug>VimspectorAddFunctionBreakpoint', { silent = true, desc = 'Add Function Breakpoint' })
      map('x', '<S-F9>',    '<Plug>VimspectorAddFunctionBreakpoint', { silent = true, desc = 'Add Function Breakpoint (visual)' })

      -- Step
      map('n', '<F10>',     '<Plug>VimspectorStepOver', { silent = true, desc = 'Step Over' })
      map('x', '<F10>',     '<Plug>VimspectorStepOver', { silent = true, desc = 'Step Over (visual)' })
      map('n', '<F11>',     '<Plug>VimspectorStepInto', { silent = true, desc = 'Step Into' })
      map('x', '<F11>',     '<Plug>VimspectorStepInto', { silent = true, desc = 'Step Into (visual)' })
      map('n', '<S-F11>',   '<Plug>VimspectorStepOut',  { silent = true, desc = 'Step Out' })
      map('x', '<S-F11>',   '<Plug>VimspectorStepOut',  { silent = true, desc = 'Step Out (visual)' })

      -- Run / Continue / Reset / Restart / Pause
      -- F5: まず設定ファイル生成 → Continue
      map('n', '<F5>',      '<Cmd>CreateVimspectorJson<CR><Plug>VimspectorContinue', { silent = true, desc = 'Generate config & Continue' })
      map('x', '<F5>',      '<Cmd>CreateVimspectorJson<CR><Plug>VimspectorContinue', { silent = true, desc = 'Generate config & Continue (visual)' })
      map('n', '<S-F5>',    '<Cmd>VimspectorReset<CR>',   { silent = true, desc = 'Reset' })
      map('x', '<S-F5>',    '<Cmd>VimspectorReset<CR>',   { silent = true, desc = 'Reset (visual)' })
      map('n', '<S-C-F5>',  '<Plug>VimspectorRestart',    { silent = true, desc = 'Restart' })
      map('x', '<S-C-F5>',  '<Plug>VimspectorRestart',    { silent = true, desc = 'Restart (visual)' })
      map('n', '<F6>',      '<Plug>VimspectorPause',      { silent = true, desc = 'Pause' })
      map('x', '<F6>',      '<Plug>VimspectorPause',      { silent = true, desc = 'Pause (visual)' })
    end,
  },
}
