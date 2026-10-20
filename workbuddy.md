# WorkBuddy 对话上下文（workbuddy.md）

> 本文件为「麦麦创贴」使用 **WorkBuddy（腾讯 WorkBuddy 智能体）** 进行开发的对话上下文导出，用于核验本项目是否符合「麦当劳程序员创意开发大赛」WorkBuddy 专项奖励的联动条件。
> 开发环境：macOS + WorkBuddy（mcd-mcp 自定义连接器已配置并实测打通）。

---

## 0. 项目元信息

| 项 | 值 |
|---|---|
| 项目名称 | 麦麦创贴 · 快乐，由你来贴 |
| 形态 | 单文件离线 HTML（three.js / GLTFLoader / DRACOLoader 全内联） |
| 开发工具 | WorkBuddy（本会话全程使用） |
| MCP 连接器 | `mcd-mcp`（麦当劳中国 MCP Server，Streamable HTTP） |
| Token 状态 | 已申请并实测 `initialize` / `tools/list` 通过（35 工具） |
| 资产来源 | 3D 容器 GLB/STL + 透明艺术家贴纸（本地 codex 产出目录） |

---

## 1. 项目缘起与调研（WorkBuddy 内完成）

- 调研茶饮品牌（喜茶等）「手绘杯贴 / DIY 贴纸」爆火机制：表达欲与归属感、社交货币、抽卡式过审博弈、小程序内置绘图 + 门店即时打印的技术闭环；并暴露「手残党依赖代画」的痛点。
- 论证麦当劳转化基础：1995 年 Doodle Art Cups（*"Here, make it yours"*）、印度手绘薯条盒复刻成真包装、McCafé × Doodles 联名杯等，说明「包装即画布 + IP 资产 + 线下核销」是可成立的玩法。
- 结论：把「自由手绘」升级为「自由手绘 + 艺术家预置资产随时调用」，既保留自由、又用预置资产解决质感焦虑，同时把麦当劳真实 MCP 数据织进创作流程以满足参赛硬要求。

## 2. 关键设计决策（用户拍板）

1. **用户自由创作为主，艺术家贴纸随时调用**：开屏即空白画布；贴纸是「可叠加 / 可撤除」的加成层，非强制模板。
2. **移动端竖版、轻量**：参考喜茶「去定制 → 灵感创作」操作流，单屏 + 底部工具栏 + 贴纸底部抽屉（bottom-sheet）。
3. **四款真实 3D 容器**：可乐杯、麦旋风、McCafé、薯条盒，造型按真实产品修正（红杯+圆顶盖、透明矮胖杯+平盖勺孔、白纸杯+咖啡带+热饮盖、开口盒+微笑弧+薯条探出）。
4. **艺术家预置资产**：透明 PNG 贴纸包（线条童趣 / 波普 / 极简几何 / 星夜线等），点选即叠加。

## 3. MCP 接入（WorkBuddy 内完成）

- 读取 `https://open.mcd.cn/mcp/doc` 官方文档，沉淀为 `mcd-mcp-dev-rules.md`（接入配置、限流 600 次/分、错误码、参数枚举、TOON/Markdown 输出陷阱、写操作风险清单、35 工具清单、合规红线）。
- 在 `~/.workbuddy/mcp.json` 写入 `mcd-mcp` 连接器（无点前缀，符合 WorkBuddy 规范），并用真实 Token 实测：`initialize` 返回 `mcd-mcp v1.0.0`、`tools/list` 返回 **35 个真实工具**，确认服务端无状态。
- 规划真实调用点：`campaign-calendar`（注入官方主题贴纸）、`query-meals`/`query-nearby-stores`（上下文）、`now-time-info`（水印）、`create-order.remark`（仅备注级、人工确认）。

## 4. 资产与界面落地（用户提供 / 本地产出）

- 用户置入预置 3D 资产（四款容器的 GLB/STL 及预览图）与透明艺术家贴纸（art-1/2/3-transparent.png + 校验脚本）。
- 用户调整了界面配色与部分功能；主程序定名为「麦麦创贴 · 快乐，由你来贴」，并最终以单文件离线 3D 原型形态交付（`mcd-cuptez.html`，约 5.2MB，资产内联）。

## 5. 提交材料准备（本文件为其中之一）

按活动规则 `activityGuidelines.md` 准备仓库必备文件：

| 文件 | 状态 |
|---|---|
| `README.md` | 已生成 |
| `CONTEST_DECLARATION.md` | 已按官方模板原样放入（内容不可改） |
| `MCP_INTEGRATION.md` | 已生成（含集成状态如实声明） |
| `mcp-config.example.json` | 已生成（仅 `${MCD_MCP_TOKEN}` 占位符） |
| `workbuddy.md` | 本文件 |
| 源代码 | `mcd-cuptez.html` + 资产 |

## 6. 待办 / 风险提示

- **真实 MCP 已接入**：`mcd-cuptez.html` 经随附的 `mcp-proxy.py` 本地代理真实调用麦当劳 MCP——加载即拉取 `campaign-calendar` / `now-time-info`，将当期真实活动（如「麦当劳 X PEACEMINUSONE」联名）注入官方主题贴纸包；无头 Chromium 真机验证通过。`create-order` 保持强制人工确认 + 仅备注级。以 `file://` 直接打开时自动降级为离线模式（静态官方主题），其余功能不受影响。
- 仓库须 Public，且**项目（仓库）创建时间**须在 2025-12-25 ~ 2026-10-25；报名 Issue 标题与正文间、项目地址均不使用 Markdown 格式。
- 定榜时间 2026-10-26 00:00（以此时公开 Star 为准）；兑奖/信息提交截止 2026-11-14。

---

*以上上下文由 WorkBuddy 在开发会话中持续记录并导出，用于联动活动奖励核验。*
