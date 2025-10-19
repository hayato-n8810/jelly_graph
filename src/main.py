import jelly_graph
from pathlib import Path

input_file = "/Users/hayato-n/projects/jelly_graph/sample/jelly_result_single.json"
jelly_obj = jelly_graph.load_jelly(input_file)
# 依存関係の重みを計算  
depend_map = jelly_graph.dependency_weights(jelly_obj)
# コールグラフを構築
callgraph = jelly_graph.build_callgraph(depend_map)
# 特定の関数を検索
target_func = jelly_graph.match_function(jelly_obj, "filepath", 1, 10)

# 呼び出し元・呼び出し先の経路を検索
# パスの中に自分も入ることに注意\
# 呼び出し元
src_paths = jelly_graph.search_src(callgraph, jelly_obj, target_func=target_func)
jelly_graph.print_src_trace_results(callgraph, jelly_obj, target_func, show_all_paths=True)
# 呼び出し先
dst_paths = jelly_graph.search_dst(callgraph, jelly_obj, target_func=target_func)
jelly_graph.print_dst_trace_results(callgraph, jelly_obj, target_func, show_all_paths=True)

# 特定の関数の依存関係を調査
if target_func in jelly_obj.functions:
    print(f"\n=== 関数 {target_func} の依存関係 ===")
    
    # この関数が呼び出す関数
    caller_deps = jelly_graph.get_caller_dependencies(depend_map, target_func)
    if caller_deps:
        print(f"関数 {target_func} が呼び出す関数:")
        for callee, count in sorted(caller_deps.items(), key=lambda x: x[1], reverse=True):
            print(f"  -> 関数 {callee}: {count}回")
    else:
        print(f"関数 {target_func} は他の関数を呼び出していません")
    
    # この関数を呼び出す関数
    callee_deps = jelly_graph.get_callee_dependencies(depend_map, target_func)
    if callee_deps:
        print(f"\n関数 {target_func} を呼び出す関数:")
        for caller, count in sorted(callee_deps.items(), key=lambda x: x[1], reverse=True):
            print(f"  関数 {caller} -> : {count}回")
    else:
        print(f"\n関数 {target_func} を呼び出す関数はありません")