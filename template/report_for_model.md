# 模型任务说明：生成报告占位符数据（仅 JSON）

人类可读的完整报告排版见 `template/report.md`（`{{ 键名 }}` 占位）。**量表分、样本均值、百分位、焦虑/机制排序、人格标签等已由程序离线写入 `student.report_json_prefill`**；你**不要**改动这些键的值。你仅撰写 **`personality_analysis_text`** 与 **`personalized_advice_list`**，并须输出包含**全部键**的完整 JSON（未让你改写的键请从 `report_json_prefill` 原样抄写）。可结合 `student.scales` 与 `cohort` 理解语境；题库在 system 中按需查阅。

## 键名、类型与填写要求

| 键 | 类型 | 说明 |
|----|------|------|
| `total_score` | number 或 null | 焦虑相关量表总分（如 0–21）；无法从导出字段可靠计算则为 `null`。 |
| `sample_mean` | number 或 null | 本次全体样本焦虑总分均值；**user 中未提供样本汇总时为 `null`，禁止编造。** |
| `relative_level` | string 或 null | 与样本均值比较：`"高于"` / `"低于"` / `"等于"`；无 `sample_mean` 时为 `null`。 |
| `percentile` | number 或 null | 超过全体同学的百分比（0–100）；无样本分布时为 `null`。 |
| `percentile_band` | string 或 null | 分位带文字描述，如 `"前 20%"`；无样本时为 `null`。 |
| `negative_events_list` | string | 该生勾选的压力事件，用顿号或逗号分隔的**纯文本**一行。 |
| `sample_top_event_1` | string 或 null | 样本中最常勾选事件 1；无样本统计时为 `null`。 |
| `sample_top_event_2` | string 或 null | 样本中最常勾选事件 2；无样本统计时为 `null`。 |
| `top_anxiety_type_1` | string | 八大焦虑领域中该生得分最高者（简短中文名）。 |
| `top_anxiety_type_2` | string | 第二高。 |
| `top_anxiety_type_3` | string | 第三高。 |
| `top_mechanism_1` | string | 五种心理机制中该生得分最高者（与题库命名一致）。 |
| `top_mechanism_2` | string | 第二高。 |
| `top_mechanism_3` | string | 第三高。 |
| `personality_analysis_text` | string | 基于大五人格得分与该生焦虑模式的**一小段**个性化分析（Markdown 内嵌段落即可，勿抄题库）。 |
| `prominent_personality_trait` | string | 一句话概括最突出的人格特质组合，如 `"高尽责性与高宜人性"`。 |
| `personalized_advice_list` | string | 专属建议：可为多段 Markdown（列表/小标题）；规则参考——焦虑总分较高时侧重情绪调节与求助；机制前 2 侧重认知调整；焦虑类型前 3 可给领域建议。如果使用markdown格式，请使用小标题或者四级以下标题。 |

## 输出约束（必须遵守）

1. **整段回复只能是合法 JSON**：从 `{` 开始到 `}` 结束；禁止 Markdown 代码围栏、禁止前后解释性句子。
2. 所有键**必须全部出现**；无可靠数据时用 `null`（字符串字段若无样本统计用 `null`，不要用空字符串冒充样本值）。
3. 数值类型为 JSON number，不要用字符串形式的数字（除非字段定义为 string）。
4. 字符串内换行用 `\n` 转义；不要使用未转义的控制字符。

## 键集合与形态示例（示例值仅说明形态，勿照抄）

```json
{
  "total_score": 12,
  "sample_mean": 8.5,
  "relative_level": "高于",
  "percentile": 85,
  "percentile_band": "前 15%",
  "negative_events_list": "学业评价或科研产出压力、假期后收心困难",
  "sample_top_event_1": "学业评价或科研产出压力",
  "sample_top_event_2": "未来发展不确定感",
  "top_anxiety_type_1": "学业焦虑",
  "top_anxiety_type_2": "AI使用焦虑",
  "top_anxiety_type_3": "社交焦虑",
  "top_mechanism_1": "社会比较倾向",
  "top_mechanism_2": "失败恐惧",
  "top_mechanism_3": "自我价值学业绑定",
  "personality_analysis_text": "……",
  "prominent_personality_trait": "高尽责性与高宜人性",
  "personalized_advice_list": "### 1. …\n……"
}
```
