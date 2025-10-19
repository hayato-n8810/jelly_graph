import networkx as nx
from typing import Any
from pathlib import Path
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

from ..classes.jelly import dependMap, FunctionID, JellyObject


def save_callgraph_image(
    graph: nx.DiGraph,
    output_path: str | Path,
    layout: str = "spring",
    figsize: tuple[int, int] = (16, 12),
    node_size_multiplier: int = 300,
    show_weights: bool = True,
    show_labels: bool = True,
    title: str | None = None,
    dpi: int = 300,
) -> None:
    """
    コールグラフを画像として保存
    
    Args:
        graph: NetworkXの有向グラフ
        output_path: 出力ファイルパス（.png, .pdf, .svg など）
        layout: レイアウトアルゴリズム
                - "spring": バネモデル（デフォルト、バランスが良い）
                - "circular": 円形配置
                - "kamada_kawai": 力学モデル（きれい）
                - "planar": 平面配置
                - "shell": シェル配置
        figsize: 図のサイズ (幅, 高さ)
        node_size_multiplier: ノードサイズの倍率
        show_weights: エッジの重み（呼び出し回数）を表示するか
        show_labels: ノードラベル（関数ID）を表示するか
        title: グラフのタイトル
        dpi: 画像の解像度
    """
    # レイアウトを計算
    if layout == "spring":
        pos = nx.spring_layout(graph, k=1.5, iterations=50, seed=42)
    elif layout == "circular":
        pos = nx.circular_layout(graph)
    elif layout == "kamada_kawai":
        pos = nx.kamada_kawai_layout(graph)
    elif layout == "planar":
        try:
            pos = nx.planar_layout(graph)
        except nx.NetworkXException:
            # 平面グラフでない場合はspringに戻す
            pos = nx.spring_layout(graph, k=1.5, iterations=50, seed=42)
    elif layout == "shell":
        pos = nx.shell_layout(graph)
    else:
        pos = nx.spring_layout(graph, k=1.5, iterations=50, seed=42)
    
    # 図を作成
    plt.figure(figsize=figsize)
    
    # ノードサイズを重み付き入次数に基づいて計算
    node_sizes = []
    for node in graph.nodes():
        weighted_in = sum(
            data.get("weight", 1) for _, _, data in graph.in_edges(node, data=True)
        )
        # 最小サイズを保証
        node_sizes.append(max(300, weighted_in * node_size_multiplier))
    
    # ノードの色を重み付き出次数に基づいて計算
    node_colors = []
    for node in graph.nodes():
        weighted_out = sum(
            data.get("weight", 1) for _, _, data in graph.out_edges(node, data=True)
        )
        node_colors.append(weighted_out)
    
    # ノードを描画
    nx.draw_networkx_nodes(
        graph,
        pos,
        node_size=node_sizes,
        node_color=node_colors,
        cmap=plt.cm.YlOrRd,
        alpha=0.8,
        edgecolors="black",
        linewidths=1.5,
    )
    
    # エッジを描画（重みに応じて太さを変える）
    edges = graph.edges()
    weights = [graph[u][v].get("weight", 1) for u, v in edges]
    max_weight = max(weights) if weights else 1
    
    # 重みに応じてエッジの太さを調整
    edge_widths = [1 + (w / max_weight) * 4 for w in weights]
    
    nx.draw_networkx_edges(
        graph,
        pos,
        width=edge_widths,
        alpha=0.5,
        edge_color="gray",
        arrows=True,
        arrowsize=20,
        arrowstyle="->",
        connectionstyle="arc3,rad=0.1",
    )
    
    # ノードラベルを描画
    if show_labels:
        nx.draw_networkx_labels(
            graph,
            pos,
            font_size=8,
            font_weight="bold",
            font_color="black",
        )
    
    # エッジラベル（重み）を描画
    if show_weights:
        edge_labels = {
            (u, v): f"{d['weight']}"
            for u, v, d in graph.edges(data=True)
            if d.get("weight", 0) > 0
        }
        nx.draw_networkx_edge_labels(
            graph,
            pos,
            edge_labels,
            font_size=6,
            bbox=dict(boxstyle="round,pad=0.3", facecolor="white", alpha=0.7),
        )
    
    # タイトルを設定
    if title:
        plt.title(title, fontsize=16, fontweight="bold", pad=20)
    else:
        plt.title(
            f"コールグラフ ({graph.number_of_nodes()} 関数, {graph.number_of_edges()} 依存関係)",
            fontsize=16,
            fontweight="bold",
            pad=20,
        )
    
    # 凡例を追加
    legend_elements = [
        mpatches.Patch(color="white", label=f"ノードサイズ: 呼ばれた回数"),
        mpatches.Patch(color="white", label=f"ノード色: 呼び出した回数（赤いほど多い）"),
        mpatches.Patch(color="white", label=f"エッジ太さ: 呼び出し回数"),
    ]
    plt.legend(
        handles=legend_elements,
        loc="upper left",
        framealpha=0.9,
        fontsize=10,
    )
    
    plt.axis("off")
    plt.tight_layout()
    
    # 保存
    plt.savefig(output_path, dpi=dpi, bbox_inches="tight", facecolor="white")
    plt.close()


