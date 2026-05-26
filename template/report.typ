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
#let link-blue = rgb("#2563EB")

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

#show link: it => underline(offset: 0.16em, stroke: 0.05em + link-blue)[
  #text(fill: link-blue)[#it]
]


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
    你的个性化焦虑报告
  ]

  #v(1em)

  #text(
    size: 11pt,
    fill: rgb("#52606D"),
  )[
    Personalized Anxiety Report
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
    清华大学学生心理发展指导中心
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

  这份报告是基于你在《自主测评第二弹》中填写的问卷生成的。我们希望从焦虑状态、焦虑来源、心理机制三个维度，为你绘制一幅关于“焦虑”的更完整的画像。

  #par(first-line-indent: 0em)[
    焦虑不是敌人，它是我们面对不确定性和压力时的正常反应。理解它，是与它和平相处的第一步。
  ]
]


#disclaimer[
  #soft-emph[温馨提醒：]
  本报告仅为心理健康科普与自我探索参考，不作为临床诊断依据。如果你的状态让你感到困扰，请主动寻求帮助，心理支持与求助资源将在报告末尾呈现。
]


// ============================================================

= 一、焦虑状态：你的焦虑水平如何？

== 1.1 在人群中：你的焦虑水平如何

#body-block[
  本次参与测评的同学中，焦虑总分的平均值为
  #emph[{{ sample_mean }} 分]。
  你的分数为
  #emph[{{ total_score }} 分]，
  #emph[{{ relative_level }}]
  平均水平。
]


#chart-title[图 1　群体分数分布直方图]

#chart-box[
  {{ chart_slot_1 }}
]


== 1.2 参考标准：你的焦虑程度意味着什么？

#body-block[
  这个分数到底意味着什么？我需要担心吗？

  下面的参考表将分数区间与不同的焦虑程度对应起来，帮助你更具体地理解自己当前的状态。
]


#chart-title[图 2　焦虑程度参考对照表]

#chart-box[
  {{ chart_slot_2 }}
]


#body-block[
  #soft-emph[参考解读：]
  如果你发现自己的分数偏高，请不要紧张。这不代表你“有问题”，而是说明你最近可能承受了较大的压力。很多同学都会经历这样的阶段。本报告仅为心理健康科普参考，不作为临床诊断依据。若分数达到重度水平且严重影响个人生活，可主动寻求帮助。
]


// ============================================================

= 二、焦虑原因：你因为什么而焦虑？

#body-block[
  焦虑很少凭空产生，它往往附着在具体的生活事件和领域上。这一部分，我们将拆解你的焦虑“导火索”——看看是哪些开学后的经历，以及哪几个生活领域，让你感受到了更多的压力。

  首先，是那些开学以来发生的、让你感到困扰的具体事件。它们有些是突发的，有些是持续累积的。
]


== 2.1 开学后的负面事件

#body-block[
  开学以来，你经历了一些让你感到压力的事情，它们可能单独出现，也可能叠在一起。你勾选了以下事件：
  #emph[{{ negative_events_list }}]。

  对于本次测评中的同学们来说，80% 以上的负面情绪由下列原因造成：学业评价或科研产出压力、身体健康、升学/申请/未来去向压力、开学初课程难度提升、人工智能带来的“威胁”、假期后收心困难、花粉/柳絮过敏、天气变化、学生工作及社团压力。在本次样本中，最常被勾选的是
  “#emph[{{ sample_top_event_1 }}]”，
  其次是
  “#emph[{{ sample_top_event_2 }}]”。
]


== 2.2 焦虑类型（多维度得分）

#body-block[
  接下来，我们把镜头拉远一点，看看你的焦虑在八个典型的生活领域上是如何分布的。有些领域可能你感受强烈，有些则相对平静。本次测评覆盖了家庭、未来、社交、经济、外貌、学业、AI 学习焦虑、AI 替代焦虑八个焦虑类型。

  下面几幅图从不同角度呈现了你的焦虑来源。
  #soft-emph[雷达图]对比了你与全体同学在 8 个焦虑类型上的平均得分，越靠外的顶点表示你在该类型的焦虑越突出。
  #soft-emph[维度间排序图]将 8 个焦虑类型按你的个人得分从高到低排列，可以一眼看出你最显著的焦虑领域。
]


