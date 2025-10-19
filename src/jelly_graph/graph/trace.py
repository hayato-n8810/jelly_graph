import networkx as nx
from typing import Any

from ..classes.jelly import FunctionID, JellyObject, location
from ..classes.trace import SrcPathInfo, DstPathInfo


def find_root_nodes(graph: nx.DiGraph) -> set[FunctionID]:
    """
    グラフ内の根ノード（入次数0のノード）を見つける
    
    Args:
        graph: NetworkXの有向グラフ
    
    Returns:
        根ノードのIDのセット
    """
    return {node for node in graph.nodes() if graph.in_degree(node) == 0}


def find_leaf_nodes(graph: nx.DiGraph) -> set[FunctionID]:
    """
    グラフ内の葉ノード（出次数0のノード）を見つける
    
    Args:
        graph: NetworkXの有向グラフ
    
    Returns:
        葉ノードのIDのセット
    """
    return {node for node in graph.nodes() if graph.out_degree(node) == 0}


def search_src(
    graph: nx.DiGraph,
    jelly_obj: JellyObject,
    target_func_id: FunctionID,
    max_depth: int = 100
) -> list[SrcPathInfo]:
    """
    指定した関数から根ノード（呼び出し元を遡る）までの全経路を探索
    
    Args:
        graph: NetworkXの有向グラフ（重み付き）
        jelly_obj: JellyObjectインスタンス（location情報取得用）
        target_func_id: 開始関数ID
        max_depth: 最大探索深度（循環検出用）
    
    Returns:
        全経路の情報リスト（SrcPathInfo）
    """
    if target_func_id not in graph.nodes():
        raise ValueError(f"関数ID {target_func_id} はグラフに存在しません")
    
    # 根ノードを検出
    root_nodes = find_root_nodes(graph)
    
    # 開始ノードが既に根ノードの場合
    if target_func_id in root_nodes:
        return [SrcPathInfo(
            path=[target_func_id],
            total_weight=0,
            root_node=target_func_id,
            parents={}
        )]
    
    # 全経路を格納
    all_paths: list[SrcPathInfo] = []
    
    # 訪問済みの経路を追跡（重複排除用）
    visited_paths: set[tuple[FunctionID, ...]] = set()
    
    def dfs(
        current_node: FunctionID,
        current_path: list[FunctionID],
        current_weight: int,
        visited_in_path: set[FunctionID],
        parents_info: dict[FunctionID, location]
    ) -> None:
        """
        深さ優先探索で根ノードまでの経路を探索
        
        Args:
            current_node: 現在のノード
            current_path: 現在の経路
            current_weight: 現在の経路の総重み
            visited_in_path: 現在の経路で訪問済みのノード（循環検出用）
            parents_info: 親ノードのlocation情報
        """
        # 最大深度チェック
        if len(current_path) > max_depth:
            return
        
        # 根ノードに到達した場合
        if current_node in root_nodes:
            path_tuple = tuple(current_path)
            if path_tuple not in visited_paths:
                visited_paths.add(path_tuple)
                all_paths.append(
                    SrcPathInfo(
                        path=current_path.copy(),
                        total_weight=current_weight,
                        root_node=current_node,
                        parents=parents_info.copy()
                    )
                )
            return
        
        # 前方のノード（呼び出し元）を探索
        for predecessor in graph.predecessors(current_node):
            # 循環検出：既に現在の経路で訪問済みの場合はスキップ
            if predecessor in visited_in_path:
                continue
            
            # エッジの重みを取得
            edge_weight = graph[predecessor][current_node].get("weight", 1)
            
            # 親ノードのlocation情報を取得
            new_parents_info = parents_info.copy()
            if predecessor in jelly_obj.functions:
                new_parents_info[predecessor] = jelly_obj.functions[predecessor]
            
            # 次のノードへ進む
            new_path = current_path + [predecessor]
            new_weight = current_weight + edge_weight
            new_visited = visited_in_path | {predecessor}
            
            dfs(predecessor, new_path, new_weight, new_visited, new_parents_info)
    
    # 探索開始
    initial_parents = {}
    if target_func_id in jelly_obj.functions:
        initial_parents[target_func_id] = jelly_obj.functions[target_func_id]
    
    dfs(target_func_id, [target_func_id], 0, {target_func_id}, initial_parents)
    
    return all_paths


