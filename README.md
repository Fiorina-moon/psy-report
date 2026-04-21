# psy-report

基于问卷星导出数据（`xlsx`）自动生成心理测评个性化报告的轻量流程项目。  
当前流程分为 4 步：

1. 离线计分（不依赖大模型）
2. 大模型补充叙事字段（输出 JSON）
3. 生成图表
4. 文本 + 图表拼接为最终 Markdown 报告

---

## 目录结构

- `data/`：原始数据与问卷说明
- `template/report.md`：最终报告模板（含 `{{...}}` 占位符）
- `template/report_for_model.md`：给模型看的输出规范
- `prompts/system.md`：system prompt
- `prompts/user_report.md`：user prompt
- `scoring/compute.py`：离线计分主逻辑
- `main.py`：调用模型生成 `姓名_学号.json`
- `plot_report_charts.py`：生成 4 张图
- `render_report.py`：将 JSON + 图片拼接到 `report.md`
- `output/`：所有输出产物

---

## 环境准备

### 1) 安装依赖

```bash
pip install -r requirements.txt
```

### 2) 配置大模型环境变量

复制 `.env.example` 为 `.env`，填写：

- `PARATERA_API_KEY`
- `PARATERA_BASE_URL`
- `PARATERA_MODEL`
- `PARATERA_MODEL_LIST`（可选白名单）

---

## 快速开始（推荐顺序）

### 第一步：离线计分（全体 + 每个学生）

```bash
python -m scoring --config config.yaml
```

输出：

- `output/scored/scored_cohort.json`

### 第二步：生成该学生报告 JSON（模型）

默认会选 `row_index` 最小的学生；也可指定 `--row`。

```bash
python main.py --row 0
```

输出（命名规则：`姓名_学号`）：

- `output/姓名_学号.json`

调试提示词（不调用模型）：

```bash
python main.py --dry-run --row 0
```

输出：

- `output/姓名_学号_system.md`
- `output/姓名_学号_user.md`

### 第三步：绘图（4 张）

```bash
python plot_report_charts.py --row 0
```

输出：

- `output/charts/姓名_学号_1_cohort_distribution.png`
- `output/charts/姓名_学号/姓名_学号_2_gad_reference.png`
- `output/charts/姓名_学号/姓名_学号_3_anxiety_types_overlay.png`
- `output/charts/姓名_学号/姓名_学号_4_mechanisms_overlay.png`

### 第四步：渲染最终报告（文本 + 图）

```bash
python render_report.py 
```

输出：

- `output/姓名_学号.md`

`render_report.py` 会自动：

- 替换 `template/report.md` 中占位符
- 把上述 4 张图插入对应图表位置
- 默认移除模板中的 “JSON 结构示例”段落

---
