# UNS 业务建模格式

按用户提供的 [原始格式规范](uns-json-source.txt) 建模，业务层级与主题按当前方案选择，不能机械复用能源或设备示例。

- 根对象为 `{"namespace": [...]}`。每个节点使用 `name`，下级节点使用 `children`。
- 业务树从工厂（Plant / Factory）开始，可按车间、产线、工位或设备展开，不显示 v1 等版本前缀；不为凑层级虚构对象。主题、来源与 Agent 引用保持一致；已有真实接口前缀不得擅自修改，可将真实技术路径与展示层级分开说明。
- Topic 叶子必须直接属于 `Metric`、`State` 或 `Action`，不能直接放在工厂、产线、设备等业务文件夹下。
- Metric：测量值、KPI、计数器及数值时序；必须至少有一个包含 `name`、`type` 的 field。
- State：运行状态、模式、告警、当前任务、设备或物料状态。
- Action：命令、触发、操作员动作、业务事务和控制请求；区分建模定义与实际已连接的执行能力。
- 可选属性：displayName、description、enableHistory、mockData、extendProperties、fields。enableHistory 和 mockData 使用字符串 `"TRUE"` / `"FALSE"`，不能用布尔值。
- 字段类型仅可使用 INTEGER、STRING、FLOAT、DOUBLE、BOOLEAN、LONG、DATETIME。
- 完整路径拆分成 name/children 嵌套节点。字段定义不是实时数据值，不把示例读数直接写成节点键值。

页面展示采用可读的业务树，可配折叠 JSON；官网方案页默认不显示 JSON 下载入口；导出的 JSON 与显示结构保持一致，检查字段类型、主题父节点、字符串标志与 JSON 语法。格式校验通过不等同于实际产品导入测试通过。

原始规范中的“只输出一个 JSON 代码块”用于用户单独要求生成 JSON 的交付；不覆盖方案页制作、Skill 更新或修改报告的当前任务要求。

页面 Namespace 控制在一个紧凑版块内，与旁侧正文高度协调。保留业务层级及 Metric / State / Action；主题名与简短字段说明优先同行展示，JSON 默认折叠。移动端允许自然换行，不挤压或截断关键名称。
