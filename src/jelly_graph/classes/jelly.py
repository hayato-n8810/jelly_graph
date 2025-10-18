from dataclasses import dataclass
from typing import NewType

FileID = NewType("FileID", int)
FunctionID = NewType("FunctionID", int)
CallID = NewType("CallID", int)

@dataclass
class location:
    """関数・呼び出しの位置情報"""

    fileid: FileID
    startrow: int
    startcolumn: int
    endrow: int
    endcolumn: int

@dataclass
class JellyObject:
    """jellyから必要要素を抜き出したオブジェクト"""

    files: dict[FileID, str]
    functions: dict[FunctionID, location]
    calls: dict[CallID, location]
    fun2fun: list[list[FunctionID, FunctionID]]
    call2fun: list[list[CallID, FunctionID]]

@dataclass
class dependMap:
    """依存関係マップ"""

    dependMap: dict[(FunctionID, FunctionID), int]