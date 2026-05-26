# psy-report

基于问卷星导出数据（`xlsx`）自动生成心理测评个性化报告的轻量流程项目。  
当前流程分为 4 步：

1. 离线计分（不依赖大模型）
2. 大模型补充叙事字段（输出 JSON）
3. 生成图表
4. 文本 + 图表拼接为 Typst 源文件并编译 PDF

---

## 目录结构

- `data/`：原始数据与问卷说明
- `template/report.typ`：最终报告 Typst 模板（含 `{{...}}` 占位符）
- `template/report_for_model.md`：给模型看的输出规范
- `prompts/system.md`：system prompt
- `prompts/user_report.md`：user prompt
- `scoring/compute.py`：离线计分主逻辑
- `main.py`：调用模型生成 `姓名_学号.json`
- `plot_report_charts.py`：生成 4 张图
- `render_report.py`：将 JSON + 图片拼接到 `report.typ`，可选 `--compile` 生成 PDF
- `output/`：所有输出产物

---

## 环境准备

### 1) 安装依赖

```bash
pip install -r requirements.txt
```

### 2) 安装 Typst（编译 PDF）

[Typst](https://typst.app/) 用于将 `.typ` 编译为 PDF。任选一种安装方式：

- Windows：`winget install --id Typst.Typst`
- 或从官网下载：https://github.com/typst/typst/releases

安装后终端应能执行 `typst --version`。

### 3) 配置大模型环境变量

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

- `output/charts/1_cohort_distribution.png`（全体分布，共用）
- `output/charts/姓名_学号/姓名_学号_2_gad_reference.png`
- `output/charts/姓名_学号/姓名_学号_3_anxiety_types_overlay.png`
- `output/charts/姓名_学号/姓名_学号_4_mechanisms_overlay.png`

报告结构见 `template/report.md`（焦虑状态 → 焦虑原因 → 焦虑机制 → 总结与建议）；排版模板为 `template/report.typ`。

### 第四步：渲染最终报告（文本 + 图）

```bash
python render_report.py
```

或指定 JSON：

```bash
python render_report.py --json output/姓名_学号.json
```

输出：

- `output/姓名_学号.typ`
- `output/姓名_学号.pdf`（加 `--compile` 时）
- `output/姓名_学号_long.png`（加 `--long-image` 时，各页纵向拼接的长图）

`render_report.py` 会自动：

- 替换 `template/report.typ` 中占位符
- 把上述 4 张图插入对应图表位置（`#figure` + `image`）
- 将模型输出的 Markdown 叙事字段转为 Typst 片段
- 默认移除模板中的 “JSON 结构示例”段落

渲染并一步编译 PDF：

```bash
python render_report.py --json output/姓名_学号.json --compile
```

渲染并导出长图（先编译 PDF，再拼接为一张 PNG，适合手机浏览/转发）：

```bash
pip install pymupdf Pillow
python render_report.py --json output/姓名_学号.json --long-image
```

更清晰的长图（提高 DPI）：

```bash
python render_report.py --json output/姓名_学号.json --long-image --dpi 200
```

仅编译（已生成 `.typ` 时）：

```bash
typst compile output/姓名_学号.typ
```

---
