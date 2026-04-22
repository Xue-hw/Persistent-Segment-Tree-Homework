import sys
import os
import webbrowser
import solution

def get_input_array():
    default_arr = [4, 1, 3, 2, 5, 2, -1, 3, 7, 4, 1]
    print("="*60)
    print("【可持久化线段树 (主席树) 交互测试系统】")
    print(f"默认测试数组: {default_arr}")
    print("="*60)
    
    print("请输入自定义数组 (用空格分隔数字)。")
    print("提示: 输入 'file:文件路径' 支持从本地文本文件读取数组内容 (如 file:data.txt)。")
    user_input = input("直接回车使用默认数组：\n> ").strip()
    if not user_input:
        print("-> 使用默认数组。")
        return default_arr
    
    if user_input.startswith("file:"):
        filepath = user_input[5:].strip()
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
                arr = [int(x) for x in content.split()]
                print(f"-> 成功从文件 {filepath} 读取到 {len(arr)} 个元素。")
                return arr
        except Exception as e:
            print(f"!! 读取文件失败 ({e})，将使用默认数组 !!")
            return default_arr

    try:
        arr = [int(x) for x in user_input.split()]
        print("-> 自定义数组解析成功。")
        return arr
    except ValueError:
        print("!! 输入格式错误，包含非数字字符，将使用默认数组 !!")
        return default_arr

def print_array_info(arr):
    print("\n--- 当前数组信息 ---")
    print(f"原始数组: {arr}")
    print(f"数组索引: {' '.join([f'[{i}]' for i in range(len(arr))])}")
    print(f"数组数值: {' '.join([f' {v} ' for v in arr])}")
    print("-" * 20)

def trace_operations(pst, arr):
    print("\n" + "*"*50)
    print("【详细操作跟踪输出】")
    print("1. 离散化处理结果:")
    print(f"   去重排序后的唯一值骨架: {pst.sorted_unique}")
    print(f"   原始数值到离散下标的映射: {pst.val_to_idx}")
    
    print("\n2. 权值线段树 (主席树) - 建树演进过程 (简化版树结构):")
    print("--- [操作 0] 初始状态 (空树) ---")
    pst.print_version_tree(0)
    
    for i, val in enumerate(arr, 1):
        print(f"\n--- [操作 {i}] 插入元素 {val} 后 (生成版本 {i}) ---")
        pst.print_version_tree(i)
    print("*"*50)

def rebuild_trees_if_needed(arr, pst, pst_dist, n):
    """
    增删改操作会改变原数组结构，静态主席树需要重新离散化和建树
    这个辅助函数用于在修改后快速重建数据结构
    """
    print("\n正在根据新数组重新构建可持久化树...")
    try:
        new_pst = solution.PersistentSegmentTree(arr)
        new_pst_dist = solution.PersistentTreeDistinct(arr)
        print("-> 重新构建完成！")
        return new_pst, new_pst_dist, len(arr)
    except Exception as e:
        print(f"-> 重新构建失败: {e}，回滚操作...")
        return pst, pst_dist, n

