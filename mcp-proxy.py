#!/usr/bin/env python3
"""
麦麦创贴 · 本地 MCP 代理 (mcp-proxy.py)
=====================================
为什么需要它：
  麦当劳 MCP 服务器 (https://mcp.mcd.cn) 不返回 CORS 头，浏览器里的网页
  无法直接 fetch 它（预检会被 403 拒绝）。本代理在 127.0.0.1 起一个本地
  服务：既托管 HTML，又把 /mcp 转发给麦当劳 MCP，并在服务端注入 Token。
  这样网页通过同源 http://127.0.0.1:<port>/mcp 调用，彻底绕过 CORS，
  且 Token 始终留在服务端，不会进客户端代码（符合比赛合规要求）。

运行：
  python3 mcp-proxy.py
  # 然后浏览器打开 http://127.0.0.1:8787

Token 来源（按优先级）：
  1) 环境变量 MCD_MCP_TOKEN
  2) ~/.workbuddy/mcp.json 里的 mcd-mcp.headers.Authorization
（两者都是本机本地文件/环境变量，绝不会进入要提交的仓库）
"""
import http.server
import socketserver
import urllib.request
import urllib.error
import json
import os

PORT = int(os.environ.get("MCP_PROXY_PORT", "8787"))
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
HTML_FILE = os.environ.get(
    "MCP_PROXY_HTML",
    os.path.join(SCRIPT_DIR, "mcd-cuptez.html"),
)
MCP_URL = "https://mcp.mcd.cn"


def load_token():
    tok = os.environ.get("MCD_MCP_TOKEN")
    if tok:
        return tok.strip()
    try:
        cfg = json.load(open(os.path.expanduser("~/.workbuddy/mcp.json"), encoding="utf-8"))
        auth = cfg["mcpServers"]["mcd-mcp"]["headers"]["Authorization"]
        return auth.replace("Bearer ", "").strip()
    except Exception as e:  # noqa
        print("⚠️  未能读取 MCP Token，请设置 MCD_MCP_TOKEN 或确认 ~/.workbuddy/mcp.json 存在")
        return ""


TOKEN = load_token()


class Handler(http.server.BaseHTTPRequestHandler):
    def _send(self, code, body, ctype="application/json", extra=None):
        if isinstance(body, str):
            body = body.encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        if extra:
            for k, v in extra.items():
                self.send_header(k, v)
        self.end_headers()
        if body:
            self.wfile.write(body)

    def do_GET(self):
        path = self.path.split("?", 1)[0]
        if path in ("/", "/index.html"):
            try:
                data = open(HTML_FILE, "rb").read()
            except Exception as e:  # noqa
                self._send(404, f"HTML 未找到: {e}", ctype="text/plain")
                return
            self._send(200, data, ctype="text/html; charset=utf-8")
            return
        fp = os.path.normpath(os.path.join(SCRIPT_DIR, path.lstrip("/")))
        if os.path.isfile(fp) and os.path.dirname(fp) == SCRIPT_DIR:
            with open(fp, "rb") as f:
                self._send(200, f.read(), ctype="application/octet-stream")
        else:
            self._send(404, "not found", ctype="text/plain")

    def do_POST(self):
        if self.path.split("?", 1)[0].rstrip("/") != "/mcp":
            self._send(404, "only /mcp is proxied", ctype="text/plain")
            return
        try:
            length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(length) if length else b"{}"
        except Exception:  # noqa
            self._send(400, "bad request", ctype="text/plain")
            return
        req = urllib.request.Request(MCP_URL, data=body, method="POST")
        req.add_header("Content-Type", self.headers.get("Content-Type", "application/json"))
        req.add_header("Accept", "application/json, text/event-stream")
        if TOKEN:
            req.add_header("Authorization", "Bearer " + TOKEN)
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                data = resp.read()
                ctype = resp.headers.get("Content-Type", "application/json")
                self._send(resp.status, data, ctype=ctype,
                           extra={"Access-Control-Allow-Origin": "*"})
        except urllib.error.HTTPError as e:
            self._send(e.code, e.read(), ctype="application/json")
        except Exception as e:  # noqa
            self._send(502, json.dumps({"error": str(e)}), ctype="application/json")

    def log_message(self, *args):  # 静默
        pass


if __name__ == "__main__":
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(("127.0.0.1", PORT), Handler) as httpd:
        print(f"✅ 麦麦创贴 MCP 代理已启动")
        print(f"   打开:      http://127.0.0.1:{PORT}")
        print(f"   代理 HTML: {HTML_FILE}")
        print(f"   Token:     {'已加载' if TOKEN else '⚠️ 缺失'}")
        print(f"   转发目标:  {MCP_URL}")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n已停止")
