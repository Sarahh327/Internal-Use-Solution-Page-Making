# 交互式界面模型

仅制作或修改产品界面演示时使用交互模型。App、Builder、Namespace、Agent 的控件应产生可见结果；普通文案、业务解释、流程与关系图保持静态。首屏使用用户原始产品截图展示最终效果，桌面左文右图、移动端上下排列；截图保持原比例。

## 覆盖每个视觉位置

先区分首屏截图、普通静态说明与产品界面演示。仅为产品交互记录「初态 → 操作 → 结果 → 恢复」，交接清单包含 DOM ID、语言、数据依据与验证结果；不要求首屏和普通图文可点击。

| 原视觉 | 界面模型至少完成的操作 |
|---|---|
| 后续产品界面演示（首屏原始截图除外） | 选择记录或筛选范围，打开详情；业务动作改变状态，可重置 |
| 数据接入、UNS 树 | 选择来源查看采集方式与目标主题，展开对象与字段；源、模型、Agent 来源一致 |
| 普通流程、架构或关系说明 | 保持静态 HTML / SVG 图文，不需要点击切换 |
| 趋势、统计示意 | 切换对象/周期/系列更新实际图表和可读数据；单位、范围和计算一致，不能只改标题 |
| Builder | 保留 App 在底、Prompt 在右下的构图；预览具体变更、应用到关联 App、验证新增视图/字段/规则，并能撤销；版本与反馈一致 |
| Agent | 预设问题切换回答、Source 和结果；Chat/Card List 可切换，添加卡片或示例任务改变本页状态 |

截图放大、图片上的透明热点、仅 hover 高亮、无状态变化的按钮、循环播放录屏都不满足此要求。不要给导航、发送、筛选等控件制造无效外观。未覆盖的操作删去；确需保留的不可用状态说明具体原因。

首屏原始截图标记 data-visual="evidence" 并记录来源用途。普通图文可标记 data-visual="explanation"，不需要交互控件。品牌与装饰使用 brand / decoration；产品模型使用 interactive、唯一 id 和 data-t0-demo。不得把产品截图标成 explanation 来冒充产品交互。

## 实现约定

- 优先沿用页面已有栈。独立 HTML 使用随包的 HTML/CSS/原生 JS；不为局部演示引入 SPA、远端截图服务或 iframe 产品嵌入。模型能复制到页面，资源路径以交付目录为准。
- 首个有意义的状态直接写入语义 HTML，标题、字段、问题和结果可以选取/抓取；JS 渐进增强交互。脚本未加载时保留可读首态，依赖 JS 的操作先禁用，不能出现空白区域或假成功。
- 每个模型独立保存选中项、输入与动作状态，事件限定在自己的根节点。使用稳定 ID、显式状态更新和幂等动作；重复点击不重复添加，重置恢复初态。重新插入/加载脚本不能重复绑定事件。不要把一个模块的按钮绑定到页面另一个同名控件。
- 配置和用户输入按文本处理：模板输出转义，运行时用 `textContent`/表单值，禁止把输入传给 `innerHTML`、`eval` 或拼成可执行脚本。不要收集演示输入、访问生产 API、调用真实 AI、修改真实业务数据或要求凭证。复制需求是用户主动操作，失败时允许手动复制。
- Agent 使用与 UNS 字段对应的预设问答；自由输入未匹配示例时明确提示可用问题，保留当前结果，不伪造任意 AI 回答。添加任务只修改示例列表，不能表示已经安排真实调度。用「交互示例」「本地数据」等必要界面状态说明边界，避免长篇免责声明。
- 优先原生 `button`、`form`、`label`、`details/summary`。ARIA tabs 必须同时实现选中态、面板关联、方向键、Home/End 与合理焦点顺序；普通筛选用按钮组选中语义。成功反馈用温和的 `role="status"`，错误就近可见。避免为详情引入不必要的模态框；确需弹窗时实现焦点圈定、Esc 关闭和返回触发控件。
- 桌面、375px 手机和触屏均能完成关键操作；重排布局，不把整张桌面界面缩小到字不可读。滚动限定在宽表内，输入字号至少 16px，触屏目标宜 44px。尊重 `prefers-reduced-motion`；不自动循环、不制造假进度或为了演示增加等待。
- 双语翻译所有状态，包括错误、空态、重置反馈、aria 标签和预设问题。保留原始证据，不把本地化模型当成产品已支持该语言的证明。

