# Meaningful Human Control(意味のある人間の管理)— 一次文献の裏取りレポート

*用途:講演「フィジカルAIとプロセスセキュリティ」への引用。作成日 2026-07-01。*
*方法:多角的Web検索 → 23ソース取得 → 39の検証可能主張を抽出 → 各主張を3票の敵対的検証(2/3で棄却)。24主張が確認、1主張が棄却。*

---

## 0. 要旨

- **Meaningful Human Control(以下 MHC)**は、**自律型致死兵器システム(LAWS)**をめぐる国際規制論のなかで、NGO **Article 36**(英)が生んだ政策概念である。学術的な体系化は **Santoni de Sio & van den Hoven(2018)** が行い、**tracking(追従)** と **tracing(追跡)** の2条件として定式化した。
- 以後、兵器の枠を超えて**自動運転・医療AI・AIガバナンス一般**へ拡張された。中心にあるのは、自律システムの帰結を必ず人間の責任へ結び戻し、**「責任の空白(responsibility gap)」**を塞ぐという発想である。
- ただし「MHC は曖昧で、実装可能な明確基準をまだ確立していない」という**批判**も一次・二次文献に明確に存在する。米国は "meaningful human control" を採らず **"appropriate levels of human judgment"** を用いる、という**用語上の対立**も要注意点。

---

## 1. 概念の起源と定義(一次文献)

### 1-1. 起源:Article 36 と Richard Moyes(政策側の原典)

- MHC という**特定の用語**は、**2013年の政策文書**(英国の無人システム政策を論じたもの)に遡る、と West Point の Lieber Institute は指摘している〔検証済〕。これは NGO **Article 36** による2013年ブリーフィングを指す(広範な「兵器への人間の管理」という倫理的関心そのものより、まずこの語の初出という意味で)。
  - 出典(二次・解説):Lieber Institute, West Point, *"How Meaningful is 'Meaningful Human Control'?"* — https://lieber.westpoint.edu/how-meaningful-is-meaningful-human-control-laws-regulation/

- **一次文献(原典)**:Richard **Moyes**(Article 36)による**ブリーフィングペーパー**
  **"Meaningful Human Control, Artificial Intelligence and Autonomous Weapons"**、**2016年4月**、ジュネーブの **CCW 専門家会合(LAWS)** に提出。Dr. **Heather Roff** との共同研究に基づく〔検証済〕。
  - URL:https://article36.org/wp-content/uploads/2016/04/MHC-AI-and-AWS-FINAL.pdf
  - 関連一次資料:Roff & Moyes, *"Meaningful Human Control"* (Stop Killer Robots 収録版)
    https://www.stopkillerrobots.org/wp-content/uploads/2021/09/Roff_Moyes_Meaningful_Human_Control-with-cover-page-v2.pdf

- この原典系の主張の要点〔いずれも検証済〕:
  - 「人間が引き金を引く」「ボタンを押す」「in the loop / on the loop / overseeing the loop」といった**通俗的な"人間の関与"の定式は概念的に混乱**しており、"the loop"(ループ)という枠組み自体が不適切である。
  - MHC は単なる技術要件ではなく、**時間的に層をなすシステム・プロセス・ドクトリン**として、戦闘行為への統制を保つために人間が設計するもの、と広く理解すべき。
  - 「meaningful human control」は、自律兵器規制の国際議論で**支配的・標準的な参照語**となった。

### 1-2. 定義:Santoni de Sio & van den Hoven(2018)— 学術的原典

- **一次文献**:Filippo **Santoni de Sio** & Jeroen **van den Hoven**,
  **"Meaningful Human Control over Autonomous Systems: A Philosophical Account,"**
  *Frontiers in Robotics and AI*, **Vol. 5, Article 15(2018年2月28日)**, **DOI: 10.3389/frobt.2018.00015**〔検証済〕。
  著者は **デルフト工科大学(TU Delft)** 技術政策管理学部・技術倫理/哲学セクション所属〔検証済〕。
  - 本文(オープンアクセス):https://www.frontiersin.org/journals/robotics-and-ai/articles/10.3389/frobt.2018.00015/full
  - 機関リポジトリ:https://research.tudelft.nl/en/publications/meaningful-human-control-over-autonomous-systems-a-philosophical-/

