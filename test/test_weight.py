"""weight.pyのテストスクリプト"""
import sys
from pathlib import Path

# srcディレクトリをパスに追加
sys.path.insert(0, str(Path(__file__).parent / "src"))

from jelly_graph.weight.mapping import load_jelly
from jelly_graph.weight.weight import (
    dependency_weights,
    get_dependency,
    get_total_dependencies,
    get_total_calls,
    get_caller_dependencies,
    get_callee_dependencies,
    get_top_dependencies,
)
from jelly_graph.classes.jelly import FunctionID

# サンプルJSONファイルを読み込み
sample_file = Path(__file__).parents[1] / "sample" / "jelly_result_single.json"
jelly_obj = load_jelly(sample_file)

print("=== Jelly データ読み込み完了 ===")
print(f"ファイル数: {len(jelly_obj.files)}")
print(f"関数数: {len(jelly_obj.functions)}")
print(f"呼び出し数: {len(jelly_obj.calls)}")
print(f"call2fun エッジ数: {len(jelly_obj.call2fun)}")

# 依存関係の重みを計算
print("\n=== 依存関係の重み計算中... ===")
depend_map = dependency_weights(jelly_obj)

# 統計情報を表示
print(f"\n総依存関係数（ユニークなペア）: {get_total_dependencies(depend_map)}")
print(f"総呼び出し回数: {get_total_calls(depend_map)}")

# 呼び出し回数の多い依存関係トップ10を表示
print("\n=== 呼び出し回数トップ10 ===")
top_deps = get_top_dependencies(depend_map, top_n=10)
for i, (caller_id, callee_id, count) in enumerate(top_deps, 1):
    caller_loc = jelly_obj.functions.get(caller_id)
    callee_loc = jelly_obj.functions.get(callee_id)
    
    caller_file = jelly_obj.files.get(caller_loc.fileid) if caller_loc else "不明"
    callee_file = jelly_obj.files.get(callee_loc.fileid) if callee_loc else "不明"
    
    print(f"{i}. 関数 {caller_id} -> 関数 {callee_id}: {count}回")
    print(f"   呼び出し元: {Path(caller_file).name if caller_file != '不明' else caller_file}")
    print(f"   呼び出し先: {Path(callee_file).name if callee_file != '不明' else callee_file}")

# 特定の関数の依存関係を調査（例：関数14）
test_func_id = FunctionID(14)
if test_func_id in jelly_obj.functions:
    print(f"\n=== 関数 {test_func_id} の依存関係 ===")
    
    # この関数が呼び出す関数
    caller_deps = get_caller_dependencies(depend_map, test_func_id)
    if caller_deps:
        print(f"関数 {test_func_id} が呼び出す関数:")
        for callee, count in sorted(caller_deps.items(), key=lambda x: x[1], reverse=True):
            print(f"  -> 関数 {callee}: {count}回")
    else:
        print(f"関数 {test_func_id} は他の関数を呼び出していません")
    
    # この関数を呼び出す関数
    callee_deps = get_callee_dependencies(depend_map, test_func_id)
    if callee_deps:
        print(f"\n関数 {test_func_id} を呼び出す関数:")
        for caller, count in sorted(callee_deps.items(), key=lambda x: x[1], reverse=True):
            print(f"  関数 {caller} -> : {count}回")
    else:
        print(f"\n関数 {test_func_id} を呼び出す関数はありません")

# 特定の依存関係の強さをチェック
print("\n=== 特定の依存関係の例 ===")
example_pairs = [(FunctionID(14), FunctionID(1)), (FunctionID(14), FunctionID(10)), (FunctionID(17), FunctionID(1))]
for caller, callee in example_pairs:
    strength = get_dependency(depend_map, caller, callee)
    if strength > 0:
        print(f"関数 {caller} -> 関数 {callee}: {strength}回")

print("\n✅ 依存関係の重み計算完了！")