## 产品级 App 质量标准

参考 [Hex 首页](https://hex.tech/) 的产品窗口构图、数据密度和多视图组织；参考 [shadcn/ui Blocks](https://ui.shadcn.com/blocks) 与 [Data Table](https://ui.shadcn.com/docs/components/data-table) 的应用骨架、层级、表格工具栏与控件细节。品牌仍来自 Tier0 官方设计，不照搬 Hex 的品牌、文案或商业数据。已有 React 项目优先使用已有的 shadcn 组件；单文件 HTML 用语义 DOM 和本地状态实现同等行为，不把模仿外观说成已使用 shadcn 包。

- **完整的应用构图**：产品顶栏、清晰的业务导航、主工作区、与记录关联的详情或抽屉。主 App 至少呈现三个有实际内容的关联视图，如工作台、工单、设备；专业场景选择相应视图，不给所有行业套维护工单。
- **可信的信息密度**：主 App 使用至少 6 条有差异的记录、至少 3 种生命周期状态；呈现对象、负责人、日期、优先级、处理记录等业务信息，避免整齐重复的占位行。宽度不足时给 App 整行空间，不把界面缩成不可读的装饰图。
- **真实的操作深度**：导航更换内容，搜索/筛选改变记录集，图表点击进入对应记录，设备关联到工单；详情中的检查项和表单保留当前输入，校验失败阻止提交，成功后改变记录状态及活动记录。至少一个主业务操作完成这一过程。
- **统一的数据关系**：列表、详情、状态分布、指标、图表基于同一组业务记录。完成工单后待办数、完成率、设备待办和完成图表同时更新，禁止给指标写死任意数字。Agent 的预设分析标明示例依据；它与 App 是独立的局部演示，不宣称跨模块实时同步。
- **精细的界面表达**：统一留白、排版、细边框、克制阴影、状态标签、选中态与焦点态。常规按钮保持中性，主操作有主次。图表带坐标/单位/周期及可读数值；空态和校验错误有明确下一步。
- **交付前看实物**：浏览器以 1440、1024、375px 检查初态、筛选态和详情态；检查焦点、遮挡和数据变化。将实际界面与参考的完整度并排评估。仅通过代码检查、增加按钮数量或说“shadcn 风格”不能证明达到质量要求。

随包 [App 模型](../assets/components/app-demo.html) 与 [运行时](../assets/components/app-demo.js) 提供上述设备维护实现：三个视图、八条工单、六台设备、搜索/筛选/排序、来源一致的统计、可校验的完成操作、负责人分派和活动记录。它是制作其他业务 App 的可运行质量参考，不是所有场景的固定模板。

## Builder 与 App 联动

让读者体验一句具体需求如何改变正在使用的 App。先展示可审查的前后差异，再应用到同一个实例，用新的界面或业务规则完成一次操作。App 继续保有已填写的记录，不能每次换需求就替换成另一张截图或重置全部数据。

随包提供三种有实际结果的需求：

- `board`：增加状态看板导航与三列工单卡片；卡片打开同一条工单详情，完工后移入已完成列。
- `priority`：增加优先级列，并把紧急未完成工单排在前面；保留区域与状态筛选。
- `downtime`：未完成的紧急工单增加必填停机分钟数；空值、负数或小数阻止完工，合法值写入该工单的活动记录。撤销规则后不删除已经完成的工单或其记录。

这些是设备维护的演示变更。其他场景选择能体现业务适配的需求，如批次字段、检验放行条件、排程视图；同步实现预览描述、App 实际状态及行为测试，不能只改预设按钮上的文字。

`builder.changes` 每项包含唯一 id、title、prompt、before、after；随包运行时只接受上述已实现的 id。需求框可编辑，未匹配预设时不更改 App；编辑后使旧的变更预览失效，重新预览才可应用。不要用假进度条或延迟暗示真实 AI 正在生成。

HTML 中 Builder 用 `data-app-target` 显式绑定同一模块的 App。通过目标元素上的 [CustomEvent](https://developer.mozilla.org/en-US/docs/Web/API/CustomEvent) 传递限定的 `t0:app-command`（state/apply/inspect/undo）和 `t0:app-state`；不依赖全局选择器或执行输入代码。已有应用栈可使用对应的共享状态方式。App 持有配置版本与业务记录，Builder 根据 App 返回的版本/变更状态显示反馈；不提前宣称应用成功。

重复应用同一变更不增加版本。撤销回退界面配置，保留业务操作；App 的重置同时恢复配置、业务数据和 Builder 初态。浏览器验证新规则确实能拦截错误输入、新视图和统计确实使用同一组记录、其他 App 实例不受影响，以及键盘和手机上的整个流程。

## 使用随包实现

生成器现在输出 Namespace、Builder、Agent、服务模式四个片段。仍需合入当前页面的语义 main、官方导航和页脚；**片段不是可直接分享的整页**。

```sh
python3 scripts/render_components.py assets/components/example.zh-CN.json --output output/components.html
```

- `builder.preview` 定义 title、workspace、as_of、people 和 records。每条记录有 id、title、asset、asset_name、location、priority、status、owner、due、completed_on、checks、note、history。字段和本地业务状态见中英配置示例；已完成记录必须有负责人、已勾选检查项、处理记录和完成日期。
- `render_app_demo(preview, language, demo_id)` 可用于 Builder、Hero 或独立 App 体验；每个调用使用不同的 HTML ID。趋势、排程、生产执行等场景按相同质量标准制作适合自身业务的模型。
- `namespace` 包含 heading、intro、sources；每个来源有 label、method、topic。topic 必须存在于 Agent 的 sources；生成器从同一映射生成可展开对象/字段。不同来源的适用性仍需业务核对。
- `agent.examples` 可追加 question、answer、result、field_refs；字段全部校验。`followup` 必须对应一个预设问题。根 data_status/evidence 适用于整组结果；verified 要覆盖全部示例的证据，不以此绕过人工核实。
- 运行时仅持有页面内存，刷新或重置还原示例。Card List 和任务列表防重复添加；所有模型保留可读首态，使用少量不依赖第三方库的脚本。

`assets/app-patterns/` 仅保留构图参考，其静态底图和未绑定按钮不得原样用于交付。可直接生成自包含 App 参考文件：

```sh
python3 scripts/render_demo.py assets/components/example.zh-CN.json --output output/app.html
python3 scripts/render_demo.py assets/components/example.zh-CN.json --with-builder --output output/builder-app.html
```

这些文件可单独打开和分享，含全部样式、脚本和示例数据。`--with-builder` 输出可操作的 Builder/App 联动参考；参考页不内置品牌素材，不替代带完整叙事、官方品牌、导航与页脚的方案页。

## 验收和交付

1. 用 `check_solution.py` 检查模块、视觉标记、控制目标和资源；它无法判断所有 CSS 背景、Canvas 内容或按钮是否有真实行为，必须再逐项核对视觉清单。
2. 用浏览器实际完成每个模型的初态 → 操作 → 结果 → 重置，并覆盖重复操作、无匹配输入、键盘和手机。检查控制台；不能以静态属性、截图或 HTTP 200 代替交互测试。
3. 随包组件使用 `python3 scripts/test_components.py` 和 `node scripts/test_interactions.cjs`。后者需要已有 Playwright 与 Chromium；可以用 `PLAYWRIGHT_MODULE`、`CHROMIUM_PATH` 指定现有安装，不由测试脚本自动安装。测试只证明随包样例，定制页面仍需自己的浏览器验证。
4. 分享 HTML 时从实际交付文件重新打开，确认数据已填入、脚本和样式已合入。要求自包含时内嵌数据/样式/脚本/必要图片，单独复制到空目录并断网测试，不能把源模板、配置占位符或构建片段当作成品。业务参考链接和网站 CTA 保持真实链接。
5. 文章/Markdown 配套可打开的模型 HTML；用户明确要求 PDF、图片等静态载体时附对应可点击 HTML 或链接，说明该载体本身不执行交互，不声称静态截图可点击。

## 官方实现依据

2026-09-20 核对；上方 Hex 和 shadcn 用于产品完成度与视觉参照，下方用于交互实现：
- [WAI Button pattern](https://www.w3.org/WAI/ARIA/apg/patterns/button/)：按钮语义、名称与键盘激活。
- [WAI Tabs pattern](https://www.w3.org/WAI/ARIA/apg/patterns/tabs/)：预加载面板、选中状态、焦点和方向键。
- [MDN details](https://developer.mozilla.org/en-US/docs/Web/HTML/Reference/Elements/details)：原生可展开内容。
- [web.dev Motion](https://web.dev/learn/accessibility/motion)：用户触发动作及减少动态效果。
