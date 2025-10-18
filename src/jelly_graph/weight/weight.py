from ..classes.jelly import CallID, dependMap, FunctionID, JellyObject, location


def is_call_in_function(call_loc: location, func_loc: location) -> bool:
    """
    呼び出しが関数内に完全に含まれているかを判定
    
    Args:
        call_loc: 呼び出しの位置情報
        func_loc: 関数の位置情報
    
    Returns:
        呼び出しが関数内に完全に含まれている場合True
    """
    # ファイルIDが一致し、呼び出しの範囲が関数の範囲に完全に含まれる
    return (
        call_loc.fileid == func_loc.fileid
        and func_loc.startrow <= call_loc.startrow
        and call_loc.endrow <= func_loc.endrow
    )


def find_src_function(
    call_loc: location, functions: dict[FunctionID, location]
) -> FunctionID | None:
    """
    呼び出しを含む関数を特定
    
    Args:
        call_loc: 呼び出しの位置情報
        functions: 関数ID -> 位置情報の辞書
    
    Returns:
        呼び出し元の関数ID。見つからない場合はNone
    """
    # 同じファイル内の関数のみをフィルタリング
    candidates = [
        (func_id, func_loc)
        for func_id, func_loc in functions.items()
        if func_loc.fileid == call_loc.fileid
    ]
    
    # 呼び出しを完全に含む関数を探す
    matching_functions = [
        (func_id, func_loc)
        for func_id, func_loc in candidates
        if is_call_in_function(call_loc, func_loc)
    ]
    
    if not matching_functions:
        return None
    
    # 最も範囲が狭い関数を選択（より具体的な関数を優先）
    # 行数が最も少ない関数を選ぶ
    best_match = min(
        matching_functions,
        key=lambda x: (x[1].endrow - x[1].startrow, x[1].endcolumn - x[1].startcolumn),
    )
    
    return best_match[0]


def dependency_weights(jelly_obj: JellyObject) -> dependMap:
    """
    依存関係の重み（呼び出し回数）を計算
    
    Args:
        jelly_obj: JellyObjectインスタンス
    
    Returns:
        dependMapインスタンス（呼び出し元関数ID, 呼び出し先関数ID -> 呼び出し回数）
    """
    # 依存関係マップを初期化
    dependency_counts: dict[tuple[FunctionID, FunctionID], int] = {}
    
    # call2funの各要素を処理
    for call_id, dst_func_id in jelly_obj.call2fun:
        # CallIDから呼び出しの位置情報を取得
        if call_id not in jelly_obj.calls:
            continue  # 呼び出し情報が見つからない場合はスキップ
        
        call_loc = jelly_obj.calls[call_id]
        
        # 呼び出しを含む関数（呼び出し元）を特定
        src_func_id = find_src_function(call_loc, jelly_obj.functions)
        
        if src_func_id is None:
            continue  # 呼び出し元が見つからない場合はスキップ
        
        # 依存関係のキーを作成
        dependency_key = (src_func_id, dst_func_id)
        
        # 呼び出し回数をカウント
        if dependency_key in dependency_counts:
            dependency_counts[dependency_key] += 1
        else:
            dependency_counts[dependency_key] = 1
    
    return dependMap(dependMap=dependency_counts)


def get_dependency(
    depend_map: dependMap, src_id: FunctionID, dst_id: FunctionID
) -> int:
    """
    特定の依存関係の強さ（呼び出し回数）を取得
    
    Args:
        depend_map: 依存関係マップ
        src_id: 呼び出し元関数ID
        dst_id: 呼び出し先関数ID
    
    Returns:
        呼び出し回数（依存関係が存在しない場合は0）
    """
    return depend_map.dependMap.get((src_id, dst_id), 0)


def get_total_dependencies(depend_map: dependMap) -> int:
    """
    総依存関係数（ユニークな呼び出しペアの数）を取得
    
    Args:
        depend_map: 依存関係マップ
    
    Returns:
        依存関係の総数
    """
    return len(depend_map.dependMap)


def get_total_calls(depend_map: dependMap) -> int:
    """
    総呼び出し回数を取得
    
    Args:
        depend_map: 依存関係マップ
    
    Returns:
        すべての呼び出しの合計回数
    """
    return sum(depend_map.dependMap.values())


def get_caller_dependencies(
    depend_map: dependMap, src_id: FunctionID
) -> dict[FunctionID, int]:
    """
    特定の関数が呼び出す関数とその回数を取得
    
    Args:
        depend_map: 依存関係マップ
        src_id: 呼び出し元関数ID
    
    Returns:
        呼び出し先関数ID -> 呼び出し回数の辞書
    """
    return {
        dst: count
        for (src, dst), count in depend_map.dependMap.items()
        if src == src_id
    }


def get_callee_dependencies(
    depend_map: dependMap, dst_id: FunctionID
) -> dict[FunctionID, int]:
    """
    特定の関数を呼び出す関数とその回数を取得
    
    Args:
        depend_map: 依存関係マップ
        dst_id: 呼び出し先関数ID
    
    Returns:
        呼び出し元関数ID -> 呼び出し回数の辞書
    """
    return {
        src: count
        for (src, dst), count in depend_map.dependMap.items()
        if dst == dst_id
    }


def get_top_dependencies(
    depend_map: dependMap, top_n: int = 10
) -> list[tuple[FunctionID, FunctionID, int]]:
    """
    呼び出し回数の多い依存関係上位N件を取得
    
    Args:
        depend_map: 依存関係マップ
        top_n: 取得する件数（デフォルト: 10）
    
    Returns:
        (呼び出し元関数ID, 呼び出し先関数ID, 呼び出し回数)のリスト（降順）
    """
    sorted_deps = sorted(
        [(caller, callee, count) for (caller, callee), count in depend_map.dependMap.items()],
        key=lambda x: x[2],
        reverse=True,
    )
    return sorted_deps[:top_n]
