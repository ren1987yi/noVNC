# 放在 noVNC 根目录或当前工作目录
import re
import logging
import os

# 兼容不同版本 websockify：找不到 BaseTokenPlugin 时提供最小基类
try:
    from websockify.token_plugins import BaseTokenPlugin as _WSBBase
except Exception:
    try:
        # 某些版本可能叫 TokenPlugin 或 BasePlugin
        from websockify.token_plugins import TokenPlugin as _WSBBase
    except Exception:
        try:
            from websockify.token_plugins import BasePlugin as _WSBBase
        except Exception:
            class _WSBBase:
                def __init__(self, src):
                    pass

# Logger 设置
_logger = logging.getLogger("param_token_plugin")
if not _logger.handlers:
    _handler = logging.StreamHandler()
    _fmt = logging.Formatter("[%(asctime)s] %(levelname)s param_token_plugin: %(message)s")
    _handler.setFormatter(_fmt)
    _logger.addHandler(_handler)
# 支持通过环境变量控制日志级别，默认 INFO；例如：set PARAM_TOKEN_PLUGIN_LOG=DEBUG
_level_name = os.environ.get("PARAM_TOKEN_PLUGIN_LOG", "INFO").upper()
_logger.setLevel(getattr(logging, _level_name, logging.INFO))

_IPV4_RE = re.compile(r"^(?:\d{1,3}\.){3}\d{1,3}$")
_HOST_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9\.-]{0,253}[A-Za-z0-9]$")

def _is_host(s: str) -> bool:
    if _IPV4_RE.match(s):
        parts = s.split(".")
        try:
            ok = all(0 <= int(p) <= 255 for p in parts)
            _logger.debug(f"IPv4 校验: {s} -> {ok}")
            return ok
        except ValueError:
            _logger.debug(f"IPv4 片段非数字: {s}")
            return False
    m = _HOST_RE.match(s) is not None
    _logger.debug(f"主机名正则校验: {s} -> {m}")
    return m

class ParamTokenPlugin(_WSBBase):
    """
    仅支持 token 为 "host:port" 的直连形式。
    --token-plugin "param_token_plugin:ParamTokenPlugin"
    例如：
      token=192.168.0.50:5901 -> 直连
    """
    def __init__(self, src):
        super().__init__(src)
        _logger.info("ParamTokenPlugin 已初始化（仅支持 host:port）")
        _logger.debug(f"--token-source 原样传入: {src!r}")

    def lookup(self, token):
        _logger.info(f"收到 token: {token!r}")
        if not token:
            _logger.warning("token 为空")
            return None

        t = token.strip()
        if ":" not in t:
            _logger.warning(f"token 缺少端口分隔符: {t!r}")
            return None

        host, port = t.rsplit(":", 1)
        host, port = host.strip(), port.strip()
        _logger.debug(f"解析得到 host={host!r}, port={port!r}")

        if not _is_host(host):
            _logger.warning(f"非法 host: {host!r}")
            return None

        try:
            port_i = int(port)
        except ValueError:
            _logger.warning(f"端口非数字: {port!r}")
            return None

        if not (0 < port_i < 65536):
            _logger.warning(f"端口越界: {port_i}")
            return None

        _logger.info(f"解析成功 -> ({host}, {port_i})")
        return (host, port_i)