- **2つの条件(講演のキモ)**〔検証済〕:
  1. **Tracking(追従条件)**:システムは、それを設計・運用する**人間の関連する(道徳的)理由**と、**環境中の関連する事実**の双方に応答して振る舞うこと。
  2. **Tracing(追跡条件)**:システムは、その動作の帰結を、**設計・運用の連鎖に沿った少なくとも1人の人間へ遡って結び付けられる**ように設計されていること。
  - 本論文は概念を **LAWS(自律兵器の責任の空白)**に起源づけつつ、**自動運転車など非軍事の自律システムへ明示的に拡張**している〔検証済〕。

---

## 2. 学術的に体系化した主要一次文献

### 2-1. Mecacci & Santoni de Sio(2019/2020)— tracking の工学的操作化

- **一次文献**:Giulio **Mecacci** & Filippo **Santoni de Sio**,
  **"Meaningful human control as reason-responsiveness: the case of dual-mode vehicles,"**
  *Ethics and Information Technology*, **Vol. 22, Issue 2, pp. 103–115**(オンライン2019年/巻2020年), **DOI: 10.1007/s10676-019-09519-w**〔検証済〕。
  - https://link.springer.com/article/10.1007/s10676-019-09519-w
- 要点〔検証済〕:
  - **tracking = reason-responsiveness(理由応答性)** と読み替え、設計要件へ翻訳可能にする(価値配慮設計 value-sensitive design の路線)。
  - tracking を **"proximal scale of reasons"(理由の近接尺度)**、tracing を **"evaluation cascade table"(評価カスケード表)** で操作化。哲学・行動心理学・交通工学の学際作業に基づく。
  - **Tesla "autopilot" 等のデュアルモード運転**へ適用。tracking は工学・交通心理学の「制御」概念に**似つつ、それを超える**ことを明確化。
  - tracking 基準は「制御する側と制御される系の**関係の質**」に、tracing 基準は「人間の制御者の**能力と関与の性質**」に関わる、と役割を分ける。

### 2-2. Cavalcante Siebert et al.(2022/2023)— AI開発のための4つの実装可能特性

- **一次文献**:Cavalcante **Siebert, L.**, Lupetti, M.L., Aizenberg, E., Beckers, N., Zgonnikov, A., Veluwenkamp, H., et al. (2023),
  **"Meaningful human control: actionable properties for AI system development,"**
  *AI and Ethics*, **Vol. 3(1), pp. 241–255**(オンライン2022年5月18日), **DOI: 10.1007/s43681-022-00167-3**〔検証済〕。
- **4つの actionable properties(実装可能特性)**〔検証済〕:
  1. システムが動作すべき**道徳的に負荷のかかる状況の領域を明示的に定義**する(*moral operational design domain*=道徳的運用設計領域)。
  2. **適切で相互に整合する人間/AIの表象(representations)**。
  3. **人間が系を制御しうる能力・権限に見合った責任**の配分。
  4. **AIエージェントの行為と、道徳的責任を自覚する人間の行為との明示的な結び付き**。
  - Santoni de Sio & van den Hoven の哲学的枠組み(tracking/tracing)を、**アブダクションを介して工学実務へ橋渡し**。兵器を超え**一般の自律AI**へ拡張し、**責任の空白を塞ぐ手段**と位置づける〔検証済〕。

> ※ **一次文献 vs 二次的解説の別**:上記2-1・2-2・1-2 は査読付き一次研究。1-1 の Article 36 資料は政策原典(一次)。Lieber Institute 記事は解説(二次)。

