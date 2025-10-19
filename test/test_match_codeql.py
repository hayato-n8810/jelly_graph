"""
CSVファイルとJellyObjectの紐付けテスト
"""

from pathlib import Path
from jelly_graph.weight.mapping import load_jelly
from jelly_graph.find.match_codeql import (
    load_and_match_codeql,
    get_matched_function_ids,
    get_unmatched_functions,
)


def main():
    print("=== CodeQL結果とJellyObjectの紐付けテスト ===\n")
    
    # データの読み込み
    jelly_obj = load_jelly("sample/jelly_result_single.json")
    
    print(f"JellyObject: {len(jelly_obj.files)}ファイル, {len(jelly_obj.functions)}関数\n")
    
    # base_pathの設定（CSVのパスがjelly_result_single.jsonのファイルパスと合うように）
    # jelly_result_single.jsonのファイルパスの例を確認
    first_file = list(jelly_obj.files.values())[0]
    print(f"JellyObjectの最初のファイルパス: {first_file}")
    
    # パスの構造から基準パスを推測
    # 例: "packages/react-reconciler/src/ReactFiberHydrationDiffs.js"
    # CSVのパス: "/packages/react-reconciler/src/ReactFiberHydrationDiffs.js"
    # base_pathは不要（もしくはプロジェクトルート）
    
    print("\n--- テスト1: すべての紐付け結果を取得 ---")
    results = load_and_match_codeql("sample/ql_result.csv", jelly_obj)
    
    matched_count = sum(1 for _, _, func_id in results if func_id is not None)
    unmatched_count = sum(1 for _, _, func_id in results if func_id is None)
    
    print(f"総数: {len(results)}件")
    print(f"マッチ: {matched_count}件")
    print(f"未マッチ: {unmatched_count}件\n")
    
    for i, (filepath, (start_row, end_row), func_id) in enumerate(results, 1):
        filename = filepath.split("/")[-1]
        status = f"✅ FunctionID {func_id}" if func_id is not None else "❌ 未マッチ"
        print(f"{i}. {filename} (行 {start_row}-{end_row}): {status}")
    
    print("\n--- テスト2: マッチした関数IDのみを取得 ---")
    matched_ids = get_matched_function_ids("sample/ql_result.csv", jelly_obj)
    print(f"マッチした関数ID数: {len(matched_ids)}")
    if matched_ids:
        print(f": {matched_ids}")
    
    print("\n--- テスト3: 未マッチの関数情報を取得 ---")
    unmatched = get_unmatched_functions("sample/ql_result.csv", jelly_obj)
    print(f"未マッチの関数数: {len(unmatched)}")
    if unmatched:
        print("最初の3件:")
        for i, (filepath, (start_row, end_row)) in enumerate(unmatched[:3], 1):
            filename = filepath.split("/")[-1]
            print(f"{i}. {filename} (行 {start_row}-{end_row})")
    
    # マッチ率の計算
    if results:
        match_rate = (matched_count / len(results)) * 100
        print(f"\n--- マッチ率 ---")
        print(f"{match_rate:.1f}% ({matched_count}/{len(results)})")
    
    # マッチした関数の詳細情報を表示
    if matched_ids:
        print(f"\n--- マッチした関数の詳細（最初の3個）---")
        for func_id in matched_ids[:3]:
            loc = jelly_obj.functions[func_id]
            filepath = jelly_obj.files[loc.fileid]
            filename = Path(filepath).name
            print(f"FunctionID {func_id}:")
            print(f"  ファイル: {filename}")
            print(f"  行範囲: {loc.startrow}-{loc.endrow}")
            print(f"  位置: ({loc.startcolumn}, {loc.endcolumn})")


if __name__ == "__main__":
    main()
