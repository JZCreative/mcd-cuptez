# 麦麦创贴 · 快乐，由你来贴

> 基于 **麦当劳中国 MCP（mcd-mcp）** 能力的个性化杯贴创作工具：在可口可乐杯 / 麦旋风 / McCafé / 薯条盒等 3D 容器上自由创作，并随时调用艺术家预置贴纸提质。当期活动主题经 `campaign-calendar` 真实注入官方贴纸包，创作可经订单备注闭环到真实点单场景。另附**免后端快速浏览版**，方便直接在线体验。

本仓库为「麦当劳程序员创意开发大赛」参赛项目。

🌐 **在线快速浏览（GitHub Pages，免后端）**：https://jzcreative.github.io/mcd-cuptez/
🌐 **真实 MCP 体验**：本地运行 `python3 mcp-proxy.py` 后打开 http://127.0.0.1:8787

---

## 一、项目简介

「麦麦创贴」把茶饮品牌流行的「手绘杯贴」玩法，合理迁移到麦当劳更丰富的包装载体上：

- **用户自由创作为主**：开屏即空白 3D 容器，画笔 / 文字 / 形状完全由用户掌控，不预设任何模板。
- **艺术家贴纸随时调用**：内置透明贴纸资产（线条童趣 / 波普 / 极简几何 / 星夜线等风格），点击即叠加、可拖动、可撤除——**调用时机完全由用户决定**，不用时就是纯手绘。
- **当期主题真实联动**：主版本经麦当劳 MCP `campaign-calendar` 自动注入「官方主题」贴纸包，创作更「应景」；另提供**免后端快速浏览版**（内置虚拟当期活动）供 GitHub Pages 直接打开，开箱即完整体验。

与喜茶杯贴的本质区别：**你随便画，但随时能一键调用艺术家贴纸来提质**——自由是默认，资产是加成。

---

## 二、核心特性

| 特性 | 说明 |
|---|---|
| 3D 容器画布 | 四款容器（可乐杯 / 麦旋风 / McCafé / 薯条盒）真实 3D 模型，支持旋转、移动、缩放 |
| 自由创作 | 画笔（多色）、文字（点哪写哪）、橡皮点删、撤销、清空 |
| 艺术家预置资产 | 多风格透明贴纸包，随时叠加 / 移除 / 拖动 |
| 当期主题联动 | 主版本经 `campaign-calendar` 注入真实当期活动贴纸包；快速浏览版内置虚拟当期活动 |
| 双格式导出 | 导出当前视角 PNG（2× 栅格）/ 正面设计矢量源（SVG） |
| 订单备注 / 下单 | 主版本经 `create-order.remark` 写入真实点单备注（人工确认）；快速浏览版仅本机保存 |
| 单文件离线 | 主程序 `mcd-cuptez.html` 资产全内联（three.js / GLTFLoader / DRACO），无需联网 / 构建；MCP 调用经本地或公网代理 |

---

## 三、目录结构

```
.
├── mcd-cuptez.html            # 主程序：单文件 3D 创作原型，真实接入麦当劳 MCP（经 mcp-proxy.py / 公网代理）
├── mcd-cuptez.standalone.html  # 免后端快速浏览版：内置虚拟当期活动，GitHub Pages 直接打开即用，不调 MCP
├── mcp-proxy.py              # 本地 MCP 代理：托管页面并转发 /mcp，使浏览器绕过 CORS 真实调用麦当劳 MCP
├── config.js                 # 公网 MCP 代理地址（window.MCP_PROXY_URL）；留空则走本地 /mcp
├── deploy/                   # 公网 serverless 代理（Cloudflare Worker 等）部署脚本与说明
├── README.md                 # 本文件
├── CONTEST_DECLARATION.md    # 参赛声明（官方模板，内容不可改）
├── MCP_INTEGRATION.md        # MCP 集成说明（Server / Tools / 流程 / 状态）
├── mcp-config.example.json   # 脱敏 MCP 配置（仅环境变量占位符）
├── workbuddy.md              # WorkBuddy 对话上下文（参赛 WB 专项奖励用）
├── mcd-mcp-dev-rules.md      # 麦当劳 MCP 接入与开发规则手册（开发参考）
├── mcd-cuptez-design.md      # 调研分析与开发方案（背景资料）
└── (可选) assets/            # 源码级 3D / UI 资产（见下方「资产来源」）
```

> **源码资产来源**：3D 容器模型与 UI 资产位于
> `/Users/jiyutao/.codex/.chatgpt-projects/g-p-6aa3bac82d5c8191b97e3ce4b97b240e/output`
> 下的 `mcd-cup-assets/`（glb / stl / previews / source 构建脚本）与 `mcd-ui/`（art-assets 透明贴纸、qa 校验脚本）。
> 主程序已内联全部资产、可独立运行；如需再生成/替换资产，可将上述目录复制进仓库 `assets/` 目录。

---

## 四、安装与运行

### 方式 A：本地代理运行（**真实接入麦当劳 MCP**，推荐用于参赛演示）

> mcp.mcd.cn 不返回 CORS 头，普通静态服务器（如 `python3 -m http.server`）**无法**让网页真正调用 MCP。必须通过随附的 `mcp-proxy.py` 代理。

```bash
# 在仓库目录下执行（需能访问 mcp.mcd.cn，且本机 ~/.workbuddy/mcp.json 含 Token，或设了 MCD_MCP_TOKEN）
python3 mcp-proxy.py
# 浏览器打开 http://127.0.0.1:8787
```

