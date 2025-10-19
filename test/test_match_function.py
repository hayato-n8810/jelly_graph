"""
match_function関数のテスト
"""

from pathlib import Path
from jelly_graph.weight.mapping import load_jelly
from jelly_graph.find import match_function


def main():
    # サンプルデータの読み込み
    jelly_obj = load_jelly("sample/jelly_result_single.json")
    
    print("=== match_function テスト ===\n")
    
    # ファイルとその中の関数を確認
    print("利用可能なファイル:")
    for file_id, filepath in jelly_obj.files.items():
        print(f"  FileID {file_id}: {filepath}")
    
    print("\n登録されている関数:")
    for func_id, loc in list(jelly_obj.functions.items())[:5]:  # 最初の5個のみ表示
        filepath = jelly_obj.files[loc.fileid]
        print(f"  FunctionID {func_id}: {Path(filepath).name} (行 {loc.startrow}-{loc.endrow})")
    print(f"  ... (全{len(jelly_obj.functions)}個の関数)")
    
    # テスト1: 最初の関数を検索
    if jelly_obj.functions:
        first_func_id = list(jelly_obj.functions.keys())[0]
        first_loc = jelly_obj.functions[first_func_id]
        first_filepath = jelly_obj.files[first_loc.fileid]
        
        print(f"\n--- テスト1: 最初の関数を検索 ---")
        print(f"検索条件: {Path(first_filepath).name}, 行 {first_loc.startrow}-{first_loc.endrow}")
        
        result = match_function(
            jelly_obj,
            first_filepath,
            first_loc.startrow,
            first_loc.endrow
        )
        
        if result == first_func_id:
            print(f"✅ 成功: FunctionID {result} を発見")
        else:
            print(f"❌ 失敗: 期待 {first_func_id}, 取得 {result}")
    
    # テスト2: 存在しないファイルパス
    print(f"\n--- テスト2: 存在しないファイルパス ---")
    result = match_function(jelly_obj, "/nonexistent/file.py", 1, 10)
    if result is None:
        print("✅ 成功: None を返した")
    else:
        print(f"❌ 失敗: {result} を返した（None が期待される）")
    
    # テスト3: 存在しない行範囲
    if jelly_obj.functions:
        first_loc = jelly_obj.functions[list(jelly_obj.functions.keys())[0]]
        first_filepath = jelly_obj.files[first_loc.fileid]
        
        print(f"\n--- テスト3: 存在しない行範囲 ---")
        result = match_function(jelly_obj, first_filepath, 99999, 99999)
        if result is None:
            print("✅ 成功: None を返した")
        else:
            print(f"❌ 失敗: {result} を返した（None が期待される）")


if __name__ == "__main__":
    main()