---

## 3. 国際的な政策文脈(CCW / GGE / DoD)

- **Amoroso & Tamburrini(2020)**(査読付きレビュー、一次寄り):
  *"Autonomous Weapons Systems and Meaningful Human Control: Ethical and Legal Issues,"*
  *Current Robotics Reports*, **Vol. 1, pp. 187–194**, **DOI: 10.1007/s43154-020-00024-3**〔検証済〕。
  - https://link.springer.com/article/10.1007/s43154-020-00024-3
  - 主張:**自律兵器を含む全兵器系は、倫理的に許容され合法的に用いられるために MHC 下に置かれるべき**。中核問題は「人間の介入なしにロボット系が破壊力を解き放ち、生死の決定を下してよいか」。MHC は**倫理・法・国際政策フォーラムを横断する共有参照概念**として機能している〔検証済〕。
- **CCW / GGE on LAWS**:MHC はジュネーブの CCW(特定通常兵器使用禁止制限条約)専門家会合・政府専門家会合(GGE)で用いられる中心語。1-1 の Moyes ブリーフィングはまさにこの過程への提出物。
- **用語の対立(講演で効く論点)**:
  - 国際 NGO・多くの国:**"meaningful human control"**。
  - **米国 国防総省(DoD)**:これを採らず **"appropriate levels of human judgment"(適切な水準の人間の判断)**(DoD Directive 3000.09 の系譜)。同じ懸念に対し**あえて異なる語**を用いる政治的含意がある。
  - 解説出典:Lieber Institute(West Point)各記事
    https://lieber.westpoint.edu/human-responsibility-retained-us-positions-judgment-oversight-laws/
- **最近の動き**:オーストリア政府主催の**ウィーン会議 "Humanity at the Crossroads"** に **140カ国超**が参加し、自律兵器の国際規制を前進させた〔検証済/二次ソース(ブログ)による。一次の会議文書での再確認を推奨〕。

---

## 4. 兵器以外への拡張(2019–2023 の一次研究)

- **自動運転車**:2-1(Mecacci & Santoni de Sio 2019/2020)がデュアルモード車へ MHC を適用した代表例。狙いは「危険な運転操作について**人間と制度を最終的な制御者・責任者に留め**、安全を守り責任の空白を減らす」こと〔検証済〕。
- **AI一般・システム開発**:2-2(Siebert et al. 2022/2023)が MHC を**汎用自律AIの設計原則**へ一般化。
- **ハンドブック/レビュー(発展を示す二次資料)**:
  - *Research Handbook on Meaningful Human Control of Artificial Intelligence Systems*(Edward Elgar)
    https://www.e-elgar.com/shop/gbp/research-handbook-on-meaningful-human-control-of-artificial-intelligence-systems-9781802204124.html
  - arXiv:2112.01298(MHC の operationalization 関連)https://arxiv.org/abs/2112.01298
- **含意**:MHC は当初の LAWS 論から、**責任の帰属可能性(traceability)を工学要件へ落とす枠組み**として横展開している。この「軍事で鍛えた概念が民生の自律システムへ流れ込む」流れ自体が、フィジカルAI×プラントの論点に直結する。

---

## 5. 批判・限界

- **曖昧さ・実装困難**〔検証済〕:Lieber Institute は「**MHC は LAWS 統制のための明確で執行可能な基準をまだ確立していない**」とし、概念が**漠然として操作化が難しい**という批判を支持する。MHC は「LAWS の運用機能の監督・指揮に**実質的な人間の関与**を確保し、**説明責任の閾値**を置く」標準として性格づけられるが、**枠組みと実際の執行可能性の間にギャップ**がある。
  - https://lieber.westpoint.edu/how-meaningful-is-meaningful-human-control-laws-regulation/
