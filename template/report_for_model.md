# 模型任务说明：生成报告占位符数据（仅 JSON）

人类可读的完整报告排版见 `template/report.typ`（`{{ 键名 }}` 占位）；内容结构见 `template/report.md`。渲染时会将叙事字段中的 Markdown 转为 Typst。**量表分、样本均值、焦虑/机制排序、压力事件等已由程序离线写入 `student.report_json_prefill`**；你**不要**改动这些键的值。你仅撰写 **`mechanism_explanation_text`** 与 **`personalized_advice_list`**，并须输出包含**全部键**的完整 JSON（未让你改写的键请从 `report_json_prefill` 原样抄写）。可结合 `student.scales` 与 `cohort` 理解语境。

## 键名、类型与填写要求

| 键 | 类型 | 说明 |
|----|------|------|
| `total_score` | number 或 null | GAD-7 焦虑总分（0–21）。 |
| `sample_mean` | number 或 null | 本次全体样本焦虑总分均值；**禁止编造。** |
| `relative_level` | string 或 null | 与样本均值比较：`"高于"` / `"低于"` / `"等于"`。 |
| `percentile` | number 或 null | 超过全体同学的百分比（0–100）；须从预填抄写。 |
| `percentile_band` | string 或 null | 分位带描述（如 `"前 20%"`）；须从预填抄写。 |
| `negative_events_list` | string | 该生勾选的压力事件，顿号分隔的一行纯文本。 |
| `sample_top_event_1` | string 或 null | 样本中最常勾选事件 1。 |
| `sample_top_event_2` | string 或 null | 样本中最常勾选事件 2。 |
| `top_anxiety_type_1` | string | 八大焦虑类型中得分最高者（如 `学业焦虑`、`AI学习焦虑`）。 |
| `top_anxiety_type_2` | string | 第二高。 |
| `top_anxiety_type_3` | string | 第三高。 |
| `top_mechanism_1` | string | 五种心理机制中相对最突出者（与计分命名一致）。 |
| `top_mechanism_2` | string | 第二高。 |
| `top_mechanism_3` | string | 第三高。 |
| `mechanism_explanation_text` | string | **一小段**连贯文字：结合 `top_mechanism_1/2/3`，用温暖、去病理化语言解释「这意味着你可能因为……而陷入焦虑」（勿抄题库原句；Markdown 仅可用加粗，勿用标题）。 |
| `personalized_advice_list` | string | 2–4 条针对性建议；Markdown 使用 `####` 或 `####` 以下小标题 + 列表；结合焦虑总分、前三焦虑类型与前三机制；总分偏高时提示可寻求校内心理支持。 |

## 输出约束（必须遵守）

1. **整段回复只能是合法 JSON**：从 `{` 开始到 `}` 结束；禁止 Markdown 代码围栏、禁止前后说明。
2. 所有键**必须全部出现**；无可靠数据时用 `null`（勿用空字符串冒充样本统计值）。
3. 除 `mechanism_explanation_text`、`personalized_advice_list` 外，其余键必须与 `report_json_prefill` **完全一致**。

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
  "sample_top_event_2": "身体健康",
  "top_anxiety_type_1": "学业焦虑",
  "top_anxiety_type_2": "AI学习焦虑",
  "top_anxiety_type_3": "社交焦虑",
  "top_mechanism_1": "他人评价条件化",
  "top_mechanism_2": "失败恐惧",
  "top_mechanism_3": "自我价值学业绑定",
  "mechanism_explanation_text": "当你格外在意……时，容易在……情境下感到焦虑加剧。",
  "personalized_advice_list": "#### 1. …\n- …\n\n#### 2. …\n- …"
}
```
