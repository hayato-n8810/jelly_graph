"""mapping.pyのテストスクリプト"""
import sys
from pathlib import Path

# srcディレクトリをパスに追加
sys.path.insert(0, str(Path(__file__).parent / "src"))

from jelly_graph.weight.mapping import load_jelly

# サンプルJSONファイルを読み込んでテスト
sample_file = Path(__file__).parents[1] / "sample" / "jelly_result_single.json"
jelly_obj = load_jelly(sample_file)

print("=== JellyObject の内容 ===\n")
print(f"ファイル数: {len(jelly_obj.files)}")
print(f"関数数: {len(jelly_obj.functions)}")
print(f"呼び出し数: {len(jelly_obj.calls)}")
print(f"fun2fun エッジ数: {len(jelly_obj.fun2fun)}")
print(f"call2fun エッジ数: {len(jelly_obj.call2fun)}")

print("\n=== ファイル一覧 ===")
for file_id, filepath in sorted(jelly_obj.files.items()):
    print(f"FileID {file_id}: {filepath}")

print("\n=== 最初の5つの関数 ===")
for func_id, loc in list(jelly_obj.functions.items())[:5]:
    print(f"FunctionID {func_id}: File={loc.fileid}, Line={loc.startrow}-{loc.endrow}")

print("\n=== 最初の5つの呼び出し ===")
for call_id, loc in list(jelly_obj.calls.items())[:5]:
    print(f"CallID {call_id}: File={loc.fileid}, Line={loc.startrow}-{loc.endrow}")

print("\n=== 最初の5つのfun2funエッジ ===")
for edge in jelly_obj.fun2fun[:5]:
    print(f"Function {edge[0]} -> Function {edge[1]}")

print("\n=== 最初の5つのcall2funエッジ ===")
for edge in jelly_obj.call2fun[:5]:
    print(f"Call {edge[0]} -> Function {edge[1]}")

print("\n✅ マッピング成功！")