def search_dst(
    graph: nx.DiGraph,
    jelly_obj: JellyObject,
    target_func_id: FunctionID,
    max_depth: int = 100
) -> list[DstPathInfo]:
    """
    指定した関数から葉ノード（呼び出し先を辿る）までの全経路を探索
    
    Args:
        graph: NetworkXの有向グラフ（重み付き）
        jelly_obj: JellyObjectインスタンス（location情報取得用）
        target_func_id: 開始関数ID
        max_depth: 最大探索深度（循環検出用）
    
    Returns:
        全経路の情報リスト（DstPathInfo）
    """
    if target_func_id not in graph.nodes():
        raise ValueError(f"関数ID {target_func_id} はグラフに存在しません")
    
    # 葉ノードを検出
    leaf_nodes = find_leaf_nodes(graph)
    
    # 開始ノードが既に葉ノードの場合
    if target_func_id in leaf_nodes:
        children_info = {}
        if target_func_id in jelly_obj.functions:
            children_info[target_func_id] = jelly_obj.functions[target_func_id]
        return [DstPathInfo(
            path=[target_func_id],
            total_weight=0,
            children=children_info
        )]
    
    # 全経路を格納
    all_paths: list[DstPathInfo] = []
    
    # 訪問済みの経路を追跡（重複排除用）
    visited_paths: set[tuple[FunctionID, ...]] = set()
    
    def dfs(
        current_node: FunctionID,
        current_path: list[FunctionID],
        current_weight: int,
        visited_in_path: set[FunctionID],
        children_info: dict[FunctionID, location]
    ) -> None:
        """
        深さ優先探索で葉ノードまでの経路を探索
        
        Args:
            current_node: 現在のノード
            current_path: 現在の経路
            current_weight: 現在の経路の総重み
            visited_in_path: 現在の経路で訪問済みのノード（循環検出用）
            children_info: 子ノードのlocation情報
        """
        # 最大深度チェック
        if len(current_path) > max_depth:
            return
        
        # 葉ノードに到達した場合
        if current_node in leaf_nodes:
            path_tuple = tuple(current_path)
            if path_tuple not in visited_paths:
                visited_paths.add(path_tuple)
                all_paths.append(
                    DstPathInfo(
                        path=current_path.copy(),
                        total_weight=current_weight,
                        children=children_info.copy()
                    )
                )
            return
        
        # 後方のノード（呼び出し先）を探索
        for successor in graph.successors(current_node):
            # 循環検出：既に現在の経路で訪問済みの場合はスキップ
            if successor in visited_in_path:
                continue
            
            # エッジの重みを取得
            edge_weight = graph[current_node][successor].get("weight", 1)
            
            # 子ノードのlocation情報を取得
            new_children_info = children_info.copy()
            if successor in jelly_obj.functions:
                new_children_info[successor] = jelly_obj.functions[successor]
            
            # 次のノードへ進む
            new_path = current_path + [successor]
            new_weight = current_weight + edge_weight
            new_visited = visited_in_path | {successor}
            
            dfs(successor, new_path, new_weight, new_visited, new_children_info)
    
    # 探索開始
    initial_children = {}
    if target_func_id in jelly_obj.functions:
        initial_children[target_func_id] = jelly_obj.functions[target_func_id]
    
    dfs(target_func_id, [target_func_id], 0, {target_func_id}, initial_children)
    
    return all_paths


