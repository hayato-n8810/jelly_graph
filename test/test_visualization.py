"""グラフ画像出力のテストスクリプト"""
from pathlib import Path

from jelly_graph.weight.mapping import load_jelly
from jelly_graph.weight.weight import dependency_weights
from jelly_graph.graph.build_callgraph import (
    build_callgraph,
    build_meta_callgraph,
)
from jelly_graph.graph.plot import (
    save_callgraph_image,
    save_callgraph_with_metadata,
    save_subgraph_by_function,
)
from jelly_graph.classes.jelly import FunctionID

# 出力ディレクトリを作成
output_dir = Path(__file__).parents[1] / "output"
output_dir.mkdir(exist_ok=True)

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

# 1. 基本的なコールグラフを出力
print("\n=== 画像出力中... ===")
print("1. 基本コールグラフ（Spring レイアウト）...")
save_callgraph_image(
    graph,
    output_dir / "callgraph_spring.png",
    layout="spring",
    title="コールグラフ - Spring レイアウト",
)

print("2. 基本コールグラフ（Circular レイアウト）...")
save_callgraph_image(
    graph,
    output_dir / "callgraph_circular.png",
    layout="circular",
    title="コールグラフ - Circular レイアウト",
)

print("3. 基本コールグラフ（Kamada-Kawai レイアウト）...")
save_callgraph_image(
    graph,
    output_dir / "callgraph_kamada.png",
    layout="kamada_kawai",
    title="コールグラフ - Kamada-Kawai レイアウト",
)

# 2. メタデータ付きコールグラフを出力
print("4. メタデータ付きコールグラフ...")
save_callgraph_with_metadata(
    graph_with_meta,
    jelly_obj,
    output_dir / "callgraph_with_metadata.png",
    layout="spring",
    title="コールグラフ（ファイル名付き）",
)

# 3. 特定の関数を中心としたサブグラフを出力
print("5. 関数14を中心としたサブグラフ（深さ2）...")
save_subgraph_by_function(
    graph_with_meta,
    jelly_obj,
    FunctionID(14),
    output_dir / "subgraph_func14_depth2.png",
    depth=2,
)

print("6. 関数17を中心としたサブグラフ（深さ1）...")
save_subgraph_by_function(
    graph_with_meta,
    jelly_obj,
    FunctionID(17),
    output_dir / "subgraph_func17_depth1.png",
    depth=1,
)

# 4. 高解像度版を出力
print("7. 高解像度コールグラフ（PDF形式）...")
save_callgraph_image(
    graph,
    output_dir / "callgraph_high_res.pdf",
    layout="spring",
    figsize=(20, 16),
    dpi=600,
    title="高解像度コールグラフ",
)

# 5. 重みラベルなしバージョン
print("8. シンプル版（重みラベルなし）...")
save_callgraph_image(
    graph,
    output_dir / "callgraph_simple.png",
    layout="spring",
    show_weights=False,
    title="コールグラフ（シンプル版）",
)

print(f"\n✅ すべての画像を {output_dir} に出力しました！")
print(f"\n出力されたファイル:")
for file in sorted(output_dir.glob("*")):
    print(f"  - {file.name}")
