# 部署公网 MCP 代理（让在线版脱离本地 mcp-proxy.py）

GitHub Pages / CloudStudio 等静态托管**无法运行后端**，浏览器也因 CORS 无法直接访问 `mcp.mcd.cn`。
因此在线版需要一个**公网 serverless 代理**：替浏览器持有 Token 并转发、附加 CORS 头。
Token 只存在于服务端 Secret，**绝不进入客户端代码或仓库**，符合比赛安全要求。

推荐 **Cloudflare Workers**（免费、无需安装 CLI，Dashboard 粘贴即可）。

---

## 方式 A：Cloudflare Dashboard（无需 CLI，约 2 分钟）

1. 打开 https://dash.cloudflare.com/ 并登录（无账号用邮箱注册，免费）。
2. 左侧 **Workers & Pages → Create → Create Worker**。
3. 名称输入 `mcd-mcp-proxy`，把编辑器里的默认代码**全部替换为** `worker.js` 的内容。
4. 点 **Deploy**。
5. 进入该 Worker → **Settings → Variables → Add**，
   - Variable name：`MCD_MCP_TOKEN`
   - Type 选 **Secret**（不是 Text）
   - Value：你的麦当劳 MCP Token（`open.mcd.cn/mcp` 申请）
   - 保存。
6. 回到 Worker 概览，复制你的地址，形如 `https://mcd-mcp-proxy.<你的子域>.workers.dev`。
7. 打开仓库根目录 `config.js`，把地址填入：
   ```js
   window.MCP_PROXY_URL = "https://mcd-mcp-proxy.<你的子域>.workers.dev";
   ```
   提交并推送。之后 `https://jzcreative.github.io/mcd-cuptez/mcd-cuptez.html` 即完整在线联动。

> 也可不改动 `config.js`，直接在链接后加 `?proxy=https://mcd-mcp-proxy.xxx.workers.dev` 临时指定。

---

## 方式 B：Wrangler CLI（如已安装并 `wrangler login`）

```bash
cd deploy
wrangler secret put MCD_MCP_TOKEN      # 交互输入 Token
wrangler deploy                          # 部署，输出公网地址
# 将输出的地址填入仓库根目录 config.js 的 window.MCP_PROXY_URL
```

---

## 方式 C：Vercel / Netlify / 腾讯云函数（任选）

核心逻辑一致：一个接收 `POST /mcp` 的函数，服务端注入 Bearer Token 转发至
`https://mcp.mcd.cn`，回包加 `Access-Control-Allow-Origin: *`。
可据平台文档把 `worker.js` 改写为对应运行时（Node / Python 均可）。

- **Vercel**：`api/mcp.js`（Node）导出默认 handler，Token 存于项目 Environment Variables。
- **Netlify**：`netlify/functions/mcp.js` + `netlify.toml`，Token 存于 Site env。
- **腾讯云 SCF / 阿里云 FC**：函数计算 + API 网关，Token 存于函数环境变量（Secret）。

---

## 验证

部署后，浏览器打开在线版，开屏应自动同步当期活动（如「麦当劳 X PEACEMINUSONE」），
官方主题贴纸包动态命名并显示真实活动贴纸——即代表代理已生效。
如仅显示静态占位，请检查：Worker 地址是否填对、Secret 是否设置、Worker 路径是否为 `/mcp`。