def save_callgraph_with_metadata(
    graph: nx.DiGraph,
    jelly_obj: JellyObject,
    output_path: str | Path,
    layout: str = "spring",
    figsize: tuple[int, int] = (20, 16),
    max_label_length: int = 30,
    show_weights: bool = True,
    title: str | None = None,
    dpi: int = 300,
) -> None:
    """
    メタデータ付きコールグラフを画像として保存（ファイル名付き）
    
    Args:
        graph: NetworkXの有向グラフ（メタデータ付き）
        jelly_obj: JellyObjectインスタンス
        output_path: 出力ファイルパス
        layout: レイアウトアルゴリズム
        figsize: 図のサイズ (幅, 高さ)
        max_label_length: ラベルの最大文字数
        show_weights: エッジの重みを表示するか
        title: グラフのタイトル
        dpi: 画像の解像度
    """
    # レイアウトを計算
    if layout == "spring":
        pos = nx.spring_layout(graph, k=2, iterations=50, seed=42)
    elif layout == "circular":
        pos = nx.circular_layout(graph)
    elif layout == "kamada_kawai":
        pos = nx.kamada_kawai_layout(graph)
    else:
        pos = nx.spring_layout(graph, k=2, iterations=50, seed=42)
    
    # 図を作成
    plt.figure(figsize=figsize)
    
    # ノードサイズとカラーを計算
    node_sizes = []
    node_colors = []
    for node in graph.nodes():
        weighted_in = sum(
            data.get("weight", 1) for _, _, data in graph.in_edges(node, data=True)
        )
        weighted_out = sum(
            data.get("weight", 1) for _, _, data in graph.out_edges(node, data=True)
        )
        node_sizes.append(max(500, weighted_in * 200))
        node_colors.append(weighted_out)
    
    # ノードを描画
    nx.draw_networkx_nodes(
        graph,
        pos,
        node_size=node_sizes,
        node_color=node_colors,
        cmap=plt.cm.YlOrRd,
        alpha=0.8,
        edgecolors="black",
        linewidths=2,
    )
    
    # エッジを描画
    edges = graph.edges()
    weights = [graph[u][v].get("weight", 1) for u, v in edges]
    max_weight = max(weights) if weights else 1
    edge_widths = [1 + (w / max_weight) * 5 for w in weights]
    
    nx.draw_networkx_edges(
        graph,
        pos,
        width=edge_widths,
        alpha=0.5,
        edge_color="gray",
        arrows=True,
        arrowsize=25,
        arrowstyle="->",
        connectionstyle="arc3,rad=0.1",
    )
    
    # ノードラベル（関数ID + ファイル名）を作成
    labels = {}
    for node in graph.nodes():
        if node in jelly_obj.functions:
            loc = jelly_obj.functions[node]
            file_path = jelly_obj.files.get(loc.fileid, "不明")
            file_name = Path(file_path).stem if file_path != "不明" else "不明"
            
            # ラベルを短縮
            if len(file_name) > max_label_length:
                file_name = file_name[:max_label_length-3] + "..."
            
            labels[node] = f"{node}\n{file_name}"
        else:
            labels[node] = str(node)
    
    # ラベルを描画
    nx.draw_networkx_labels(
        graph,
        pos,
        labels,
        font_size=7,
        font_weight="bold",
        font_color="black",
    )
    
    # エッジラベルを描画
    if show_weights:
        edge_labels = {
            (u, v): f"{d['weight']}"
            for u, v, d in graph.edges(data=True)
            if d.get("weight", 0) > 0
        }
        nx.draw_networkx_edge_labels(
            graph,
            pos,
            edge_labels,
            font_size=7,
            bbox=dict(boxstyle="round,pad=0.3", facecolor="yellow", alpha=0.7),
        )
    
    # タイトル
    if title:
        plt.title(title, fontsize=18, fontweight="bold", pad=20)
    else:
        plt.title(
            f"コールグラフ（ファイル情報付き）\n{graph.number_of_nodes()} 関数, {graph.number_of_edges()} 依存関係",
            fontsize=18,
            fontweight="bold",
            pad=20,
        )
    
    # 凡例
    legend_elements = [
        mpatches.Patch(color="white", label=f"ノードサイズ: 呼ばれた回数"),
        mpatches.Patch(color="white", label=f"ノード色: 呼び出した回数"),
        mpatches.Patch(color="white", label=f"エッジ太さ: 呼び出し回数"),
        mpatches.Patch(color="white", label=f"ラベル形式: [関数ID]\\n[ファイル名]"),
    ]
    plt.legend(
        handles=legend_elements,
        loc="upper left",
        framealpha=0.9,
        fontsize=11,
    )
    
    plt.axis("off")
    plt.tight_layout()
    
    # 保存
    plt.savefig(output_path, dpi=dpi, bbox_inches="tight", facecolor="white")
    plt.close()


