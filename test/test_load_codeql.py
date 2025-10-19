"""
load_codeql_csv関数のテスト
"""

from jelly_graph.find.ql_function import load_codeql


def main():
    print("=== load_codeql_csv テスト ===\n")
    
    # CSVファイルの読み込み
    codeql_result = load_codeql("sample/ql_result.csv")
    
    print(f"読み込んだ関数の数: {len(codeql_result.function)}\n")
    
    # 最初の5件を表示
    print("--- 最初の5件 ---")
    for i, (filepath, (start_row, end_row)) in enumerate(codeql_result.function[:5], 1):
        print(f"{i}. ファイル: {filepath}")
        print(f"   行範囲: {start_row} - {end_row}\n")
    
    # ファイルごとにグループ化して件数を表示
    print("--- ファイルごとの検出数 ---")
    file_count: dict[str, int] = {}
    for filepath, _ in codeql_result.function:
        file_count[filepath] = file_count.get(filepath, 0) + 1
    
    # 上位5件を表示
    sorted_files = sorted(file_count.items(), key=lambda x: x[1], reverse=True)
    for filepath, count in sorted_files[:5]:
        # ファイル名のみ表示（パスが長いため）
        filename = filepath.split("/")[-1]
        print(f"  {filename}: {count}件")
    
    print(f"\n合計: {len(file_count)}ファイル, {len(codeql_result.function)}関数")
    
    # データ構造の確認
    print("\n--- データ構造の確認 ---")
    if codeql_result.function:
        first_item = codeql_result.function[0]
        print(f"型: {type(first_item)}")
        print(f"ファイルパス型: {type(first_item[0])}")
        print(f"行範囲型: {type(first_item[1])}")
        print(f"開始行型: {type(first_item[1][0])}")
        print(f"終了行型: {type(first_item[1][1])}")
        print("✅ 期待通りの型: tuple[str, tuple[int, int]]")


if __name__ == "__main__":
    main()
