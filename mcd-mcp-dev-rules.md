# 麦当劳 MCP 接入与开发规则手册（实战版）

> 用途：为「麦当劳程序员创意开发大赛」参赛 Skill 开发提供接入与合规基准。
> 来源：`https://open.mcd.cn/mcp/doc` 官方文档 + 实测（2026-10-10 token 已验证打通）。
> 注意：本文件不含真实 Token，Token 仅存于 `~/.workbuddy/mcp.json`。

## 1. 接入配置（已实测通过）
- 协议：**Streamable HTTP**
- Endpoint（Base URL）：`https://mcp.mcd.cn`
- 认证：请求头 `Authorization: Bearer <MCP_TOKEN>`
- WorkBuddy 配置落点：`~/.workbuddy/mcp.json`（无点前缀；带点 `.mcp.json` 是 WB 自管的 connector-proxy，勿改）
- 配置片段：
  ```json
  {
    "mcpServers": {
      "mcd-mcp": {
        "type": "streamablehttp",
        "url": "https://mcp.mcd.cn",
        "headers": { "Authorization": "Bearer <MCP_TOKEN>" }
      }
    }
  }
  ```
- 启用方式：连接器管理页 → 右上「自定义连接器」→ 对 `mcd-mcp` 点「信任」。

## 2. 实测结论（2026-10-10）
- `initialize` → HTTP 200，`serverInfo: mcd-mcp v1.0.0`，`capabilities.tools` 已声明。
- `tools/list` → **35 个真实工具**（比文档 4.1 列的 33 个多，多出 `query-promotions`、`query-survey-coupon` 等；以运行时 tools/list 为准）。
- **会话机制：无状态**。文档未定义 `Mcp-Session-Id`；实测在无 session 下 `tools/list` 直接返回 35 工具，仅靠 `Authorization` 头识别用户。利好集成——WorkBuddy 每次调用独立，无需维护会话。

## 3. 限流与错误码
- **限流：每 Token 600 次/分钟**，超限返回 `429`。
  - ⚠️ WorkBuddy 单轮对话可能多次调用工具；开发 Skill 时避免循环/批量狂刷，必要时在 Skill 提示词里加「调用间隔/合并请求」约束。
- 错误码：
  - `401`：Token 无效/过期/缺失 → 检查 header 与 Token。
  - `429`：触发限流 → 降频。

## 4. 关键参数枚举（最易踩坑）
- `beType`（业务/就餐类型）：
  - `1` = 到店，`2` = 麦乐送（外送），`5` = 得来速（drive-thru），`6` = 企业团餐
- `orderType`（订单类型）：
  - `1` = 到店自提，`2` = 外送（麦乐送）
  - 注：不同工具对这两个维度的必填要求不同，调用前务必看该工具入参说明。
- `searchType`（`query-nearby-stores`）：`1`=按当前位置（需经纬度），`2`=城市+关键词，`3`=经纬度
- `cancelReasonCode`（`cancel-order`）：`1`改主意,`2`重复,`3`点错,`4`地址错,`5`时间错,`-1`其它

## 5. 工具输出格式陷阱
- 通用结构：`{ "success", "code", "message", "datetime", "data": ... }`
- ⚠️ **TOON 紧凑格式**：如 `list-nutrition-foods` 的 `data` 是文本而非 JSON：
  `[1]{productName,nutritionDescription,energyKj,...}:\n  猪柳麦满分,null,1288,308,...`
  → Skill 解析时需按逗号/换行切分，不能直接 `JSON.parse`。
- ⚠️ **Markdown 输出**：`campaign-calendar`、`available-coupons` 直接返回 Markdown 列表（含图片链接），适合直接渲染，但程序化处理需自行解析。
- 套餐/特制：`query-meal-detail` 从 v1.0.5 起含 `modification` 字段（换组合/特制）；`query-meals` 含 `withOrder`/`currentPrice` 等（v1.0.6 促销价、随单购）。

## 6. 写操作风险清单（必须加确认机制）
以下工具会**改变用户真实状态**，Skill 中绝不可让 AI 自动执行，必须人工确认：
| 工具 | 真实后果 |
|---|---|
| `create-order` | 生成**待支付订单**（返回 `payH5Url`），真实下单动作 |
| `cancel-order` | 取消订单 |
| `delivery-create-address` | 新增配送地址 |
| `auto-bind-coupons` | 一键领取所有麦麦省券 |
| `mall-create-order` | 积分兑换下单（消耗积分） |
| `draw-lottery` | 积分抽奖（消耗积分，**1 秒内不可重复调用**） |
| `party-order-create` | 主题活动（派对/品鉴会等）下单 |

**安全（只读/计算）类**：`calculate-price`（仅算价，不改状态）、所有 `query-*`/`list-*`、营养/门店/优惠券**查询**、`campaign-calendar`、`now-time-info` 等。

## 7. 实测 35 个工具（按场景）
- 菜单/营养：`list-nutrition-foods`, `query-meals`, `query-meal-detail`, `query-meal-assistance`
- 门店/地址：`query-nearby-stores`, `delivery-query-addresses`, `delivery-create-address`, `delivery-query-stores`
- 点餐/订单：`calculate-price`, `create-order`, `cancel-order`, `query-order`, `order-list`
- 优惠券/活动：`query-store-coupons`, `available-coupons`, `auto-bind-coupons`, `query-my-coupons`, `campaign-calendar`, `query-promotions`
- 积分/会员：`query-my-account`, `mall-points-products`, `mall-product-detail`, `mall-create-order`, `mall-order-list`, `mall-order-detail`, `query-lottery-info`, `draw-lottery`, `query-my-prizes`
- 派对/主题：`query-party-city`, `query-party-store`, `query-partystore-date`, `query-partystore-session`, `party-order-create`
- 其他：`now-time-info`, `query-survey-coupon`

## 8. 合规红线（来自 MCP 服务规则 + 活动规则）
- **Token 保密**：不写入代码、不提交仓库、不泄露（如已明文出现可考虑去 open.mcd.cn 重新生成）。
- **非商业限制**：仓库示例代码仅限非商业使用；不得商业售卖/付费分发/引流变现/暗示官方背书。
- **内容合规**：不得出现违法、政治敏感、损害麦当劳品牌、与竞品对比、不健康饮食/奢靡浪费暗示等内容。
- **原创/授权**：项目须原创或已合法授权，不侵权。
- 遵守《麦当劳 MCP 服务规则》与《WorkBuddy 软件许可及服务协议》。

## 9. 参赛仓库必备文件（来自活动规则）
- 必须：`README.md`、`CONTEST_DECLARATION.md`（内容不可改，用官方模板）、`MCP_INTEGRATION.md`、`mcp-config.example.json`（脱敏，仅环境变量占位符）、源代码。
- 参与 WorkBuddy 专项奖励则必须：`workbuddy.md`（对话上下文导出）。
- 仓库 Public；项目创建时间 2025-12-25 00:00 ~ 2026-10-25 23:59；报名通过 Issue，≤1000 字无图。
- 排名看 GitHub 公开 Star；同一账号仅最高 Star 项目进榜。
- 关键节点：报名截止 10-25 23:59；定榜 10-26 00:00；兑奖信息提交截止 11-14。
