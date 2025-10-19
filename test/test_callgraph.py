"""build_callgraph.pyのテストスクリプト"""
import sys
from pathlib import Path

# srcディレクトリをパスに追加
sys.path.insert(0, str(Path(__file__).parent / "src"))

from jelly_graph.weight.mapping import load_jelly
from jelly_graph.weight.weight import dependency_weights
from jelly_graph.graph.build_callgraph import (
    build_callgraph,
    build_meta_callgraph,
    get_graph_statistics,
    get_node_statistics,
    get_most_called_functions,
    get_most_calling_functions,
    get_heaviest_edges,
    find_cycles,
    calculate_pagerank,
    get_strongly_connected_components,
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

# グラフを構築
print("\n=== コールグラフ構築中... ===")
graph = build_callgraph(depend_map)
graph_with_meta = build_meta_callgraph(depend_map, jelly_obj)

# グラフの統計情報
print("\n=== グラフ統計情報 ===")
stats = get_graph_statistics(graph)
print(f"ノード数（関数数）: {stats['num_nodes']}")
print(f"エッジ数（依存関係数）: {stats['num_edges']}")
print(f"総呼び出し回数: {stats['total_weight']}")
print(f"平均呼び出し回数: {stats['average_weight']:.2f}")
print(f"グラフ密度: {stats['density']:.4f}")
print(f"DAG（非循環）: {stats['is_dag']}")
print(f"強連結成分数: {stats['num_strongly_connected_components']}")
print(f"弱連結成分数: {stats['num_weakly_connected_components']}")

# 最も重いエッジ（頻繁な呼び出し）
print("\n=== 最も頻繁な呼び出し Top 5 ===")
heaviest = get_heaviest_edges(graph, top_n=5)
for i, (src, dst, weight) in enumerate(heaviest, 1):
    src_loc = jelly_obj.functions.get(src)
    dst_loc = jelly_obj.functions.get(dst)
    src_file = jelly_obj.files.get(src_loc.fileid) if src_loc else "不明"
    dst_file = jelly_obj.files.get(dst_loc.fileid) if dst_loc else "不明"
    
    print(f"{i}. 関数 {src} -> 関数 {dst}: {weight}回")
    print(f"   {Path(src_file).name if src_file != '不明' else src_file}")

# 最も呼ばれている関数
print("\n=== 最も呼ばれている関数 Top 5 ===")
most_called = get_most_called_functions(graph, top_n=5)
for i, (func_id, count) in enumerate(most_called, 1):
    loc = jelly_obj.functions.get(func_id)
    file_path = jelly_obj.files.get(loc.fileid) if loc else "不明"
    print(f"{i}. 関数 {func_id}: {count}回呼ばれる ({Path(file_path).name if file_path != '不明' else file_path})")

# 最も呼び出している関数
print("\n=== 最も呼び出している関数 Top 5 ===")
most_calling = get_most_calling_functions(graph, top_n=5)
for i, (func_id, count) in enumerate(most_calling, 1):
    loc = jelly_obj.functions.get(func_id)
    file_path = jelly_obj.files.get(loc.fileid) if loc else "不明"
    print(f"{i}. 関数 {func_id}: {count}回呼び出す ({Path(file_path).name if file_path != '不明' else file_path})")

# 特定のノードの統計情報
test_func_id = FunctionID(14)
print(f"\n=== 関数 {test_func_id} の詳細情報 ===")
node_stats = get_node_statistics(graph, test_func_id)
print(f"呼び出す関数の数（out-degree）: {node_stats['out_degree']}")
print(f"呼び出される関数の数（in-degree）: {node_stats['in_degree']}")
print(f"総呼び出し回数（weighted out-degree）: {node_stats['weighted_out_degree']}")
print(f"総呼ばれた回数（weighted in-degree）: {node_stats['weighted_in_degree']}")

# サイクル検出
print("\n=== サイクル（循環参照）検出 ===")
cycles = find_cycles(graph)
if cycles:
    print(f"検出されたサイクル数: {len(cycles)}")
    for i, cycle in enumerate(cycles[:3], 1):  # 最初の3つだけ表示
        print(f"サイクル {i}: {' -> '.join(map(str, cycle))} -> {cycle[0]}")
else:
    print("サイクルは検出されませんでした")

# PageRank計算
print("\n=== PageRank（重要度）Top 5 ===")
pagerank = calculate_pagerank(graph)
top_pagerank = sorted(pagerank.items(), key=lambda x: x[1], reverse=True)[:5]
for i, (func_id, score) in enumerate(top_pagerank, 1):
    loc = jelly_obj.functions.get(func_id)
    file_path = jelly_obj.files.get(loc.fileid) if loc else "不明"
    print(f"{i}. 関数 {func_id}: {score:.4f} ({Path(file_path).name if file_path != '不明' else file_path})")

# 強連結成分
print("\n=== 強連結成分 ===")
sccs = get_strongly_connected_components(graph)
large_sccs = [scc for scc in sccs if len(scc) > 1]
if large_sccs:
    print(f"サイズ > 1 の強連結成分数: {len(large_sccs)}")
    for i, scc in enumerate(large_sccs[:3], 1):
        print(f"成分 {i} (サイズ {len(scc)}): {sorted(scc)}")
else:
    print("サイズ > 1 の強連結成分はありません（すべての関数が独立）")

print("\n✅ コールグラフ構築・分析完了！")
