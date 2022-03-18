@echo off

set WXBUILDER="D:\Program Files\wxFormBuilder\wxFormBuilder.exe"

python %~d0%~p0wxformbuilder.py %1 %WXBUILDER%
