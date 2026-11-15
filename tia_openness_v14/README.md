# TIA Portal V14 Openness × Claude Code (S7-1200)

TIA Portal **V14 / V14 SP1** の Openness API を Python (pythonnet) から操作し、Claude Code に S7-1200 のブロック編集・生成・コンパイルをさせるためのツールです。

## 1. Windows PC 側の準備

1. **TIA Openness のインストール確認**
   TIA Portal → ヘルプ → インストール済みソフトウェア に「TIA Openness」があるか確認。無ければ TIA Portal V14 のインストールメディアから追加インストール。
2. **ユーザーグループ**
   `lusrmgr.msc` などで、自分の Windows ユーザーを **Siemens TIA Openness** グループに追加し、サインアウト/サインイン。
3. **Python**
   Python 3.8〜3.12 (64bit) をインストールし、依存を入れる:
   ```bash
   pip install -r requirements.txt
   ```
4. **設定ファイル**
   `tia_config.example.json` を `tia_config.json` にコピーし、`project` に `.ap14` のフルパスを設定。
   `api_dir` は空なら `PublicAPI\V14 SP1` → `PublicAPI\V14` の順に自動検出します。
5. **Claude Code**
   Windows に Claude Code をインストールし、このフォルダで `claude` を起動。`CLAUDE.md` が作業手順として読み込まれます。

## 2. 動作確認

```bash
python tia_sync.py list
```

初回は TIA Portal 側に「Openness アクセスを許可しますか」のダイアログが出るので **「はい、すべて」** を選びます。
ブロック一覧が表示されれば接続成功です。

```bash
python tia_sync.py scl src\Pump_Control.scl
```

サンプル FB が生成・コンパイルされることを確認してください。

## 3. コマンド一覧

| コマンド | 内容 |
|---|---|
| `list` | ブロック一覧 (グループ / 名前 / 種別 / 言語 / 番号) |
| `export [-b NAME]` | ブロックを `export/` に XML でエクスポート |
| `import-xml FILE...` | XML をインポート → コンパイル → 保存 |
| `scl FILE...` | SCL ソースからブロック生成 → コンパイル → 保存 |
| `compile` | コンパイルのみ |
| `tags-export` | タグテーブルを `export/tags/` に XML 出力 |
| `tags-import FILE...` | タグテーブル XML をインポート |

共通オプション: `--no-save` (保存しない)、`--no-compile` (変更後にコンパイルしない)、`--config PATH`。
終了コードは成功 0 / コンパイルエラーまたは例外 1 なので、Claude Code がそのまま成否を判定できます。

## 4. V14 ならではの注意点

- **ブロック → SCL の逆生成はできない** (GenerateSource は V15 以降)。SCL は「書いて生成」の一方向です。
- **SCL ブロックの XML エクスポートは非対応**の場合があります。失敗したブロックは `[skip]` と表示して続行します。
- **未コンパイルのブロックはエクスポートできません**。先に `compile` を通してください。
- Openness は **.NET Framework** 版なので、pythonnet は `load("netfx")` で読み込んでいます (スクリプト内で実施済み)。
- `Siemens.Engineering.dll` が見つからない場合は `tia_config.json` の `api_dir` を明示してください。
- TIA Portal を自分で起動した場合はコマンド終了時に閉じます。既に開いている TIA Portal にアタッチした場合は閉じません。

## 5. トラブルシューティング

| 症状 | 対処 |
|---|---|
| `Siemens.Engineering.dll が見つかりません` | Openness 未インストール、または `api_dir` のパス違い (V14 と V14 SP1 でフォルダ名が異なる) |
| アクセス拒否 / Openness の例外で接続できない | ユーザーが Siemens TIA Openness グループに入っていない、または再ログインしていない |
| `プロジェクトを開けない` | 同じプロジェクトを別の TIA Portal が開いている → そちらを閉じるか、同じプロジェクトを開いた状態にしてアタッチさせる |
| `[skip] ...` が多い | SCL ブロックまたは未コンパイルブロック。`compile` 後に再実行 |
| SCL 生成でエラー | 出力の `Error:` 行を確認。S7-1200 非対応命令、`#` 省略、`;` 抜けが多い |
