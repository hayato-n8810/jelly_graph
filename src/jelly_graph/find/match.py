from pathlib import Path

from ..classes.jelly import FileID, FunctionID, JellyObject


def match_function(
    jelly_obj: JellyObject,
    filepath: str | Path,
    start_row: int,
    end_row: int,
) -> FunctionID | None:
    """
    指定したファイルパスと行範囲に一致する関数IDを返す
    
    Args:
        jelly_obj: JellyObjectインスタンス
        filepath: 検索対象のファイルパス（絶対パスまたは相対パス）
        start_row: 関数の開始行
        end_row: 関数の終了行
    
    Returns:
        一致する関数ID、見つからない場合はNone
    """
    # ファイルパスを正規化（先頭の/を削除）
    target_path_str = str(filepath).lstrip("/")
    
    # ファイルIDを探す（相対パスで比較）
    target_file_id: FileID | None = None
    for file_id, file_path in jelly_obj.files.items():
        # 両方のパスから先頭の/を削除して比較
        normalized_file_path = str(file_path).lstrip("/")
        if normalized_file_path == target_path_str:
            target_file_id = file_id
            break
    
    # ファイルが見つからない場合
    if target_file_id is None:
        return None
    
    # 指定したファイル内で、開始行と終了行が一致する関数を探す
    for func_id, loc in jelly_obj.functions.items():
        if (
            loc.fileid == target_file_id
            and loc.startrow == start_row
            and loc.endrow == end_row
        ):
            return func_id
    
    # 一致する関数が見つからない場合
    return None