#chart-title[图 3　焦虑类型雷达图与排序条形图]

#chart-box[
  {{ chart_slot_3 }}
]


#body-block[
  #soft-emph[图表解读：]
  你当前最突出的三个焦虑领域依次为
  #emph[{{ top_anxiety_type_1 }}]、
  #emph[{{ top_anxiety_type_2 }}]、
  #emph[{{ top_anxiety_type_3 }}]。
  其中，
  #emph[{{ top_anxiety_type_1 }}]
  是你当前感受最为强烈的压力源。
]


// ============================================================

= 三、焦虑机制：你为什么会焦虑？

#body-block[
  同样面对一场考试或一次社交，有的人辗转难眠，有的人则相对淡然。区别往往不在于事件本身，而在于我们内心处理信息的思维习惯——也就是心理机制。

  本次测评我们聚焦于五种与焦虑密切相关的思维模式：
  #emph[自我价值学业绑定]（自尊与成绩紧密挂钩）；
  #emph[他人评价条件化]（自我价值高度依赖他人的认可）；
  #emph[失败恐惧]（害怕失败带来的后果）；
  #emph[不确定性不耐受]（无法容忍模糊和未知）；
  #emph[冒充者综合征]（怀疑自己的成功靠运气）。
  了解这些机制，是打破焦虑循环的关键一步。

  下图呈现了你的焦虑背后的思维模式。
  #soft-emph[雷达图]对比你在各心理机制上的得分与全体同学的平均分，顶点越靠外表示该机制在你身上越明显。
  #soft-emph[排序图]将你的个人得分从高到低排列，找出对你影响最大的思维模式。
]


#chart-title[图 4　心理机制雷达图与排序条形图]

#chart-box[
  {{ chart_slot_4 }}
]


#body-block[
  #soft-emph[图表解读：]
  你较为突出的思维模式依次为
  #emph[{{ top_mechanism_1 }}]、
  #emph[{{ top_mechanism_2 }}]、
  #emph[{{ top_mechanism_3 }}]。
]


// ============================================================

= 四、焦虑画像总结与针对性建议

#body-block[
  综合本次测评结果，你的焦虑画像可以概括为：

  你的焦虑总分为
  #emph[{{ total_score }} 分]，
  #emph[{{ relative_level }}]
  平均值（本次样本均值
  #emph[{{ sample_mean }} 分]）。
  焦虑的核心来源是
  #emph[{{ top_anxiety_type_1 }}]、
  #emph[{{ top_anxiety_type_2 }}]
  和
  #emph[{{ top_anxiety_type_3 }}]，
  背后的关键机制是
  #emph[{{ top_mechanism_1 }}]、
  #emph[{{ top_mechanism_2 }}]
  和
  #emph[{{ top_mechanism_3 }}]。
]


#insight-card[
  {{ mechanism_explanation_text }}
]


#body-block[
  理解了焦虑的模式之后，下一步是：可以做些什么？

  基于你在本次测评中呈现的焦虑特征，我们为你匹配了以下几条针对性建议。它们不是标准答案，而是根据你的情况提供的参考方向。你可以选择其中让你感到被理解、愿意尝试的部分，按自己的节奏来。

  #soft-emph[温馨提醒：]
  以下建议结合 AI 辅助生成。
]


#insight-card[
  {{ personalized_advice_list }}
]


== 4.1 心理支持与求助资源

#body-block[
  学生心理发展指导中心相关资源可参考推送：
  #link("https://mp.weixin.qq.com/s/TqyxhsRCpcSpU0KpyTskcQ")[https://mp.weixin.qq.com/s/TqyxhsRCpcSpU0KpyTskcQ]

  其他资源可参考推送：
  #link("https://mp.weixin.qq.com/s/iV4p5pNCmHkMa1kexEjw3w")[https://mp.weixin.qq.com/s/iV4p5pNCmHkMa1kexEjw3w]

  此外，小清心公众号中还有不少关于焦虑应对的推送，你可以搜索关键词“焦虑”，找到更多陪伴与支持。
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
    清华大学学生心理发展指导中心
  ]
]