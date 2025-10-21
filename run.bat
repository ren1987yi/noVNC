@echo off
REM 将脚本所在目录加入 PYTHONPATH，保证能找到 param_token_plugin.py
set "PYTHONPATH=%~dp0"

REM 切换到脚本目录
cd /d "%~dp0"

REM 如需 HTTPS，可增加 --cert/--key
REM 监听 6080，把 token 交给 ParamTokenPlugin 解析

REM 启动直接进主页
start "" "http://127.0.0.1:6080"

set PARAM_TOKEN_PLUGIN_LOG=DEBUG
python -m websockify --web . 6080 --token-plugin "param_token_plugin.ParamTokenPlugin"

REM 可选：自动打开浏览器（取消下一行前面的 REM 即可）