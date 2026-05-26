// ─────────────────────────────────────────────────────────────
//  个性化焦虑探索报告（最终稳定版）
//  特点：
//  - 修复中文 PDF 行高抖动
//  - 修复 emphasis 导致的行距变化
//  - 修复卡片内部 spacing 不统一
//  - 统一正文 vertical rhythm
//  - 更稳定的中文排版
//  - 更适合高质量 PDF 输出
// ─────────────────────────────────────────────────────────────


// ============================================================
// 全局参数
// ============================================================

#let body-size = 11pt

#let line-leading = 0.98em
#let para-gap = 0.72em

#let primary = rgb("#2E4057")

#let text-main = rgb("#1F2937")
#let text-soft = rgb("#667085")

#let border = rgb("#D0D5DD")

#let light-bg = rgb("#F7F8FA")
#let lighter-bg = rgb("#FAFBFC")



// ============================================================
// 页面
// ============================================================

#set page(
  paper: "a4",

  margin: (
    top: 2.4cm,
    bottom: 2.2cm,
    left: 2.6cm,
    right: 2.6cm,
  ),

  footer: context {
    align(center)[

      #set par(
        first-line-indent: 0em,
        spacing: 0em,
      )

      #text(
        size: 8pt,
        fill: rgb("#98A2B3"),
      )[
        #counter(page).display()
      ]
    ]
  },
)


// ============================================================
// 字体（重要修复）
// Sans 比 Serif 更稳定
// ============================================================

#set text(
  lang: "zh",

  font: (
    "Source Han Sans SC",
    "Noto Sans CJK SC",
    "PingFang SC",
    "Microsoft YaHei",
  ),

  size: body-size,
  fill: text-main,
)


// ============================================================
// 全局段落（统一 vertical rhythm）
// ============================================================

#show par: set par(
  justify: false,
  leading: line-leading,
  spacing: para-gap,
  first-line-indent: 0em,
)


// ============================================================
// 强调文本（重要修复）
// 不再使用 *...*
// ============================================================

#let emph(body) = text(
  weight: "semibold",
  fill: primary,
)[#body]


#let soft-emph(body) = text(
  weight: "semibold",
)[#body]


// ============================================================
// 基础组件
// ============================================================

#set list(
  spacing: 0.55em,
  body-indent: 1.8em,
)

#set heading(numbering: none)

#set figure(
  placement: none,
  gap: 0.3em,
)


// ============================================================
// 一级标题
// ============================================================

#show heading.where(level: 1): it => {

  v(1.5em)

  block(width: 100%)[

    #set par(
      first-line-indent: 0em,
      spacing: 0em,
    )

    #text(
      size: 13pt,
      weight: "semibold",
      fill: primary,
    )[
      #it.body
    ]
  ]

  v(0.55em)
}


// ============================================================
// 二级标题
// ============================================================

#show heading.where(level: 2): it => {

  v(1em)

  block(width: 100%)[

    #set par(
      first-line-indent: 0em,
      spacing: 0em,
    )

    #text(
      size: 11.5pt,
      weight: "semibold",
      fill: text-main,
    )[
      #it.body
    ]
  ]

  v(0.4em)
}


// ============================================================
// 三级标题
// ============================================================

#show heading.where(level: 3): it => {

  v(0.8em)

  block(width: 100%)[

    #set par(
      first-line-indent: 0em,
      spacing: 0em,
    )

    #text(
      size: body-size,
      weight: "semibold",
      fill: text-main,
    )[
      #it.body
    ]
  ]

  v(0.3em)
}


// ============================================================
// figure
// ============================================================

#show figure: it => {

  align(center)[

    block(
      width: 88%,
      inset: 0.9em,
      fill: lighter-bg,
      stroke: 0.5pt + border,
      radius: 6pt,
      breakable: true,
    )[

      #it.body

      #v(0.45em)

      #align(center)[

        #set par(
          first-line-indent: 0em,
          spacing: 0em,
        )

        #text(
          size: 8.8pt,
          fill: text-soft,
        )[
          #it.caption
        ]
      ]
    ]
  ]

  v(0.8em)
}


// ============================================================
// 工具组件
// ============================================================

#let body-block(body) = block(
  width: 100%,
)[
  #body
]


