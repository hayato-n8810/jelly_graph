import csv
from pathlib import Path

from ..classes.codeql import CodeQLFunction


def load_codeql(filepath: str | Path) -> CodeQLFunction:
    """
    CodeQL結果のCSVファイルを読み込み、CodeQLFunctionオブジェクトを返す
    
    Args:
        filepath: CodeQL結果CSVファイルのパス
    
    Returns:
        CodeQLFunctionオブジェクト
        
    CSVフォーマット:
        - 5列目: ファイルパス
        - 6列目: 開始行
        - 8列目: 終了行
    """
    functions: list[tuple[str, tuple[int, int]]] = []
    
    with open(filepath, "r", encoding="utf-8") as f:
        csv_reader = csv.reader(f)
        
        for row in csv_reader:
            if len(row) < 8:
                # 列数が不足している行はスキップ
                continue
            
            # 5列目(インデックス4): ファイルパス
            file_path = row[4]
            
            # 6列目(インデックス5): 開始行
            try:
                start_row = int(row[5])
            except ValueError:
                # 数値に変換できない場合はスキップ
                continue
            
            # 8列目(インデックス7): 終了行
            try:
                end_row = int(row[7])
            except ValueError:
                # 数値に変換できない場合はスキップ
                continue
            
            functions.append((file_path, (start_row, end_row)))
    
    return CodeQLFunction(function=functions)
