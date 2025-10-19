import networkx as nx
from typing import Any

from ..classes.jelly import dependMap, FunctionID, JellyObject


def build_callgraph(depend_map: dependMap) -> nx.DiGraph:
    """
    dependMapから重み付き有向グラフを構築
    
    Args:
        depend_map: 依存関係マップ
    
    Returns:
        NetworkXの有向グラフ（DiGraph）
        - ノード: 関数ID
        - エッジ: 呼び出し関係（重み付き）
    """
    # 有向グラフを作成
    graph = nx.DiGraph()
    
    # 依存関係マップの各エントリをエッジとして追加
    for (src_func_id, dst_func_id), weight in depend_map.dependMap.items():
        # エッジを追加（weightは呼び出し回数）
        graph.add_edge(src_func_id, dst_func_id, weight=weight)
    
    return graph


def build_meta_callgraph(
    depend_map: dependMap, jelly_obj: JellyObject
) -> nx.DiGraph:
    """
    メタデータ付きの重み付き有向グラフを構築
    
    Args:
        depend_map: 依存関係マップ
        jelly_obj: JellyObjectインスタンス（メタデータ取得用）
    
    Returns:
        NetworkXの有向グラフ（DiGraph）
        - ノード属性: ファイル名、行範囲など
        - エッジ属性: 呼び出し回数（weight）
    """
    # 有向グラフを作成
    graph = nx.DiGraph()
    
    # 依存関係マップの各エントリをエッジとして追加
    for (src_func_id, dst_func_id), weight in depend_map.dependMap.items():
        # エッジを追加
        graph.add_edge(src_func_id, dst_func_id, weight=weight)
    
    # ノードにメタデータを追加
    for func_id in graph.nodes():
        if func_id in jelly_obj.functions:
            loc = jelly_obj.functions[func_id]
            file_path = jelly_obj.files.get(loc.fileid, "不明")
            
            # ノード属性を設定
            graph.nodes[func_id]["file"] = file_path
            graph.nodes[func_id]["start_row"] = loc.startrow
            graph.nodes[func_id]["end_row"] = loc.endrow
            graph.nodes[func_id]["start_col"] = loc.startcolumn
            graph.nodes[func_id]["end_col"] = loc.endcolumn
            graph.nodes[func_id]["lines"] = loc.endrow - loc.startrow + 1
    
    return graph


def get_node_statistics(graph: nx.DiGraph, node_id: FunctionID) -> dict[str, Any]:
    """
    特定のノード（関数）の統計情報を取得
    
    Args:
        graph: NetworkXの有向グラフ
        node_id: 関数ID
    
    Returns:
        ノードの統計情報
    """
    if node_id not in graph.nodes():
        return {}
    
    stats = {
        "in_degree": graph.in_degree(node_id),  # 呼ばれる回数（ユニーク）
        "out_degree": graph.out_degree(node_id),  # 呼び出す回数（ユニーク）
    }
    
    # 重み付き次数（実際の呼び出し回数の合計）
    stats["weighted_in_degree"] = sum(
        data.get("weight", 0) for _, _, data in graph.in_edges(node_id, data=True)
    )
    stats["weighted_out_degree"] = sum(
        data.get("weight", 0) for _, _, data in graph.out_edges(node_id, data=True)
    )
    
    return stats



def filter_graph_by_file(
    graph: nx.DiGraph, file_id_or_path: int | str
) -> nx.DiGraph:
    """
    特定のファイルに属する関数のみを含むサブグラフを抽出
    
    Args:
        graph: NetworkXの有向グラフ（メタデータ付き）
        file_id_or_path: ファイルIDまたはファイルパス
    
    Returns:
        フィルタリングされたサブグラフ
    """
    # フィルタ対象のノードを選択
    if isinstance(file_id_or_path, int):
        # ファイルIDで比較（メタデータが必要）
        nodes_to_keep = [
            node for node in graph.nodes()
            if graph.nodes[node].get("file", "").endswith(str(file_id_or_path))
        ]
    else:
        # ファイルパスで比較
        nodes_to_keep = [
            node for node in graph.nodes()
            if file_id_or_path in graph.nodes[node].get("file", "")
        ]
    
    return graph.subgraph(nodes_to_keep).copy()


def calculate_pagerank(graph: nx.DiGraph, weight_key: str = "weight") -> dict[FunctionID, float]:
    """
    PageRankアルゴリズムで関数の重要度を計算
    
    Args:
        graph: NetworkXの有向グラフ
        weight_key: 重みのキー（デフォルト: "weight"）
    
    Returns:
        関数ID -> PageRankスコアの辞書
    """
    return nx.pagerank(graph, weight=weight_key)