// ------------------------------------------------------------
// disclaimer
// ------------------------------------------------------------

#let disclaimer(body) = block(

  width: 100%,

  inset: (
    x: 1em,
    y: 0.8em,
  ),

  fill: light-bg,

  stroke: 0.45pt + border,

  radius: 5pt,

  above: 0.8em,
  below: 0.9em,

)[

  #set par(
    first-line-indent: 0em,
    leading: 0.96em,
    spacing: 0.6em,
  )

  #set text(
    size: 9.4pt,
    fill: text-soft,
  )

  #body
]


// ------------------------------------------------------------
// chart title
// ------------------------------------------------------------

#let chart-title(title) = block(

  width: 100%,

  above: 0.7em,
  below: 0.35em,

)[

  #set par(
    first-line-indent: 0em,
    spacing: 0em,
  )

  #text(
    size: 9.8pt,
    weight: "semibold",
    fill: rgb("#475467"),
  )[
    #title
  ]
]


// ------------------------------------------------------------
// insight card
// ------------------------------------------------------------

#let insight-card(body) = block(

  width: 100%,

  inset: (
    x: 1em,
    y: 0.9em,
  ),

  fill: lighter-bg,

  stroke: (
    left: 2.5pt + rgb("#BFC9D9")
  ),

  radius: 5pt,

  above: 0.7em,
  below: 0.8em,

)[

  #set par(
    first-line-indent: 0em,
    spacing: 0.72em,
    leading: 0.98em,
  )

  #body
]


// ------------------------------------------------------------
// chart box
// ------------------------------------------------------------

#let chart-box(body) = block(

  width: 100%,

  inset: 0.9em,

  fill: lighter-bg,

  stroke: 0.45pt + border,

  radius: 6pt,

  above: 0.5em,
  below: 0.8em,

)[
  #body
]


// ============================================================
// 封面
// ============================================================

#align(center)[

  #set par(
    first-line-indent: 0em,
    spacing: 0em,
  )

  {{ cover_image }}

  #v(2.4em)

  #text(
    size: 24pt,
    weight: "bold",
    fill: primary,
    tracking: 0.03em,
  )[
    个性化焦虑探索报告
  ]

  #v(1em)

  #text(
    size: 11pt,
    fill: rgb("#52606D"),
  )[
    Personalized Anxiety Insight Report
  ]

  #v(3em)

  #line(
    length: 24%,
    stroke: 0.7pt + border,
  )

  #v(1.3em)

  #text(
    size: 10pt,
    fill: text-soft,
  )[
    基于《自主测评第二弹》问卷数据的个体化分析
  ]

  #v(0.8em)

  #text(
    size: 9pt,
    fill: rgb("#98A2B3"),
  )[
    清华大学心理中心
  ]
]

#pagebreak()


// ============================================================
// 正文
// ============================================================

#block(
  width: 100%,
)[

  #set par(
    first-line-indent: 0em,
    spacing: 0em,
  )

  #text(
    weight: "semibold",
  )[
    同学，你好：
  ]
]

#v(0.9em)


#body-block[

  本报告基于你在《自主测评第二弹》中填写的问卷数据生成，旨在帮助你更系统地理解当前的情绪状态、压力来源与心理特点。

  焦虑是一种常见的心理应激反应，通常与现实压力、不确定性以及个体认知方式有关。本报告将从焦虑状态、压力来源、心理机制与人格特质四个维度，为你提供个体化分析。
]


#disclaimer[
  #soft-emph[【说明】]
  本报告仅作为心理健康科普与自我探索参考，不作为临床诊断依据。若近期情绪状态持续影响学习、生活或睡眠，建议联系学校心理健康教育与咨询中心寻求专业支持。
]


// ============================================================

= 一、焦虑状态：个体在群体中的位置

#body-block[
  你目前的焦虑程度在同龄人中处于什么位置？我们通过经典焦虑自评量表计算了你的焦虑总分，并将其放置于本次样本分布中进行比较。
]


#chart-title[图 1　群体分数分布直方图]

#chart-box[
  {{ chart_slot_1 }}
]


