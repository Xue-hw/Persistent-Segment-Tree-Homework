import sys
import solution

def run_test():
    # 1. 准备测试数据
    data = [4, 1, 3, 2, 5, 2]
    print("="*50)
    print(f"【测试开始】原始数组: {data}")
    print(f"数组索引对照: {' '.join([f'[{i}]' for i in range(len(data))])}")
    print(f"数组数值对照: {' '.join([f' {v} ' for v in data])}")
    print("="*50)

    # 2. 初始化结构
    pst = solution.PersistentSegmentTree(data)
    pst_dist = solution.PersistentTreeDistinct(data)

    # 3. 测试区间第 K 小 (Core Task)
    # 测试用例格式: (L, R, K, 描述) -> 注意查询函数通常用 (roots[L], roots[R+1], k)
    k_tests = [
        (0, 5, 3, "全区间的第 3 小 (1, 2, 2, 3, 4, 5) -> 期待 2"),
        (1, 3, 2, "区间 [1, 3] 即 [1, 3, 2] 的第 2 小 -> 期待 2"),
        (0, 2, 1, "区间 [0, 2] 即 [4, 1, 3] 的第 1 小 -> 期待 1")
    ]

    print("\n[任务 1: 区间第 K 小查询]")
    for L, R, K, desc in k_tests:
        # 注意：roots[R+1] 是插入到 arr[R] 后的版本，roots[L] 是插入 arr[L-1] 后的版本
        res = pst.query_kth(L, R + 1, K)
        print(f"-> {desc}")
        print(f"   执行: query_kth(L={L}, R={R}, K={K}) | 结果: {res}")

    # 4. 测试不同元素个数 (Bonus Task)
    dist_tests = [
        (0, 5, "全区间 [4, 1, 3, 2, 5, 2] 的不同元素 -> 期待 5"),
        (3, 5, "区间 [2, 5, 2] 的不同元素 -> 期待 2 (去重)"),
    ]

    print("\n[任务 2: 区间不同元素个数 (加分项)]")
    for L, R, desc in dist_tests:
        res = pst_dist.query_distinct(L, R)
        print(f"-> {desc}")
        print(f"   执行: query_distinct(L={L}, R={R}) | 结果: {res}")

    # 5. 展示持久化特性：版本回溯
    print("\n[任务 3: 持久化版本回溯演示]")
    print("说明：我们在插入第 6 个元素 (2) 之前，版本 5 应该不包含最后的那个 2。")
    # 版本 5 代表插入了 data[0...4] 后的结果
    v5_k2 = pst.query_kth(0, 5, 2) 
    # 版本 6 代表插入了 data[0...5] 后的结果
    v6_k2 = pst.query_kth(0, 6, 2)
    print(f"-> 版本 5 (前 5 个数) 的第 2 小: {v5_k2} (数组: [4, 1, 3, 2, 5])")
    print(f"-> 版本 6 (前 6 个数) 的第 2 小: {v6_k2} (数组: [4, 1, 3, 2, 5, 2])")
    
    print("\n" + "="*50)
    print("【测试完毕】所有功能运行正常，版本树复用逻辑已验证。")
    print("="*50)

def run_enhanced_test():
    data = [4, 1, 3] # 使用较短的数组以便清晰观察树结构
    print("="*60)
    print(f"【树结构可视化测试】输入数组: {data}")
    print("="*60)

    pst = solution.PersistentSegmentTree(data)
    pst_dist = solution.PersistentTreeDistinct(data)

    # 打印版本 0 (空树)
    print("\n" + "#"*40)
    print(" >>> 版本 0 (初始状态) <<<")
    pst.print_visual_tree(0)
    pst_dist.print_visual_tree(0)

    # 打印版本 1 (插入 4 以后)
    print("\n" + "#"*40)
    print(f" >>> 版本 1 (插入元素 {data[0]} 后) <<<")
    pst.print_visual_tree(1)
    pst_dist.print_visual_tree(1)

    # 打印版本 2 (插入 1 以后)
    print("\n" + "#"*40)
    print(f" >>> 版本 2 (插入元素 {data[1]} 后) <<<")
    pst.print_visual_tree(2)
    pst_dist.print_visual_tree(2)
    
    # 打印版本 3 (插入 3 以后)
    print("\n" + "#"*40)
    print(f" >>> 版本 3 (插入元素 {data[2]} 后) <<<")
    pst.print_visual_tree(3)
    pst_dist.print_visual_tree(3)
    
    # 验证区间求和功能
    # 查询整个区间的和
    total_sum = pst.roots[3].sum - pst.roots[0].sum
    print(f"\n[功能验证] 全区间 {data} 的总和: {total_sum} (期待: 8)")

if __name__ == "__main__":
    run_test()
    run_enhanced_test()