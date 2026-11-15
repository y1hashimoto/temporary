# TIA Portal V14 (S7-1200) 編集ワークフロー

このフォルダは Siemens TIA Portal **V14 / V14 SP1** の Openness API を `tia_sync.py` 経由で操作するための作業場所。
TIA Portal 本体は Windows 上にあり、スクリプトは必ず **Windows 側の Python** で実行する。

## 基本ループ

1. まず現状を確認する: `python tia_sync.py list`
2. 編集方法を選ぶ
   - **SCL ブロック (FB/FC/OB/DB)** → `src/<ブロック名>.scl` を書き、`python tia_sync.py scl src\<ブロック名>.scl`
   - **LAD/FBD ブロック** → `python tia_sync.py export -b <ブロック名>` で `export/<ブロック名>.xml` を取り出して XML を編集し、`python tia_sync.py import-xml export\<ブロック名>.xml`
3. コマンドの最後に自動でコンパイルされる。終了コードが 1 なら出力の `Error:` 行を読み、原因を直して再実行する。
4. 完了したら TIA Portal 側で PLC へダウンロードする (ダウンロードはスクリプトでは行わない)。

## V14 の制約 (必ず守る)

- ブロック → SCL テキストの逆生成は V14 にはない。既存 SCL ブロックの中身を知りたいときは TIA Portal 上で確認するか、ユーザーに貼り付けてもらう。
- SCL ブロックの XML エクスポートは失敗することがある (`[skip]` と表示される)。それは正常。
- 未コンパイル・不整合なブロックはエクスポートできない。先に `python tia_sync.py compile` を通す。
- S7-1200 で使える命令・データ型のみ使う (S7-1500 専用命令は不可)。SCL ヘッダに `{ S7_Optimized_Access := 'TRUE' }` を付ける。
- `scl` コマンドは同名の外部ソースを削除して再登録し、同名ブロックを上書きする。意図しない上書きを避けるため、ブロック名は `list` で確認してから使う。
- TIA Portal が既に対象プロジェクトを開いていればアタッチする。別プロジェクトを開いている TIA Portal がある場合は新しいインスタンスを起動するので、事前にユーザーに閉じてもらうのが安全。

## ファイル配置

- `tia_sync.py` : CLI 本体
- `tia_config.json` : プロジェクトパス等 (git 管理外。`tia_config.example.json` からコピー)
- `src/` : Claude Code が書く SCL ソース。1 ファイル = 1 ブロック、ファイル名 = ブロック名
- `export/` : XML エクスポート先 (git 管理外)