#body-block[
  #soft-emph[图表解读：]

  本次参与测评的同学中，焦虑总分平均值为
  #emph[{{ sample_mean }} 分]
  （范围 0–21 分）。

  你的分数为
  #emph[{{ total_score }} 分]，
  #emph[{{ relative_level }}]
  平均水平。

  具体而言，你的焦虑分数超过了
  #emph[{{ percentile }}%]
  的参与同学。
]


#body-block[
  若你的分数处于较高区间，并不意味着个体存在缺陷，更可能说明你近期正在承受较高水平的现实压力与心理负荷。
]


// ============================================================

= 二、焦虑来源：压力的核心指向

#body-block[
  焦虑通常并非抽象存在，而是与具体生活事件、环境变化与现实任务紧密相关。
]


== 1. 近期压力事件

#body-block[
  开学以来，你所经历的压力事件可能单独出现，也可能相互叠加。

  你所勾选的事件包括：

  #emph[{{ negative_events_list }}]
]


#body-block[
  在本次测评样本中，最常被勾选的压力事件是
  “#emph[{{ sample_top_event_1 }}]”，
  其次是
  “#emph[{{ sample_top_event_2 }}]”。
]


== 2. 核心焦虑领域

#body-block[
  我们进一步从八个典型生活领域（学业、AI 使用、社交、外貌、家庭、经济、未来就业、考试）观察你的焦虑分布情况。
]


#chart-title[图 2　焦虑领域雷达图与排序条形图]

#chart-box[
  {{ chart_slot_2 }}
]


#body-block[
  #soft-emph[图表解读：]

  数据显示，你当前最突出的三个焦虑领域依次为：

  #emph[{{ top_anxiety_type_1 }}]、
  #emph[{{ top_anxiety_type_2 }}]、
  #emph[{{ top_anxiety_type_3 }}]。

  其中，
  #emph[{{ top_anxiety_type_1 }}]
  是目前感受最强烈的压力来源。
]


// ============================================================

= 三、心理机制：压力处理的思维模式

#body-block[
  面对相似的现实压力，不同的认知方式会带来不同的情绪体验。心理机制部分关注的是：你通常如何理解压力、预测结果以及回应不确定性。
]


#chart-title[图 3　心理机制雷达图与排序条形图]

#chart-box[
  {{ chart_slot_3 }}
]


#body-block[
  #soft-emph[图表解读：]

  测评结果显示，你较为突出的思维模式依次为：

  #emph[{{ top_mechanism_1 }}]、
  #emph[{{ top_mechanism_2 }}]、
  #emph[{{ top_mechanism_3 }}]。

  其中，
  #emph[{{ top_mechanism_1 }}]
  可能是你在面对不确定情境时最常调用的核心心理机制。
]


// ============================================================

= 四、人格特质：心理反应的底层特征

#body-block[
  人格特质会影响我们感知压力、处理情绪以及建立人际关系的方式。基于简版大五人格模型，你的性格特征与焦虑模式呈现出以下关联：
]


#insight-card[
  {{ personality_analysis_text }}
]


// ============================================================

= 五、焦虑画像总结与行动建议

== 1. 焦虑画像综述

#body-block[
  综合本次测评结果，你的焦虑总分位于全体样本中的
  #emph[{{ percentile_band }}]。

  当前核心压力主要集中于
  #emph[{{ top_anxiety_type_1 }}]
  与
  #emph[{{ top_anxiety_type_2 }}]。

  在面对压力与挑战时，你更倾向于使用
  #emph[{{ top_mechanism_1 }}]
  与
  #emph[{{ top_mechanism_2 }}]
  的认知方式。

  同时，你的人格特质（尤其是
  #emph[{{ prominent_personality_trait }}]）
  也会影响你对现实压力的感受与应对模式。
]


== 2. 针对性行动建议

#body-block[
  基于你的个体画像，我们为你匹配了以下建议。你可以结合自己的节奏与实际情况，选择适合自己的部分逐步尝试：
]


#insight-card[
  {{ personalized_advice_list }}
]


#v(2em)

#align(right)[

  #set par(
    first-line-indent: 0em,
    spacing: 0em,
  )

  #text(size: body-size)[
    祝好。
  ]

  #text(
    size: body-size,
    weight: "semibold",
  )[
    清华大学心理中心
  ]
]