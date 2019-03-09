@echo off
set FBT_COMMAND=%~dp0bin/flmake.exe
if exist %FBT_COMMAND% (
%FBT_COMMAND% %*
) else (
python %~dp0src/FlatBuildTool.py %*
)
