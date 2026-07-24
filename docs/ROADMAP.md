# Roadmap

以下内容均为 **Planned / 规划中**，不是当前已实现能力。

## P0：评估证据

| 规划项 | 解决的问题 | 当前未实现原因 | 前置条件 | 完成验证 |
| --- | --- | --- | --- | --- |
| 扩充有效 Golden Dataset | 降低小样本偶然性 | 当前 salon 集仅覆盖受控咨询问题 | 稳定语料版本和人工标注流程 | 独立复核标注，报告样本分布 |
| source/chunk 双层指标持续维护 | 区分文档召回与精确 chunk 召回 | 当前 salon 数据只有来源标注 | 稳定 chunk ID 与 corpus version | 两层 Hit@K/MRR 都可由明细重算 |
| 评估快照自动化与跨版本回归比较 | 持续检测检索策略、语料或模型变更导致的质量退化 | 当前仅保存一次手动执行的受控语料快照 | 固定 dataset/corpus 版本、稳定 Provider 配置和快照保留规则 | 自动比较两个及以上版本快照的 Hit@K、MRR、延迟和坏 Case |
| Dense/BM25/RRF 消融 | 量化融合收益 | 当前没有同一数据集的三组快照 | 固定索引和检索参数 | 同一 dataset 上分别报告三种结果 |

## P1：检索质量

| 规划项 | 解决的问题 | 当前未实现原因 | 前置条件 | 完成验证 |
| --- | --- | --- | --- | --- |
| 可选 Cross-Encoder Reranker | 改善候选精排 | 会增加模型、延迟和部署复杂度 | 足够大的标注集与延迟预算 | RRF 与 RRF + Reranker 消融 |
| Reranker fallback | 精排 Provider 失败时保持服务 | 尚未引入 Reranker | 明确超时和错误契约 | 故障测试验证回退排序 |
| Hard negatives | 提升相似文档区分能力 | 当前样本规模较小 | 收集真实坏 Case | 分类别评估误召回变化 |
| 更大测试集 | 提升指标可信度 | 当前为小型受控语料 | 标注审核和版本管理 | 报告样本覆盖与置信区间 |

## P2：摄取与文档

| 规划项 | 解决的问题 | 当前未实现原因 | 前置条件 | 完成验证 |
| --- | --- | --- | --- | --- |
| Markdown、DOCX、HTML、表格 | 扩展直接摄取格式 | 当前 CLI 直接处理 PDF | 每种格式的 loader contract | fixture 与端到端摄取测试 |
| 图片描述与 OCR | 处理扫描件和图片内容 | 需要视觉/OCR Provider | 隐私、成本和质量基线 | 扫描文档 Golden Dataset |
| Metadata enrichment | 改善过滤与引用 | 当前仅有基础 metadata | 稳定 schema 和回填策略 | metadata contract 和检索消融 |
| 文档生命周期管理 | 支持更新、删除和版本回滚 | 当前重点是可复现摄取 | 稳定 document identity | 更新/删除一致性测试 |

## P3：工程化

| 规划项 | 解决的问题 | 当前未实现原因 | 前置条件 | 完成验证 |
| --- | --- | --- | --- | --- |
| Docker 与 CI 真实集成验证 | 改善环境一致性 | Provider 和 runtime data 不适合默认 CI | 安全测试凭据与短生命周期索引 | 干净容器端到端通过 |
| OpenTelemetry / structured tracing | 跨组件观测 | 当前仅有本地 trace/logger | trace schema 和采样策略 | 故障链路可追踪 |
| 管理 API 或轻量 Dashboard | 查看 collection 和 ingestion 状态 | 当前以 CLI/MCP 为主 | 身份边界和只读 API | 权限与页面测试 |
| 远程 MCP transport | 支持网络部署 | 当前 stdio 满足本地集成 | 认证、TLS、部署设计 | 协议兼容和安全测试 |
| 权限与租户隔离 | 防止跨租户访问 | Collection 不是安全边界 | 认证、授权和存储隔离设计 | 越权测试与审计 |

## P4：消费者侧答案评估

Ragas 等答案级指标属于 Consumer Application，因为 MCP 服务首先负责检索结果与 Citation，不生成最终业务回答。

| 规划项 | 解决的问题 | 当前未实现原因 | 前置条件 | 完成验证 |
| --- | --- | --- | --- | --- |
| Faithfulness | 检查答案是否受上下文支持 | 本服务不生成最终答案 | Consumer 的回答数据集 | 固定模型与上下文评估 |
| Response Relevancy | 检查答案是否回答问题 | 同上 | 用户问题与参考标准 | 人工复核与自动指标对照 |
| Context Precision / Recall | 评估上下文选择质量 | 需要答案级 Ground Truth | 更完整标注 | 与检索 Hit@K 分开报告 |
