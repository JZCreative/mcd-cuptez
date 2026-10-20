/**
 * 麦当劳 MCP 公网代理（Cloudflare Worker）
 * ---------------------------------------------------------------
 * 浏览器无法直连 mcp.mcd.cn（无 CORS 头），本 Worker 作为公网代理：
 *   - 接收浏览器同源/跨域的 POST /mcp
 *   - 服务端注入 Bearer Token（存于 Worker Secret，绝不进入客户端代码）
 *   - 转发至 https://mcp.mcd.cn
 *   - 回包附加 CORS 头，使浏览器可读取
 *
 * Token 通过 Secret 注入（见 DEPLOY.md），不要写进本文件或提交仓库。
 */
export default {
  async fetch(request, env) {
    const url = new URL(request.url);

    // CORS 预检
    if (request.method === 'OPTIONS') {
      return new Response(null, { status: 204, headers: corsHeaders() });
    }

    if (url.pathname !== '/mcp') {
      return new Response('Not Found', { status: 404 });
    }
    if (request.method !== 'POST') {
      return new Response('Method Not Allowed', { status: 405 });
    }

    const token = env.MCD_MCP_TOKEN;
    if (!token) {
      return new Response('Server misconfigured: missing MCD_MCP_TOKEN secret', { status: 500 });
    }

    const upstream = await fetch('https://mcp.mcd.cn', {
      method: 'POST',
      headers: {
        'Authorization': 'Bearer ' + token,
        'Content-Type': 'application/json',
        'Accept': 'application/json, text/event-stream'
      },
      body: request.body,
      duplex: 'half'
    });

    const headers = new Headers(upstream.headers);
    for (const [k, v] of Object.entries(corsHeaders())) headers.set(k, v);
    return new Response(upstream.body, { status: upstream.status, headers });
  }
};

function corsHeaders() {
  return {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Headers': 'content-type, accept, authorization',
    'Access-Control-Allow-Methods': 'POST, OPTIONS'
  };
}
