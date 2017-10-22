@echo off
set FBT_COMMAND=%~dp0bin/FlatBuildTool.exe--
if exist %FBT_COMMAND% (
%~dp0bin/FlatBuildTool.exe %*
) else (
python %~dp0src/FlatBuildTool.py %*
)