def print_src_trace_results(
    graph: nx.DiGraph,
    jelly_obj: JellyObject,
    target_func_id: FunctionID,
    max_depth: int = 100,
    show_all_paths: bool = True
) -> None:
    """
    search_srcの結果を整形して表示
    
    Args:
        graph: NetworkXの有向グラフ（重み付き）
        jelly_obj: JellyObjectインスタンス
        target_func_id: 開始関数ID
        max_depth: 最大探索深度
        show_all_paths: 全経路を表示するか（Falseの場合はサマリのみ）
    """
    paths = search_src(graph, jelly_obj, target_func_id, max_depth)
    
    print(f"\n{'='*80}")
    print(f"関数 {target_func_id} から根ノード（呼び出し元）までの経路探索結果")
    print(f"{'='*80}\n")
    
    if not paths:
        print("⚠️  根ノードへの経路が見つかりませんでした")
        print("   （循環参照のみ、または到達不可能）\n")
        return
    
    # 根ノードごとにグループ化
    paths_by_root: dict[FunctionID, list[SrcPathInfo]] = {}
    for path_info in paths:
        root = path_info.root_node
        if root not in paths_by_root:
            paths_by_root[root] = []
        paths_by_root[root].append(path_info)
    
    print(f"📊 サマリ:")
    print(f"  - 発見された経路数: {len(paths)}")
    print(f"  - 到達可能な根ノード数: {len(paths_by_root)}")
    print()
    
    # 根ノードごとに表示
    for root_id, root_paths in sorted(paths_by_root.items()):
        print(f"🌳 根ノード {root_id} への経路 ({len(root_paths)}件)")
        print(f"   {'-'*76}")
        
        if show_all_paths:
            for i, path_info in enumerate(root_paths, 1):
                # 経路を逆順にして表示（根→開始の順）
                reversed_path = path_info.path[::-1]
                path_str = " → ".join(str(node) for node in reversed_path)
                
                print(f"   [{i}] {path_str}")
                print(f"       総重み: {path_info.total_weight}, 経路長: {len(path_info.path)}")
                print(f"       親ノード数: {len(path_info.parents)}")
        else:
            # サマリのみ表示
            weights = [p.total_weight for p in root_paths]
            lengths = [len(p.path) for p in root_paths]
            print(f"   総重み範囲: {min(weights)} 〜 {max(weights)}")
            print(f"   経路長範囲: {min(lengths)} 〜 {max(lengths)}")
        
        print()
    
    # 全体統計
    all_weights = [p.total_weight for p in paths]
    all_lengths = [len(p.path) for p in paths]
    
    print(f"📈 全体統計:")
    print(f"  重み - 最小: {min(all_weights)}, 最大: {max(all_weights)}, "
          f"平均: {sum(all_weights)/len(all_weights):.2f}")
    print(f"  経路長 - 最小: {min(all_lengths)}, 最大: {max(all_lengths)}, "
          f"平均: {sum(all_lengths)/len(all_lengths):.2f}")
    print()


def print_dst_trace_results(
    graph: nx.DiGraph,
    jelly_obj: JellyObject,
    target_func_id: FunctionID,
    max_depth: int = 100,
    show_all_paths: bool = True
) -> None:
    """
    search_dstの結果を整形して表示
    
    Args:
        graph: NetworkXの有向グラフ（重み付き）
        jelly_obj: JellyObjectインスタンス
        target_func_id: 開始関数ID
        max_depth: 最大探索深度
        show_all_paths: 全経路を表示するか（Falseの場合はサマリのみ）
    """
    paths = search_dst(graph, jelly_obj, target_func_id, max_depth)
    
    print(f"\n{'='*80}")
    print(f"関数 {target_func_id} から葉ノード（呼び出し先）までの経路探索結果")
    print(f"{'='*80}\n")
    
    if not paths:
        print("⚠️  葉ノードへの経路が見つかりませんでした")
        print("   （循環参照のみ、または到達不可能）\n")
        return
    
    print(f"📊 サマリ:")
    print(f"  - 発見された経路数: {len(paths)}")
    print()
    
    # 経路を表示
    if show_all_paths:
        for i, path_info in enumerate(paths, 1):
            path_str = " → ".join(str(node) for node in path_info.path)
            
            print(f"🍃 経路 {i}:")
            print(f"   {path_str}")
            print(f"   総重み: {path_info.total_weight}, 経路長: {len(path_info.path)}")
            print(f"   子ノード数: {len(path_info.children)}")
            print()
    else:
        # サマリのみ表示
        weights = [p.total_weight for p in paths]
        lengths = [len(p.path) for p in paths]
        print(f"   総重み範囲: {min(weights)} 〜 {max(weights)}")
        print(f"   経路長範囲: {min(lengths)} 〜 {max(lengths)}")
        print()
    
    # # 全体統計
    # all_weights = [p.total_weight for p in paths]
    # all_lengths = [len(p.path) for p in paths]
    
    # print(f"📈 全体統計:")
    # print(f"  重み - 最小: {min(all_weights)}, 最大: {max(all_weights)}, "
    #       f"平均: {sum(all_weights)/len(all_weights):.2f}")
    # print(f"  経路長 - 最小: {min(all_lengths)}, 最大: {max(all_lengths)}, "
    #       f"平均: {sum(all_lengths)/len(all_lengths):.2f}")
    # print()

