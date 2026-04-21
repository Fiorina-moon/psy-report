根据 **student.scales** 与 **cohort**（已由程序离线算好，勿改动数值含义），撰写 `personality_analysis_text` 与 `personalized_advice_list`。其余键名须出现在输出 JSON 中：**数值与排序类字段必须与 `student.report_json_prefill` 完全一致**（逐字抄写）；仅 `personality_analysis_text`、`personalized_advice_list` 由你撰写。

## 1. 输出 JSON 的键与类型说明

<<<REPORT_TEMPLATE>>>

## 2. 该生得分与样本信息（程序预计算 JSON）

<<<SCORE_PAYLOAD>>>

## 3. 输出要求

- **整段回复只能是合法 JSON**：从 `{` 到 `}`；禁止 Markdown 代码围栏与前后说明。
- 除 `personality_analysis_text`、`personalized_advice_list` 外，其余键的值必须与 `report_json_prefill` **完全一致**（含 `null`）。