def save_subgraph_by_function(
    graph: nx.DiGraph,
    jelly_obj: JellyObject,
    func_id: FunctionID,
    output_path: str | Path,
    depth: int = 2,
    layout: str = "spring",
    figsize: tuple[int, int] = (14, 10),
    dpi: int = 300,
) -> None:
    """
    特定の関数を中心としたサブグラフを画像として保存
    
    Args:
        graph: NetworkXの有向グラフ
        jelly_obj: JellyObjectインスタンス
        func_id: 中心となる関数ID
        output_path: 出力ファイルパス
        depth: 探索の深さ（何階層先まで含めるか）
        layout: レイアウトアルゴリズム
        figsize: 図のサイズ
        dpi: 画像の解像度
    """
    if func_id not in graph.nodes():
        raise ValueError(f"関数ID {func_id} はグラフに存在しません")
    
    # サブグラフのノードを収集
    subgraph_nodes = {func_id}
    
    # 前方（呼び出し先）を探索
    current_level = {func_id}
    for _ in range(depth):
        next_level = set()
        for node in current_level:
            next_level.update(graph.successors(node))
        subgraph_nodes.update(next_level)
        current_level = next_level
    
    # 後方（呼び出し元）を探索
    current_level = {func_id}
    for _ in range(depth):
        next_level = set()
        for node in current_level:
            next_level.update(graph.predecessors(node))
        subgraph_nodes.update(next_level)
        current_level = next_level
    
    # サブグラフを抽出
    subgraph = graph.subgraph(subgraph_nodes).copy()
    
    # 中心ノードの情報を取得
    loc = jelly_obj.functions.get(func_id)
    file_name = "不明"
    if loc:
        file_path = jelly_obj.files.get(loc.fileid, "不明")
        file_name = Path(file_path).name if file_path != "不明" else "不明"
    
    # タイトルを設定
    title = f"関数 {func_id} を中心としたコールグラフ (深さ={depth})\n{file_name}"
    
    # グラフを保存（中心ノードを強調）
    save_callgraph_with_metadata(
        subgraph,
        jelly_obj,
        output_path,
        layout=layout,
        figsize=figsize,
        title=title,
        dpi=dpi,
    )