- **【重要・裏取りの透明性】棄却された主張**:「MHC はこの約10年、学者・政治指導者・市民社会によって**根本的に誤解・誤伝されてきた**」という強い主張(ある解説ブログ由来)は、**敵対的検証で3票中3票が棄却(0-3)**。**事実として採用しない**。批判は「概念が曖昧/未確立」までに留め、「皆が根本的に誤解している」といった過度な一般化は避けるのが安全。
  - 出典(棄却):https://www.penncerl.org/the-rule-of-law-post/magnifying-human-confusion-meaningful-human-control-and-the-ongoing-debate-on-autonomous-weapons/

---

## 6. プロセスプラント/産業オートメーションへの含意

MHC 文献はプラント制御を直接扱わないが、講演の主軸(フィジカルAI暴走に対する「拠り所」)へ次のように接続できる。

1. **tracing 条件 = 「拠り所」の言語化**:どんなに自律化しても、**危険な帰結を必ず特定の人間・制度へ遡れる**設計にせよ、という要請。プラントでいえば、ロボット/ドローンのあらゆる危険動作が、設計・運用連鎖上の**説明責任ある人間に紐づく**こと。これは先生の「コントローラ異常対策」を、**責任のアーキテクチャ**へ拡張する視点を与える。
2. **tracking 条件 = 理由応答性**:自律エフェクタは、運用者の**関連する理由(安全上の意図)と現場の事実**に応答して動くべき。応答が切れた瞬間が「暴走」であり、そこを検知・遮断する層が要る。
3. **責任の空白(responsibility gap)**:フィジカルAI導入で「誰の責任とも言えない物理的破壊」が生じうる——これはまさに MHC が塞ごうとした空白。**"拠り所なき導入はリスク過大"** という先生の主張を、**「MHC(特に tracing)を満たせない自律系はプラントに導入すべきでない」**という規範命題へ言い換えられる。
4. **用語対立の教訓**:米国が "control" を避け "appropriate human judgment" を選んだ経緯は、「**どこまでを人間の管理と呼ぶか**」が政治的にも技術的にも係争点であることを示す。プラントの安全計装(SIS)における「人間の最終権限」をどう定義するかの議論に転用できる。

---

## 付録:主要出典一覧(一次=◎/政策原典=○/二次解説=△)

| 区分 | 文献 | 年 | 媒体・DOI/URL |
|---|---|---|---|
| ○ | Moyes(Article 36), *Meaningful Human Control, AI and Autonomous Weapons*(Roff と協働) | 2016 | CCW提出/article36.org …/MHC-AI-and-AWS-FINAL.pdf |
| ○ | Roff & Moyes, *Meaningful Human Control* | — | stopkillerrobots.org …/Roff_Moyes_… |
| ◎ | Santoni de Sio & van den Hoven, *MHC over Autonomous Systems: A Philosophical Account* | 2018 | *Frontiers in Robotics and AI* 5:15 / 10.3389/frobt.2018.00015 |
| ◎ | Mecacci & Santoni de Sio, *MHC as reason-responsiveness: dual-mode vehicles* | 2019/2020 | *Ethics and Information Technology* 22(2):103–115 / 10.1007/s10676-019-09519-w |
| ◎ | Cavalcante Siebert et al., *MHC: actionable properties for AI system development* | 2022/2023 | *AI and Ethics* 3(1):241–255 / 10.1007/s43681-022-00167-3 |
| ◎ | Amoroso & Tamburrini, *AWS and MHC: Ethical and Legal Issues* | 2020 | *Current Robotics Reports* 1:187–194 / 10.1007/s43154-020-00024-3 |
| △ | Lieber Institute(West Point), *How Meaningful is MHC?* / *US positions on judgment & oversight* | — | lieber.westpoint.edu |

*注:一部の一次PDF(Frontiers本体、Article 36 の一部PDF)はサイト側取得制限で本文抽出できず、書誌情報は機関リポジトリ・Springer 等のミラーで裏取りした。DOI・巻号・著者は複数ソースで一致を確認済み。*
