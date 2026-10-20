/* 在线版 MCP 代理地址配置
 * ---------------------------------------------------------------
 * 本地开发：保持为空即可，应用会自动走同源 /mcp（由 mcp-proxy.py 提供）。
 * 在线部署：把下面引号内填上你部署好的公网代理地址，例如：
 *   window.MCP_PROXY_URL = "https://mcd-mcp-proxy.xxx.workers.dev";
 * 部署方法见 deploy/DEPLOY.md（推荐 Cloudflare Worker，2 分钟，token 存为密钥，不进代码）。
 * 也可临时用 URL 参数覆盖：.../mcd-cuptez.html?proxy=https://你的代理地址
 */
window.MCP_PROXY_URL = "";