def main():
    arr = get_input_array()
    print_array_info(arr)
    
    verbose_mode = False
    
    print("\n正在构建可持久化树...")
    try:
        pst = solution.PersistentSegmentTree(arr)
        pst_dist = solution.PersistentTreeDistinct(arr)
        print("构建完成！")
    except Exception as e:
        print(f"构建失败: {e}")
        return

    n = len(arr)

    while True:
        print("\n" + "="*45)
        print("请选择要验证的功能：")
        print(" [核心查询功能]")
        print("  1. 查询区间 [L, R] 的第 K 小值")
        print("  2. 查询元素在区间 [L, R] 中的排名")
        print("  3. 查询区间 [L, R] 内不同元素的个数")
        print(" [原数组增删改功能 (将触发重构)]")
        print("  A. 在数组末尾追加元素 (Append)")
        print("  D. 删除数组指定位置的元素 (Delete)")
        print("  U. 修改数组指定位置的元素 (Update)")
        print(" [结构可视化与辅助]")
        print("  4. 生成并在浏览器打开 权值线段树 HTML 图表")
        print("  5. 生成并在浏览器打开 区间去重树 HTML 图表")
        print("  6. 彻底重新输入新数组")
        print(f"  7. 切换建树操作跟踪输出 (当前: {'[ON]' if verbose_mode else '[OFF]'})")
        print("  0. 退出系统")
        print("="*45)
        
        choice = input("请输入选项字母或序号: ").strip().upper()
        
        if choice == '0':
            print("感谢使用，再见！")
            break
            
        elif choice == '7':
            verbose_mode = not verbose_mode
            print(f"\n-> 操作跟踪展示已 {'开启' if verbose_mode else '关闭'}。")
            if verbose_mode:
                trace_operations(pst, arr)
            continue
            
        elif choice == '6':
            arr = get_input_array()
            print_array_info(arr)
            print("正在重新构建可持久化树...")
            pst = solution.PersistentSegmentTree(arr)
            pst_dist = solution.PersistentTreeDistinct(arr)
            n = len(arr)
            print("重新构建完成！")
            if verbose_mode:
                trace_operations(pst, arr)
            continue
            
        elif choice == 'A':
            val_str = input("请输入要追加的一个或多个数字 (空格分隔): ").strip()
            try:
                new_vals = [int(x) for x in val_str.split()]
                arr.extend(new_vals)
                print_array_info(arr)
                pst, pst_dist, n = rebuild_trees_if_needed(arr, pst, pst_dist, n)
                if verbose_mode: trace_operations(pst, arr)
            except ValueError:
                print("!! 输入包含非数字 !!")
            continue

        elif choice == 'D':
            if n == 0:
                print("!! 错误：数组已空 !!")
                continue
            idx_str = input(f"请输入要删除的索引位置 (0 到 {n-1}): ").strip()
            try:
                idx = int(idx_str)
                if 0 <= idx < n:
                    removed = arr.pop(idx)
                    print(f"-> 成功删除了位置 {idx} 上的元素 {removed}")
                    print_array_info(arr)
                    pst, pst_dist, n = rebuild_trees_if_needed(arr, pst, pst_dist, n)
                    if verbose_mode: trace_operations(pst, arr)
                else:
                    print("!! 索引越界 !!")
            except ValueError:
                print("!! 输入格式错误 !!")
            continue

        elif choice == 'U':
            if n == 0:
                print("!! 错误：数组已空 !!")
                continue
            params = input(f"请输入要修改的索引位置和新数值 (如 '2 99' 表示把位置2改为99，其中索引为 0 到 {n-1}): ").strip()
            try:
                parts = params.split()
                if len(parts) != 2:
                    print("!! 必须输入两个数字 !!")
                    continue
                idx, new_val = int(parts[0]), int(parts[1])
                if 0 <= idx < n:
                    old_val = arr[idx]
                    arr[idx] = new_val
                    print(f"-> 成功将位置 {idx} 上的元素从 {old_val} 修改为 {new_val}")
                    print_array_info(arr)
                    pst, pst_dist, n = rebuild_trees_if_needed(arr, pst, pst_dist, n)
                    if verbose_mode: trace_operations(pst, arr)
                else:
                    print("!! 索引越界 !!")
            except ValueError:
                print("!! 输入格式错误 !!")
            continue
            
        elif choice in ['1', '2', '3']:
            try:
                lr_str = input(f"请输入查询区间 L 和 R (0 <= L <= R <= {n-1})，用空格分隔: ").strip()
                L, R = map(int, lr_str.split())
                if not (0 <= L <= R < n):
                    print("!! 错误：区间越界 !!")
                    continue
                
                if choice == '1':
                    k_str = input(f"请输入 K (1 <= K <= {R-L+1}): ").strip()
                    K = int(k_str)
                    res = pst.query_kth(L, R + 1, K)
                    expected = sorted(arr[L:R+1])
                    print("\n--- 结果 ---")
                    print(f"子段真实排序: {expected}")
                    print(f"-> 您的查询结果: {res} (期待值: {expected[K-1] if 1 <= K <= len(expected) else 'K越界'})")
                    
                elif choice == '2':
                    val_str = input("请输入你想查询排名的具体数值: ").strip()
                    val = int(val_str)
                    res = pst.query_rank(L, R + 1, val)
                    expected = sorted(arr[L:R+1])
                    print("\n--- 结果 ---")
                    print(f"子段真实排序: {expected}")
                    print(f"-> 数值 {val} 在区间内的排名 (即比它小的个数 + 1) 是: {res}")
                    
                elif choice == '3':
                    res = pst_dist.query_distinct(L, R)
                    expected = set(arr[L:R+1])
                    print("\n--- 结果 ---")
                    print(f"子段内包含的不同元素: {expected}")
                    print(f"-> 查询得出不同元素的个数是: {res} (期待值: {len(expected)})")
            except ValueError:
                print("!! 输入格式有误，请输入数字 !!")
            except Exception as e:
                print(f"!! 执行时发生错误: {e}")
                
        elif choice in ['4', '5']:
            try:
                v_str = input(f"请输入要查看的树版本号 (0 <= 版本号 <= {n}): ").strip()
                v = int(v_str)
                if not (0 <= v <= n):
                    print("!! 错误：版本号不存在 !!")
                    continue
                if choice == '4':
                    print(f"\n--- 正在生成 版本 {v} 的权值线段树图表 ---")
                    filepath = "tree_viz_segment.html"
                    pst.export_html_tree(v, filepath)
                    abs_path = os.path.abspath(filepath)
                    webbrowser.open(f"file:///{abs_path.replace(chr(92), '/')}")
                    print(f"-> 成功！已自动在您的默认浏览器中打开图表：{abs_path}")
                elif choice == '5':
                    print(f"\n--- 正在生成 版本 {v} 的区间去重树图表 ---")
                    filepath = "tree_viz_distinct.html"
                    pst_dist.export_html_tree(v, filepath)
                    abs_path = os.path.abspath(filepath)
                    webbrowser.open(f"file:///{abs_path.replace(chr(92), '/')}")
                    print(f"-> 成功！已自动在您的默认浏览器中打开图表：{abs_path}")
            except ValueError:
                print("!! 输入格式有误，请输入整数版本号 !!")
        else:
            print("!! 无效选项，请重新输入 !!")

if __name__ == "__main__":
    main()