代理会托管页面并把同源 `/mcp` 请求转发到 `https://mcp.mcd.cn`，**Token 由服务端注入，不进入客户端代码**。加载即真实拉取当期活动并注入官方主题贴纸，可经订单备注发起真实点单。可用环境变量 `MCP_PROXY_PORT` 改端口、`MCD_MCP_TOKEN` 显式指定 Token。

### 方式 B：GitHub Pages 在线快速浏览（**免后端虚拟体验**）

- **在线地址**：https://jzcreative.github.io/mcd-cuptez/ → 打开即 `mcd-cuptez.standalone.html` 快速浏览版。
- 由 GitHub Pages 静态托管，**内置虚拟当期活动**，完整 UI、3D 容器、自由创作、艺术家贴纸与导出均可用，开箱即完整体验、**不依赖任何服务端、不调用 MCP**——专为快速浏览与分享设计。
- 该版不能真实拉取当期活动或下单；如需真实 MCP 能力，请按方式 A / 方式 C 在本地运行主版本。

### 方式 C：直接打开（离线降级）

`mcd-cuptez.html` 双击打开亦可运行（资产已内联），但 `file://` 下浏览器无法跨域访问 `mcp.mcd.cn`，会**自动降级**使用内置虚拟当期活动；要真实接入 MCP，务必经方式 A 的 `mcp-proxy.py` 打开。

### 方式 D：公网代理（**真实联动，脱离本地**）

GitHub Pages 静态托管无法代理 MCP。办法是再部署一个**公网 serverless 代理**（推荐 Cloudflare Worker，约 2 分钟，Token 存为 Secret 不进代码），详见 [`deploy/DEPLOY.md`](./deploy/DEPLOY.md)。部署后把 Worker 地址填入根目录 `config.js` 的 `window.MCP_PROXY_URL`，在线主版本即自动同步真实当期活动、注入官方主题贴纸、支持订单备注闭环——**全程无需你的本地 `mcp-proxy.py`**。

---

## 五、配置麦当劳 MCP（主版本真实接入）

1. 前往 `open.mcd.cn/mcp` 用手机号登录并申请 **MCP Token**。
2. 主版本通过 `mcp-proxy.py` 读取 Token：默认从 `~/.workbuddy/mcp.json` 的 `mcd-mcp.headers.Authorization` 读取，也可用环境变量 `MCD_MCP_TOKEN` 显式指定。**Token 仅留在本机 / 代理服务端，不进入任何仓库文件。**
3. 运行 `python3 mcp-proxy.py` 后打开 `http://127.0.0.1:8787`，应用内即真实调用 `campaign-calendar` / `now-time-info` 并注入官方主题；若未运行代理，页面自动降级为内置虚拟当期活动，体验不受影响。

> 详情见 [`MCP_INTEGRATION.md`](./MCP_INTEGRATION.md) 与 [`mcd-mcp-dev-rules.md`](./mcd-mcp-dev-rules.md)。

---

## 六、使用示例（主版本）

1. 打开 `mcd-cuptez.html`（经 `mcp-proxy.py`），默认进入「可乐杯」空白 3D 画布。
2. 横滑切换杯型（麦旋风 / McCafé / 薯条盒）。
3. 用画笔自由涂鸦，或用文字工具写下口号。
4. 点底部「贴纸」唤起抽屉，点一张艺术家贴纸——想提质时点，不想用就纯手绘。
5. 点「导出图」：保存当前视角 PNG 与正面设计 SVG。
6. （主版本）点「写订单备注」→ 确认后经麦当劳 MCP `create-order.remark` 写入真实点单备注；快速浏览版仅本机保存。

---

## 七、目标用户

- 麦当劳爱好者、Z 世代年轻消费者（表达欲 / 归属感 / 社交货币）。
- 内容创作者、小红书 / 抖音玩家（个性化杯贴即拍照分享素材）。
- 想做个性化杯贴但不善画的用户（艺术家预置资产替代「代画」）。
- 开发者（参考麦当劳 MCP 的真实集成范式）。

---

## 八、合规与声明

- 本项目为参赛作品，由开发者独立开发，**非麦当劳官方产品**；餐品信息、价格、供应状态以麦当劳官方渠道实时结果为准。
- 遵守《麦当劳程序员节创意开发大赛活动规则》《麦当劳 MCP 服务规则》《WorkBuddy 软件许可及服务协议》。
- 参赛声明见 [`CONTEST_DECLARATION.md`](./CONTEST_DECLARATION.md)；MCP 集成与合规见 [`MCP_INTEGRATION.md`](./MCP_INTEGRATION.md)。

---

## 九、报名（Issue 格式）

在本活动仓库下发布 Issue（标题与正文之间、项目地址均**不使用 Markdown 格式**）：

```
【参赛申请】
项目名称：麦麦创贴 · 快乐，由你来贴
项目地址：https://github.com/<你的账号>/<仓库名>
项目简介：基于麦当劳 MCP 的个性化杯贴创作工具——在 3D 容器上自由创作并随时调用艺术家贴纸，当期活动主题自动注入官方贴纸包，创作可经订单备注闭环到点单。
```

> 报名详细约束见活动仓库 `README.md` / `activityGuidelines.md`。仓库须为 **Public**，项目创建时间须在 **2025-12-25 ~ 2026-10-25** 之间。
