#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
tia_sync.py - TIA Portal V14 / V14 SP1 Openness を Python (pythonnet) から操作する CLI

Claude Code からは次のように呼び出す想定:

    python tia_sync.py list                      ブロック一覧 (名前 / 種別 / 言語 / 番号)
    python tia_sync.py export [-b NAME ...]      ブロックを export/ に XML でエクスポート
    python tia_sync.py import-xml FILE [FILE..]  XML をインポートしてコンパイル
    python tia_sync.py scl FILE [FILE..]         SCL ソースからブロックを生成してコンパイル
    python tia_sync.py compile                   PLC ソフトウェアをコンパイル
    python tia_sync.py tags-export               タグテーブルを export/tags/ に XML でエクスポート
    python tia_sync.py tags-import FILE [FILE..] タグテーブル XML をインポート

設定は同じフォルダの tia_config.json から読む (--config で変更可)。
Windows + TIA Portal V14 (+ TIA Openness) + pythonnet が前提。
"""
from __future__ import annotations

import argparse
import glob
import json
import os
import sys
import traceback

HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_CONFIG = os.path.join(HERE, "tia_config.json")

# V14 系の PublicAPI フォルダ候補。SP1 は "V14 SP1" という別フォルダになる。
API_DIR_CANDIDATES = [
    r"C:\Program Files\Siemens\Automation\Portal V14\PublicAPI\V14 SP1",
    r"C:\Program Files\Siemens\Automation\Portal V14\PublicAPI\V14",
]


# ---------------------------------------------------------------------------
# 設定
# ---------------------------------------------------------------------------
def load_config(path: str) -> dict:
    if not os.path.exists(path):
        sys.exit(
            f"設定ファイルが見つかりません: {path}\n"
            "tia_config.example.json をコピーして tia_config.json を作成してください。"
        )
    with open(path, "r", encoding="utf-8") as f:
        cfg = json.load(f)

    cfg.setdefault("api_dir", "")
    cfg.setdefault("export_dir", os.path.join(HERE, "export"))
    cfg.setdefault("src_dir", os.path.join(HERE, "src"))
    cfg.setdefault("plc_device_name", "")
    cfg.setdefault("attach_to_running", True)
    cfg.setdefault("with_ui", True)

    if not cfg.get("project"):
        sys.exit("tia_config.json の 'project' に .ap14 プロジェクトのパスを設定してください。")

    if not cfg["api_dir"]:
        for cand in API_DIR_CANDIDATES:
            if os.path.exists(os.path.join(cand, "Siemens.Engineering.dll")):
                cfg["api_dir"] = cand
                break
    if not cfg["api_dir"] or not os.path.exists(
        os.path.join(cfg["api_dir"], "Siemens.Engineering.dll")
    ):
        sys.exit(
            "Siemens.Engineering.dll が見つかりません。TIA Openness がインストールされているか確認し、\n"
            "tia_config.json の 'api_dir' に PublicAPI\\V14 (または V14 SP1) フォルダを指定してください。"
        )
    return cfg


# ---------------------------------------------------------------------------
# Openness (.NET) の読み込み
# ---------------------------------------------------------------------------
def load_openness(api_dir: str):
    """pythonnet で Siemens.Engineering.dll を読み込み、モジュール群を返す。"""
    if os.name != "nt":
        sys.exit("TIA Openness は Windows 上でのみ利用できます。TIA Portal が入っている PC で実行してください。")

    try:
        from pythonnet import load  # pythonnet >= 3
        load("netfx")  # V14 Openness は .NET Framework 4.6.x 向け
    except ImportError:
        sys.exit("pythonnet が見つかりません: pip install pythonnet")
    except RuntimeError:
        # 既にランタイムがロード済み (再呼び出しなど) の場合は無視
        pass

    import clr  # noqa: E402

    sys.path.append(api_dir)

    # Siemens 推奨の AssemblyResolve: 依存 DLL を PublicAPI フォルダから解決する
    import System  # noqa: E402

    def _resolve(sender, args):
        name = str(args.Name).split(",")[0]
        cand = os.path.join(api_dir, name + ".dll")
        if os.path.exists(cand):
            return System.Reflection.Assembly.LoadFrom(cand)
        return None

    System.AppDomain.CurrentDomain.AssemblyResolve += System.ResolveEventHandler(_resolve)

    clr.AddReference("Siemens.Engineering")

    import Siemens.Engineering as tia  # noqa: E402
    from Siemens.Engineering.HW.Features import SoftwareContainer  # noqa: E402
    from Siemens.Engineering.Compiler import ICompilable  # noqa: E402
    from System.IO import FileInfo  # noqa: E402

    return tia, SoftwareContainer, ICompilable, FileInfo


# ---------------------------------------------------------------------------
# TIA Portal / プロジェクトへの接続
# ---------------------------------------------------------------------------
class TiaSession:
    def __init__(self, cfg: dict):
        self.cfg = cfg
        self.tia, self.SoftwareContainer, self.ICompilable, self.FileInfo = load_openness(cfg["api_dir"])
        self.portal = None
        self.project = None
        self.plc_sw = None
        self._opened_here = False

    # -- 接続 ---------------------------------------------------------------
    def open(self):
        tia = self.tia
        project_path = os.path.abspath(self.cfg["project"])

        if self.cfg["attach_to_running"]:
            for proc in tia.TiaPortal.GetProcesses():
                try:
                    portal = proc.Attach()
                except Exception as e:  # noqa: BLE001
                    print(f"[warn] 起動中の TIA Portal にアタッチできません: {e}")
                    continue
                prj = portal.Projects[0] if portal.Projects.Count > 0 else None
                if prj is not None and os.path.normcase(str(prj.Path.FullName)) == os.path.normcase(project_path):
                    print(f"[info] 起動中の TIA Portal (PID {proc.Id}) にアタッチしました")
                    self.portal, self.project = portal, prj
                    break
                if prj is not None:
                    print(f"[info] 別プロジェクトを開いている TIA Portal (PID {proc.Id}) はスキップ: {prj.Path.FullName}")

        if self.project is None:
            mode = tia.TiaPortalMode.WithUserInterface if self.cfg["with_ui"] else tia.TiaPortalMode.WithoutUserInterface
            print(f"[info] TIA Portal を起動しています ({'UI あり' if self.cfg['with_ui'] else 'UI なし'})...")
            self.portal = tia.TiaPortal(mode)
            self._opened_here = True
            print(f"[info] プロジェクトを開いています: {project_path}")
            self.project = self.portal.Projects.Open(self.FileInfo(project_path))

        self.plc_sw = self._find_plc_software()
        print(f"[info] PLC ソフトウェア: {self.plc_sw.Name}")
        return self

    def _find_plc_software(self):
        want = self.cfg["plc_device_name"]
        found = []
        for device in self.project.Devices:
            for item in self._walk_device_items(device.DeviceItems):
                sc = item.GetService[self.SoftwareContainer]()
                if sc is not None and sc.Software is not None:
                    # PlcSoftware のみ (HMI は除外)
                    if "PlcSoftware" in str(sc.Software.GetType().Name):
                        found.append((device.Name, sc.Software))
        if not found:
            raise RuntimeError("プロジェクト内に PLC ソフトウェア (CPU) が見つかりません。")
        if want:
            for dev_name, sw in found:
                if dev_name == want or sw.Name == want:
                    return sw
            names = ", ".join(d for d, _ in found)
            raise RuntimeError(f"plc_device_name='{want}' に一致する CPU がありません。候補: {names}")
        if len(found) > 1:
            names = ", ".join(d for d, _ in found)
            print(f"[warn] CPU が複数あります ({names})。先頭を使用します。tia_config.json の plc_device_name で指定できます。")
        return found[0][1]

    def _walk_device_items(self, items):
        for item in items:
            yield item
            yield from self._walk_device_items(item.DeviceItems)

    # -- 終了 ---------------------------------------------------------------
    def save(self):
        self.project.Save()
        print("[info] プロジェクトを保存しました")

    def close(self):
        # 自分で起動した場合だけ閉じる。アタッチした場合はユーザーの TIA Portal をそのまま残す。
        if self._opened_here:
            try:
                self.project.Close()
                self.portal.Dispose()
                print("[info] TIA Portal を終了しました")
            except Exception as e:  # noqa: BLE001
                print(f"[warn] 終了処理で例外: {e}")

    # -- ブロック列挙 -------------------------------------------------------
    def iter_blocks(self, group=None, path=""):
        group = group or self.plc_sw.BlockGroup
        for blk in group.Blocks:
            yield path, blk
        for sub in group.Groups:
            yield from self.iter_blocks(sub, f"{path}/{sub.Name}" if path else sub.Name)

    def iter_tag_tables(self, group=None, path=""):
        group = group or self.plc_sw.TagTableGroup
        for tt in group.TagTables:
            yield path, tt
        for sub in group.Groups:
            yield from self.iter_tag_tables(sub, f"{path}/{sub.Name}" if path else sub.Name)

    # -- コマンド実装 -------------------------------------------------------
    def cmd_list(self):
        print(f"{'Group':<20} {'Name':<32} {'Type':<12} {'Lang':<6} Num")
        print("-" * 80)
        for path, blk in self.iter_blocks():
            btype = str(blk.GetType().Name)
            lang = str(getattr(blk, "ProgrammingLanguage", ""))
            num = getattr(blk, "Number", "")
            print(f"{path or '-':<20} {blk.Name:<32} {btype:<12} {lang:<6} {num}")

    def cmd_export(self, block_names):
        export_dir = self.cfg["export_dir"]
        os.makedirs(export_dir, exist_ok=True)
        ok = skipped = 0
        for path, blk in self.iter_blocks():
            if block_names and blk.Name not in block_names:
                continue
            target_dir = os.path.join(export_dir, *path.split("/")) if path else export_dir
            os.makedirs(target_dir, exist_ok=True)
            target = os.path.join(target_dir, f"{blk.Name}.xml")
            if os.path.exists(target):
                os.remove(target)  # Openness は既存ファイルがあると例外を出す
            try:
                blk.Export(self.FileInfo(target), self.tia.ExportOptions.WithDefaults)
                print(f"[ok]   {blk.Name} -> {target}")
                ok += 1
            except Exception as e:  # noqa: BLE001
                # V14 では SCL ブロックや未コンパイル (不整合) ブロックはエクスポートできない
                msg = str(e).splitlines()[0]
                print(f"[skip] {blk.Name}: {msg}")
                skipped += 1
        print(f"[info] export 完了: {ok} 件成功 / {skipped} 件スキップ")
        return skipped == 0

    def cmd_import_xml(self, files):
        for f in self._expand(files):
            print(f"[info] import: {f}")
            imported = self.plc_sw.BlockGroup.Blocks.Import(self.FileInfo(os.path.abspath(f)), self.tia.ImportOptions.Override)
            for blk in imported:
                print(f"[ok]   imported block: {blk.Name}")
        return True

    def cmd_scl(self, files):
        srcs = self.plc_sw.ExternalSourceGroup.ExternalSources
        for f in self._expand(files):
            f = os.path.abspath(f)
            name = os.path.splitext(os.path.basename(f))[0]
            existing = srcs.Find(name)
            if existing is not None:
                existing.Delete()
            print(f"[info] 外部ソース登録: {name} <- {f}")
            src = srcs.CreateFromFile(name, f)
            print(f"[info] ブロック生成: {name}")
            src.GenerateBlocksFromSource()
            print(f"[ok]   generated from {name}")
        return True

    def cmd_compile(self):
        print("[info] コンパイル中...")
        result = self.plc_sw.GetService[self.ICompilable]().Compile()
        print(f"[info] 結果: {result.State}  warnings={result.WarningCount}  errors={result.ErrorCount}")
        self._print_messages(result.Messages, indent=1)
        return int(result.ErrorCount) == 0

    def _print_messages(self, messages, indent):
        for m in messages:
            state = str(m.State)
            desc = str(m.Description).strip()
            path = str(getattr(m, "Path", "") or "")
            if desc:
                where = f" [{path}]" if path else ""
                print(f"{'  ' * indent}{state}: {desc}{where}")
            try:
                self._print_messages(m.Messages, indent + 1)
            except Exception:  # noqa: BLE001
                pass

    def cmd_tags_export(self):
        out_dir = os.path.join(self.cfg["export_dir"], "tags")
        os.makedirs(out_dir, exist_ok=True)
        for path, tt in self.iter_tag_tables():
            target_dir = os.path.join(out_dir, *path.split("/")) if path else out_dir
            os.makedirs(target_dir, exist_ok=True)
            target = os.path.join(target_dir, f"{tt.Name}.xml")
            if os.path.exists(target):
                os.remove(target)
            tt.Export(self.FileInfo(target), self.tia.ExportOptions.WithDefaults)
            print(f"[ok]   {tt.Name} -> {target}")
        return True

    def cmd_tags_import(self, files):
        for f in self._expand(files):
            print(f"[info] import tag table: {f}")
            self.plc_sw.TagTableGroup.TagTables.Import(self.FileInfo(os.path.abspath(f)), self.tia.ImportOptions.Override)
        return True

    @staticmethod
    def _expand(files):
        out = []
        for f in files:
            matches = glob.glob(f)
            out.extend(matches if matches else [f])
        missing = [f for f in out if not os.path.exists(f)]
        if missing:
            sys.exit("ファイルが見つかりません: " + ", ".join(missing))
        return out


# ---------------------------------------------------------------------------
# エントリポイント
# ---------------------------------------------------------------------------
def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="TIA Portal V14 Openness CLI")
    p.add_argument("--config", default=DEFAULT_CONFIG, help="設定ファイル (default: tia_config.json)")
    p.add_argument("--no-save", action="store_true", help="終了時にプロジェクトを保存しない")
    p.add_argument("--no-compile", action="store_true", help="import-xml / scl の後にコンパイルしない")
    sub = p.add_subparsers(dest="cmd", required=True)

    sub.add_parser("list", help="ブロック一覧")
    sp = sub.add_parser("export", help="ブロックを XML でエクスポート")
    sp.add_argument("-b", "--block", action="append", default=[], help="対象ブロック名 (省略時は全て)")
    sp = sub.add_parser("import-xml", help="XML ブロックをインポート")
    sp.add_argument("files", nargs="+")
    sp = sub.add_parser("scl", help="SCL ソースからブロック生成")
    sp.add_argument("files", nargs="+")
    sub.add_parser("compile", help="コンパイル")
    sub.add_parser("tags-export", help="タグテーブルをエクスポート")
    sp = sub.add_parser("tags-import", help="タグテーブルをインポート")
    sp.add_argument("files", nargs="+")
    return p


def main(argv=None) -> int:
    args = build_parser().parse_args(argv)
    cfg = load_config(args.config)

    session = TiaSession(cfg)
    ok = True
    changed = False
    try:
        session.open()
        if args.cmd == "list":
            session.cmd_list()
        elif args.cmd == "export":
            ok = session.cmd_export(set(args.block))
        elif args.cmd == "import-xml":
            session.cmd_import_xml(args.files)
            changed = True
        elif args.cmd == "scl":
            session.cmd_scl(args.files)
            changed = True
        elif args.cmd == "compile":
            ok = session.cmd_compile()
        elif args.cmd == "tags-export":
            session.cmd_tags_export()
        elif args.cmd == "tags-import":
            session.cmd_tags_import(args.files)
            changed = True

        if changed and not args.no_compile:
            ok = session.cmd_compile()
        if changed and not args.no_save:
            session.save()
    except Exception:  # noqa: BLE001
        traceback.print_exc()
        ok = False
    finally:
        session.close()
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
