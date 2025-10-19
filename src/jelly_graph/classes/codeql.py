from dataclasses import dataclass

@dataclass
class CodeQLFunction:
    """CodeQLから必要要素を抜き出したオブジェクト"""

    function: list[tuple[str, tuple[int, int]]]  # 関数名と（開始行、終了行）