from pathlib import Path

from ..classes.codeql import CodeQLFunction
from ..classes.jelly import FunctionID, JellyObject
from .match import match_function
from .ql_function import load_codeql


def match_codeql_to_jelly(
    codeql_result: CodeQLFunction,
    jelly_obj: JellyObject,
    base_path: str | Path | None = None,
) -> list[tuple[str, tuple[int, int], FunctionID | None]]:
    """
    CodeQL結果とJellyObjectの関数を紐付ける
    
    Args:
        codeql_result: CodeQLFunctionオブジェクト
        jelly_obj: JellyObjectインスタンス
        base_path: ファイルパスの基準となるディレクトリ（オプション）
    
    Returns:
        (ファイルパス, (開始行, 終了行), FunctionID | None) のリスト
        FunctionIDがNoneの場合は、JellyObject中に対応する関数が存在しない
    """
    results: list[tuple[str, tuple[int, int], FunctionID | None]] = []
    
    for filepath, (start_row, end_row) in codeql_result.function:
        # base_pathが指定されている場合、ファイルパスを絶対パスに変換
        if base_path is not None:
            full_path = Path(base_path) / filepath.lstrip("/")
        else:
            full_path = Path(filepath)
        
        # match_functionを使って関数IDを検索
        func_id = match_function(jelly_obj, full_path, start_row, end_row)
        
        results.append((filepath, (start_row, end_row), func_id))
    
    return results


def load_and_match_codeql(
    csv_filepath: str | Path,
    jelly_obj: JellyObject,
    base_path: str | Path | None = None,
) -> list[tuple[str, tuple[int, int], FunctionID | None]]:
    """
    CSVファイルを読み込み、JellyObjectの関数と紐付ける
    
    Args:
        csv_filepath: CodeQL結果CSVファイルのパス
        jelly_obj: JellyObjectインスタンス
        base_path: ファイルパスの基準となるディレクトリ（オプション）
    
    Returns:
        (ファイルパス, (開始行, 終了行), FunctionID | None) のリスト
        FunctionIDがNoneの場合は、JellyObject中に対応する関数が存在しない
    """
    # CSVファイルを読み込み
    codeql_result = load_codeql(csv_filepath)
    
    # 紐付けを実行
    return match_codeql_to_jelly(codeql_result, jelly_obj, base_path)


def get_matched_function_ids(
    csv_filepath: str | Path,
    jelly_obj: JellyObject,
    base_path: str | Path | None = None,
) -> list[FunctionID]:
    """
    CSVファイルからマッチした関数IDのみを取得
    
    Args:
        csv_filepath: CodeQL結果CSVファイルのパス
        jelly_obj: JellyObjectインスタンス
        base_path: ファイルパスの基準となるディレクトリ（オプション）
    
    Returns:
        マッチした関数IDのリスト（Noneは除外）
    """
    results = load_and_match_codeql(csv_filepath, jelly_obj, base_path)
    return [func_id for _, _, func_id in results if func_id is not None]


def get_unmatched_functions(
    csv_filepath: str | Path,
    jelly_obj: JellyObject,
    base_path: str | Path | None = None,
) -> list[tuple[str, tuple[int, int]]]:
    """
    CSVファイルからマッチしなかった関数情報を取得
    
    Args:
        csv_filepath: CodeQL結果CSVファイルのパス
        jelly_obj: JellyObjectインスタンス
        base_path: ファイルパスの基準となるディレクトリ（オプション）
    
    Returns:
        マッチしなかった(ファイルパス, (開始行, 終了行))のリスト
    """
    results = load_and_match_codeql(csv_filepath, jelly_obj, base_path)
    return [(filepath, (start_row, end_row)) 
            for filepath, (start_row, end_row), func_id in results 
            if func_id is None]
