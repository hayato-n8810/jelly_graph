from dataclasses import dataclass
from .jelly import FunctionID, location

@dataclass
class SrcPathInfo:
    """指定した関数を呼び出している関数の経路情報"""
    path: list[FunctionID]  # 経路（関数IDのリスト）
    total_weight: int  # 経路の総重み
    root_node: FunctionID  # 根ノード
    parents: dict[FunctionID, location] # 親ノードの経路情報リスト

@dataclass
class DstPathInfo:
    """指定した関数が呼び出している関数の経路情報"""
    path: list[FunctionID]  # 経路（関数IDのリスト）
    total_weight: int  # 経路の総重み
    children: dict[FunctionID, location] # 子ノードの経路情報リスト
