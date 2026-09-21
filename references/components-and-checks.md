# 固定组件与验收

制作或修订 HTML 时同时阅读 [交互式界面模型](interactive-demos.md)。生成和静态检查只依赖 Python 3 标准库；交互运行时不依赖第三方库，不访问后端。

## 四个模块

每页有数据采集与 UNS（`#namespace`）、Builder（`#builder`）、UNS Agent（`#uns-agent`）和服务模式（`#delivery`）。生成器现提供四个片段；它们不包含网站导航、Hero、其他业务场景或页脚，不能当作完整页面。全页其他示意视觉也需按交互契约实现。

- [Namespace](../assets/components/namespace.html)：选择数据来源、展开业务对象与字段；按 [数据接入](data-acquisition.md) 校验业务适用性。
- [Builder](../assets/components/builder.html) 使用 [完整 App 模型](../assets/components/app-demo.html) 作为底层预览，保留右下 Prompt；需求可预览差异并应用到 App，新增看板、优先级列或完工规则，支持版本同步与撤销。App 的详情、分派、表单校验、指标和图表随实际状态更新。
- [Agent](../assets/components/agent.html)：预设问答、Source、Chat/Card List、示例卡片和任务，均只操作本页状态。
- [样式](../assets/components/components.css) 与 [运行时](../assets/components/components.js) 随片段复制；字体与品牌沿用官网 token。服务模式仍从原 EMS 模板生成，不改变固定文字、按钮、链接和布局。

```sh
python3 /path/to/skill/scripts/render_components.py config.json --output output/components.html
```

合入当前页面的 main，保留生成片段中的四个 CSS 和三个 JS 引用。已有同名模块先替换，不叠加 ID；相对资源按最终页面目录解析。默认拒绝覆盖，已确认替换时可用 `--force`。最终交付真实可打开的整页，不分享配置模板或这个构建片段。

## 配置

以 [中文](../assets/components/example.zh-CN.json) 和 [英文](../assets/components/example.en.json) 为完整配置示例。

- language、app 指定页面语言与应用名称，logo 使用真实品牌资源。
- `builder.preview` 定义 App 数据与状态，字段见 [配置说明](interactive-demos.md#使用随包实现)。截图只作为视觉或事实参考。
- `builder.changes` 定义需求及实际界面变更，按 [Builder 联动](interactive-demos.md#builder-与-app-联动) 配置和实现。不能保留只有复制功能的 Builder。
- `namespace` 定义 heading、intro、sources；来源的 topic 关联 Agent sources，不额外杜撰另一份模型。
- agent 保留 heading、intro、scenario、question、answer、followup、sources、field_refs、data_status 和 result。`examples` 增加预设问答；每个问题显式声明 field_refs，followup 对应一个已有问题。sources 叶子在 Metric / State / Action 下；未声明字段拒绝生成。
- result 支持非空 table 或 list；需交互趋势等其他形式时，制作和验证相应组件，不把所有问题强制改为列表。模型中的源、单位、统计范围及演示状态必须一致。
- data_status 为 illustrative / verified；verified 的 evidence 应支持整组结果，仍由人工核对。界面预设问答不证明真实查询、集成、权限或算法已实现。
- delivery 只开放 scope、organize、integration、customize 四项业务内容；原 EMS 固定文案和 CTA 保持原有例外。

文本统一转义。资源只接受相对路径或 HTTPS，禁止将配置输入当作可执行 HTML/JS。独立/离线交付不引用远程运行时，品牌素材按授权打包。

## 静态检查

```sh
python3 /path/to/skill/scripts/check_solution.py index.html en.html --manifest screenshots.json --forbid WMS --output audit.json
```

`--forbid` 只填应清除的旧项目名，避免误禁合法业务比较。单语言页不强制双语链接。保留静态证据时提供图片清单，例如：

```json
{"images":[{"path":"assets/evidence.png","language":"zh-CN","kind":"original"}]}
```

localized 证据同时记录原图 source；路径相对最终页面。没有证据图片时无需制造清单，交互模型文字和状态的翻译仍需人工与浏览器检查。

检查范围：

- 必有模块、采集方式、UNS 业务模型、Builder 可操作预览与 Prompt、Agent 问答/Source/结果。
- 三个产品模块的交互根、语义控件、视觉用途声明、证据例外原因、ARIA 目标引用；拒绝用可点击图片/视频充当模型。
- Builder 编辑器与同模块 App 的目标绑定、差异预览、应用和撤销控件；行为仍由浏览器逐项验证。
- 服务模式两栏各三个列表项、原始固定按钮与链接；结构相同不等于像素相同。
- Title/Description/H1、重复 ID、本地资源与 CSS 依赖、锚点、语言互链、未翻译文字和旧项目名、证据图片来源。

静态返回码 0 不证明 JS 事件、真实渲染、图中语言或业务事实正确。它也无法识别所有 CSS 背景或 Canvas 内的静态 UI；报告保留 manual_required，必须逐项核对全页视觉清单。

## 行为检查

```sh
python3 /path/to/skill/scripts/test_components.py
node /path/to/skill/scripts/test_interactions.cjs
```

浏览器测试使用已安装的 Playwright/Chromium，依赖发现与实际范围见 [交互验收](interactive-demos.md#验收和交付)。它操作生成的中英模型，覆盖三个 App 视图、搜索/筛选/排序、校验失败与完成工单、分派、关联指标/活动、独立实例、UNS 与 Agent、重置、键盘/焦点、1440/1024/375px 和单 HTML 离线打开。定制图表/页面必须另做实际操作；不能把标准模板通过当成整页都已验证。

Builder 还覆盖预览不改 App、编辑失效、未知需求、实际应用三种变更、版本同步、重复应用、撤销保留业务记录、新增字段的完工校验，以及带 Builder 的单文件离线运行。
