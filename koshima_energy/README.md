# 越島エナジー株式会社 — 標的企業のPRサイト（演習用素材）
# Koshima Energy Co., Ltd. — Target company PR site (exercise kit)

> ⚠️ **教育・防御演習専用 / For education & defensive training only.**
> 「越島エナジー株式会社」および本素材の人物・メールアドレス・所在地はすべて **架空** です。
> 実在の企業・団体・個人とは一切関係ありません。
> "Koshima Energy Co., Ltd." and all people, emails and locations here are **fictional** and
> unrelated to any real entity.

---

## 1. これは何か / What this is

ペネトレーション演習の**攻撃対象企業**「越島エナジー」の、**自社PR（宣伝）Webページ**一式です。
攻撃者が **OSINT** で偵察したときに見つける「標的の公開情報」という役割を担います。ページ自体は
DXを誇る普通の企業サイトに見えますが、そこには攻撃の足がかりになる情報がちりばめられています。

The company's own **PR/marketing website**. In the exercise it plays the role of the public information an
attacker finds during **OSINT** — an ordinary, DX-proud corporate site that nonetheless leaks the footholds
an attacker needs.

## 2. 企業設定 / Company premise（PPTX 2ページ目に準拠 / per slide 2）

- 地域冷暖房サービス事業者。**2地域**へ冷水・温水・蒸気を供給。
- 主要顧客に **病院・データセンター**。酷暑・厳冬での長期停止は深刻な被害（人身・物的・環境）につながる。
- 企業規模は大きくなく、**専任のセキュリティ担当者がいない**。
- **社長の指示でDXを推進**。**DX推進チームは社長直下**で、**独断でツール導入を試行**できる。
- 攻撃者は DX推進チームのメールアドレスを OSINT で入手 → フィッシング → 工場侵入 → 工場破壊を狙う。

**この設定がページ上でどう「餌」になるか / How the premise becomes bait:**
| 設定 / Premise | ページ上の表現 / On the page |
|---|---|
| DX推進チームが社長直下・独断で導入可 | 「DX推進」章＋社長メッセージで公言 |
| ツールの試行に前向き | 「新しいツールの提案・デモを歓迎」＋`dx-team@` 窓口 |
| 担当者のメール | 「推進チーム紹介」に氏名＋個人メールを掲載（OSINT表面） |
| 止められない重要顧客 | 病院・データセンターを明記（攻撃価値の高さを示す） |

## 3. 中身 / Contents

| ファイル / File | 役割 / Role |
|---|---|
| `logo/koshima_logo.svg` | 企業ロゴ（温＋冷の循環を表す2つのループ＋ワードマーク） / logo (warm+cool loops) |
| `web/index_ja.html` | 宣伝Webページ（日本語版） / PR page (Japanese) |
| `web/index_en.html` | 宣伝Webページ（英語版） / PR page (English) |

主張メッセージ / headline claim:
**「我が社は、社長以下全社体制で、DXを推進しています」/ "We drive DX company-wide, led by our President."**

## 4. 使い方 / Usage

- ブラウザで `web/index_ja.html`（または `_en.html`）を開くだけ。外部アセットなし＝オフライン動作。
  Just open `web/index_ja.html` (or `_en.html`) in a browser. No external assets; works offline.
- 掲載の氏名・メール・地区名は自由に差し替え可能。演習で他素材（GO DXフィッシング等）と
  つなげる場合は、`dx-team@koshima-energy.co.jp` 等を標的アドレスとして利用できます。

## 5. 演習での位置づけ（検討メモ）/ Role in the exercise (discussion notes)

- **OSINT → 初期アクセスの導線**：このページ1枚で「誰に・どんな口実で」フィッシングを送ればよいかが揃う。
  受講者に「自社PRが攻撃者への情報提供になり得る」ことを体感させられる。
- **組織の弱点の可視化**：セキュリティ専任不在＋現場裁量でのツール導入という文化的リスクを、
  “前向きなDX”の裏返しとして議論できる。
- **防御の学び**：公開情報の棚卸し、ソフト導入の承認フロー、送信元・リンクの検証、
  重要インフラのIT/OT分離——へ話をつなげられる。

*(本メモは演習ファシリテーター向けの検討たたき台です。)*
