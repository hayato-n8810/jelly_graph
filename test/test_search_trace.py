"""search_src と search_dst 関数のテストスクリプト"""
from pathlib import Path

from jelly_graph.weight.mapping import load_jelly
from jelly_graph.weight.weight import dependency_weights
from jelly_graph.graph.build_callgraph import build_callgraph
from jelly_graph.graph.trace import (
    find_root_nodes,
    find_leaf_nodes,
    search_src,
    search_dst,
    print_src_trace_results,
    print_dst_trace_results,
)
from jelly_graph.classes.jelly import FunctionID

# サンプルJSONファイルを読み込み
sample_file = Path(__file__).parents[1] / "sample" / "jelly_result_single.json"
jelly_obj = load_jelly(sample_file)

print("=== Jelly データ読み込み完了 ===")
print(f"ファイル数: {len(jelly_obj.files)}")
print(f"関数数: {len(jelly_obj.functions)}")

# 依存関係の重みを計算
print("\n=== 依存関係の重み計算中... ===")
depend_map = dependency_weights(jelly_obj)

# コールグラフを構築
print("\n=== コールグラフ構築中... ===")
graph = build_callgraph(depend_map)
print(f"ノード数: {graph.number_of_nodes()}")
print(f"エッジ数: {graph.number_of_edges()}")

# 根ノードと葉ノードを検出
root_nodes = find_root_nodes(graph)
leaf_nodes = find_leaf_nodes(graph)
print(f"\n=== ノード情報 ===")
print(f"根ノード数: {len(root_nodes)}")
print(f"根ノードID: {sorted(root_nodes)}")
print(f"葉ノード数: {len(leaf_nodes)}")
print(f"葉ノードID: {sorted(leaf_nodes)}")

# テスト1: search_src - 関数14から根ノードまで
print("\n" + "="*80)
print("テスト1: search_src - 関数14から根ノード（呼び出し元）まで")
print("="*80)
print_src_trace_results(graph, jelly_obj, FunctionID(14), show_all_paths=True)

# テスト2: search_dst - 関数14から葉ノードまで
print("\n" + "="*80)
print("テスト2: search_dst - 関数14から葉ノード（呼び出し先）まで")
print("="*80)
print_dst_trace_results(graph, jelly_obj, FunctionID(14), show_all_paths=True)


# テスト3: プログラム的に経路を取得して処理
print("\n" + "="*80)
print("テスト3: 関数14の経路を取得してプログラム的に処理")
print("="*80)

# 呼び出し元への経路
src_paths = search_src(graph, jelly_obj, FunctionID(14))
print(f"\n📤 呼び出し元への経路数: {len(src_paths)}")
if src_paths:
    print(f"   例: 経路1")
    print(f"   - path: {src_paths[0].path}")
    print(f"   - total_weight: {src_paths[0].total_weight}")
    print(f"   - root_node: {src_paths[0].root_node}")
    print(f"   - parents数: {len(src_paths[0].parents)}")
    if src_paths[0].parents:
        first_parent_id = list(src_paths[0].parents.keys())[0]
        first_parent_loc = src_paths[0].parents[first_parent_id]
        print(f"   - 親ノード例: {first_parent_id} -> {first_parent_loc}")

# 呼び出し先への経路
dst_paths = search_dst(graph, jelly_obj, FunctionID(14))
print(f"\n📥 呼び出し先への経路数: {len(dst_paths)}")
if dst_paths:
    print(f"   例: 経路1")
    print(f"   - path: {dst_paths[0].path}")
    print(f"   - total_weight: {dst_paths[0].total_weight}")
    print(f"   - children数: {len(dst_paths[0].children)}")
    if dst_paths[0].children:
        first_child_id = list(dst_paths[0].children.keys())[0]
        first_child_loc = dst_paths[0].children[first_child_id]
        print(f"   - 子ノード例: {first_child_id} -> {first_child_loc}")

# テスト6: 根ノードから葉ノードまでの経路
print("\n" + "="*80)
print("テスト6: 根ノード2から葉ノードまでの経路")
print("="*80)
if 2 in root_nodes:
    print_dst_trace_results(graph, jelly_obj, FunctionID(2), show_all_paths=False)
else:
    print("⚠️  関数2は根ノードではありません")

print("\n✅ テスト完了!")
