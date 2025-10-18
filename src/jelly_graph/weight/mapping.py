from pathlib import Path
from typing import Any

from ..classes.jelly import (
    CallID,
    FileID,
    FunctionID,
    JellyObject,
    location,
)
from ..utils.file_io import json_load

def parse_location(location_str: str) -> location:
    """
    位置情報文字列をlocationオブジェクトに変換
    
    Args:
        location_str: "fileID:startRow:startColumn:endRow:endColumn"形式の文字列
    
    Returns:
        locationオブジェクト
    """
    parts = location_str.split(":")
    return location(
        fileid=FileID(int(parts[0])),
        startrow=int(parts[1]),
        startcolumn=int(parts[2]),
        endrow=int(parts[3]),
        endcolumn=int(parts[4]),
    )


def mapping_jelly(json_data: dict[str, Any]) -> JellyObject:
    """
    Jelly JSONデータをJellyObjectにマッピング
    
    Args:
        json_data: Jelly形式のJSON辞書
    
    Returns:
        JellyObjectインスタンス
    """
    # filesリストをFileID -> ファイルパスの辞書に変換
    files = {FileID(i): filepath for i, filepath in enumerate(json_data["files"])}
    
    # functionsをFunctionID -> locationの辞書に変換
    functions = {
        FunctionID(int(func_id)): parse_location(loc_str)
        for func_id, loc_str in json_data["functions"].items()
    }
    
    # callsをCallID -> locationの辞書に変換
    calls = {
        CallID(int(call_id)): parse_location(loc_str)
        for call_id, loc_str in json_data["calls"].items()
    }
    
    # fun2funをリストに変換（各要素を[FunctionID, FunctionID]に）
    fun2fun = [
        [FunctionID(src), FunctionID(dst)]
        for src, dst in json_data["fun2fun"]
    ]
    
    # call2funをリストに変換（各要素を[CallID, FunctionID]に）
    call2fun = [
        [CallID(call), FunctionID(func)]
        for call, func in json_data["call2fun"]
    ]
    
    return JellyObject(
        files=files,
        functions=functions,
        calls=calls,
        fun2fun=fun2fun,
        call2fun=call2fun,
    )


def load_jelly(filepath: str | Path) -> JellyObject:
    """
    JSONファイルからJellyObjectを読み込み
    
    Args:
        filepath: JSONファイルのパス
    
    Returns:
        JellyObjectインスタンス
    """
    json_data = json_load(filepath)

    return mapping_jelly(json_data)
