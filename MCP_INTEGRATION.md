# MCP 集成说明（MCP_INTEGRATION）

> 本文件说明「麦麦创贴」如何真实使用 **麦当劳中国 MCP Server（mcd-mcp）** 的能力。
> 接入配置见 [`mcp-config.example.json`](./mcp-config.example.json)；MCP 服务规则与工具清单见 [`mcd-mcp-dev-rules.md`](./mcd-mcp-dev-rules.md)。

---

## 1. 使用的 MCP Server

| 项目 | 值 |
|---|---|
| Server 名称 | `mcd-mcp`（麦当劳中国 MCP Server） |
| 协议 | Streamable HTTP |
| Endpoint | `https://mcp.mcd.cn` |
| 认证 | 请求头 `Authorization: Bearer <MCP_TOKEN>` |
| 会话机制 | 无状态（仅凭 Token 识别用户，无需维护 `Mcp-Session-Id`） |
| 工具总数 | 运行时 `tools/list` 实测 **35 个**（以运行时为准） |

Token 通过 WorkBuddy 自定义连接器（`mcd-mcp`）注入，**不写入任何代码或提交仓库**，仅以环境变量占位符 `MCD_MCP_TOKEN` 出现在脱敏配置中。

---

## 2. 实际调用的工具（Tools）

本项目按「用户自由创作为主、艺术家贴纸随时调用」的设计，将以下麦当劳 MCP 工具织入创作流程：

| 工具 | 用途 | 调用性质 | 业务价值 |
|---|---|---|---|
| `campaign-calendar` | 拉取**当期活动主题** → 自动注入「官方主题」贴纸包到贴纸抽屉 | 只读 | 让创作「应景」，把官方营销节点变成可用的创作资产 |
| `query-meals` / `query-meal-detail` | 查询套餐/单品信息与特制项（`modification`/`withOrder`） | 只读 | 为用户提供「套餐 → 杯贴主题」的匹配建议 |
| `query-nearby-stores` | 查询附近门店（城市/经纬度） | 只读 | 提供门店上下文，支撑「就近门店」类创作文案 |
| `now-time-info` | 获取当前时间 | 只读 | 导出图时间戳水印，证明创作时点 |
| `create-order`（仅 `remark` 字段） | 将「定制意图 / 定制码」写入订单备注（≤50 字） | 写操作（**仅备注级**） | 创作闭环到真实点单，且**不改订单商品/金额**，安全 |

### 写操作安全约束（必须遵守）

`create-order` 等写操作**绝不自动执行**，必须：
1. 在 UI 中显式展示将要写入的 `remark` 内容；
2. 经用户人工确认（点击「写订单备注」并二次确认）后才发起；
3. 且仅写入 `remark` 备注字段，不改动商品、数量、价格，不产生额外费用。

> 严禁自动调用的写操作（来自 `mcd-mcp-dev-rules.md`）：`create-order`、`cancel-order`、`delivery-create-address`、`auto-bind-coupons`、`mall-create-order`、`draw-lottery`、`party-order-create`。本项目仅以「备注级」方式使用 `create-order`，且强制人工确认。

---

## 3. 调用流程（Call Flow）

```
[用户] 打开麦麦创贴 → 选择杯型 → 自由创作（画笔/文字/艺术家贴纸）
   │
   ├─(1) 应用经 mcd-mcp 连接器调用  campaign-calendar
   │        └─> 当期活动主题 → 注入「官方主题」贴纸包（贴纸抽屉新增 tab）
   │
   ├─(2) 可选：query-meals / query-nearby-stores
   │        └─> 套餐/门店上下文 → 推荐创作方向（仅建议，不强制）
   │
   ├─(3) 导出：now-time-info → 时间戳水印叠加到导出图
   │
   └─(4) 可选「写订单备注」：展示 remark 预览 → 用户人工确认
            └─> create-order（仅 remark 字段，不改商品/金额）
```

集成方式：麦当劳 MCP 服务器 `mcp.mcd.cn` **不返回 CORS 头**，浏览器里的网页无法直接 `fetch` 它（预检会被 403 拒绝）。本项目随附 **`mcp-proxy.py`** 本地代理——它在 `127.0.0.1` 起服务并托管页面，把同源 `/mcp` 请求转发给 `mcp.mcd.cn`，**Token 在服务端注入**（读取 `~/.workbuddy/mcp.json` 或环境变量 `MCD_MCP_TOKEN`），绝不进入客户端代码；前端经 `fetch('/mcp')` 调用，彻底绕过 CORS。以 `file://` 直接打开时则自动降级为离线模式（保留静态官方主题贴纸，应用内状态栏可见连接状态）。

---

## 4. 业务价值

1. **满足参赛硬要求**：将麦当劳 MCP 的真实数据（活动/菜单/门店/时间）织进创作流程，而非纯静态绘图工具。
2. **创作「应景」**：当期活动主题经 `campaign-calendar` 自动转化为可叠加的官方主题贴纸，让 UGC 跟上营销节奏。
3. **闭环到点单**：创作意图可经 `create-order.remark` 安全写入订单，连接「表达」与「消费」。
4. **艺术家资产提质**：以预置透明贴纸资产（见 `mcd-ui/art-assets`）降低创作门槛、保证质感。

---

## 5. 集成状态（如实声明）

- 本仓库随附的 **`mcd-cuptez.html` 已真实接入麦当劳 MCP**：经 `mcp-proxy.py` 本地代理调用 `campaign-calendar` 与 `now-time-info`，**加载即从麦当劳拉取当期真实活动并注入官方主题贴纸包**。已用无头 Chromium 真机验证通过——实测 `campaign-calendar · ✓ 已连接`、当期活动为「麦当劳 X PEACEMINUSONE」等联名活动、官方贴纸包动态更新为「当期 · PEACEM」并新增第 5 张真实活动贴纸。
- 运行方式：在仓库目录执行 `python3 mcp-proxy.py`，浏览器打开 `http://127.0.0.1:8787` 即让项目真实跑在麦当劳 MCP 之上（详见 README「安装与运行」）。
- `create-order` 写操作保持**强制人工确认 + 仅备注级**，未经确认绝不发起（符合活动规则对写操作的要求）。
- 以 `file://` 直接打开时，因无法跨域访问 MCP，自动降级为离线模式（应用内「关于创作演示」状态栏可见连接状态），此时官方贴纸包使用静态占位主题，其余创作功能不受影响。

---

## 6. 合规要点

- Token 仅存本地配置/环境变量，绝不进代码或仓库（已脱敏为 `${MCD_MCP_TOKEN}`）。
- 仓库示例代码仅限**非商业**使用，不售卖、不变现、不暗示官方背书。
- 内容不出现损害品牌、与竞品对比、不健康饮食/奢靡浪费暗示等违规内容（遵守《麦当劳 MCP 服务规则》与《WorkBuddy 软件许可及服务协议》）。
- 项目素材为原创或已合法授权（3D 容器模型与透明贴纸均为自制/已授权资产）。
