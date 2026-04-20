import sys
sys.setrecursionlimit(200000)#增加递归深度限制，防止在构建或查询深度较大的线段树时出现 RecursionError

class Node:
    """
    线段树节点类
    """
    __slots__ = ['count', 'sum', 'left', 'right']  # 限制属性，优化内存
    def __init__(self, count=0, sum_val=0, left=None, right=None):
        self.count = count
        self.sum = sum_val
        self.left = left
        self.right = right

class PersistentSegmentTree:
    """
    可持久化权值线段树 (主席树)
    用于解决静态区间第 k 小问题、区间排名问题等
    """
    def __init__(self, arr):
        self.arr = arr
        # 1. 离散化：去重并排序，建立原始值与离散化下标的映射
        #Q：why离散化
        #A：离散化可以将原始数据映射到一个较小的范围内，减少线段树的高度，提高查询效率
        #实践中：只要查询涉及值的排序或统计（第 k 小、排名、值域计数、不同元素计数等），就应先做离散化；若只按位置更新/查询（区间和、点改等），則直接按下标建树即可
        self.sorted_unique = sorted(list(set(arr)))
        self.val_to_idx = {val: idx for idx, val in enumerate(self.sorted_unique)}# 离散化映射
        self.max_idx = len(self.sorted_unique) - 1#索引，要用个数减一

        # 记录每个历史版本的根节点，roots[i] 表示插入原数组前 i 个元素后的线段树根节点
        self.roots = [self._build(0, self.max_idx)]
        
        # 逐个插入数组元素，生成新的版本
        for val in arr:
            idx = self.val_to_idx[val]
            # 基于上一个版本的根节点，插入新元素
            new_root = self._insert(self.roots[-1], 0, self.max_idx, idx)
            self.roots.append(new_root)

    def query_rank(self, left_root_idx, right_root_idx, val):
        """
        查询元素 val 在区间 [left_root_idx+1, right_root_idx] 中的排名 (比它小的元素个数 + 1)
        """
        if val not in self.val_to_idx:
            # 如果 val 不在数组里，可以找到第一个大于它的元素的下标（这里做简化，假设查询合法存在的值）
            import bisect
            idx = bisect.bisect_left(self.sorted_unique, val) - 1
        else:
            idx = self.val_to_idx[val] - 1
            
        if idx < 0:
            print("输入值小于最小值")
            return 1
            
        smaller_count = self._query_count(self.roots[left_root_idx], self.roots[right_root_idx], 0, self.max_idx, 0, idx)
        return smaller_count + 1

    def _query_count(self, left_node, right_node, tree_l, tree_r, q_l, q_r):
        """
        查询离散化下标在 [q_l, q_r] 范围内的元素出现次数
        """
        if q_l <= tree_l and tree_r <= q_r:
            return right_node.count - left_node.count
            
        mid = (tree_l + tree_r) // 2
        res = 0
        if q_l <= mid:
            res += self._query_count(left_node.left, right_node.left, tree_l, mid, q_l, q_r)
        if q_r > mid:
            res += self._query_count(left_node.right, right_node.right, mid + 1, tree_r, q_l, q_r)
        return res

    def _build(self, l, r):
        """
        初始化空树（第0个版本）
        :param l: 离散化区间左端点
        :param r: 离散化区间右端点
        :return: 当前节点
        """
        node = Node()
        if l == r:
            return node
        mid = (l + r) // 2
        node.left = self._build(l, mid)
        node.right = self._build(mid + 1, r)
        return node

    def _insert(self, prev_node, l, r, val_idx):
        """
        插入新节点，返回新版本的节点
        """
        inserted_val = self.sorted_unique[val_idx]
        new_node = Node(prev_node.count + 1, prev_node.sum + inserted_val, prev_node.left, prev_node.right)
        
        if l == r:
            # 抵达叶子节点，完成插入
            return new_node
            
        mid = (l + r) // 2
        # 判断插入位置在左子树还是右子树
        if val_idx <= mid:
            # 只需更新左子树，右子树继续共享原版本
            new_node.left = self._insert(prev_node.left, l, mid, val_idx)
        else:
            # 只需更新右子树，左子树继续共享原版本
            new_node.right = self._insert(prev_node.right, mid + 1, r, val_idx)
            
        return new_node

    def query_kth(self, left_root_idx, right_root_idx, k):
        """
        查询区间 [left_root_idx+1, right_root_idx] 的第 k 小值
        :param left_root_idx: 区间左端点的前一个位置 (l-1)
        :param right_root_idx: 区间右端点 (r)
        :param k: 第 k 小
        :return: 对应的原数组值
        """
        # 检查区间总数
        total_count = self.roots[right_root_idx].count - self.roots[left_root_idx].count
        if k <= 0 or k > total_count:
            print(f"查询失败：k={k} 超出区间元素总数 {total_count}")
            return None
        return self._query_kth(self.roots[left_root_idx], self.roots[right_root_idx], 0, self.max_idx, k)

    def _query_kth(self, left_node, right_node, l, r, k):
        """
        递归查询第 k 小
        利用前缀和思想：right_node 包含前 r 个元素的信息，left_node 包含前 l-1 个元素的信息。
        相减即可得到区间 [l, r] 内的元素分布。
        """
        if l == r:
            # 找到目标叶子节点，返回其对应的真实值
            return self.sorted_unique[l]
            
        mid = (l + r) // 2
        # 计算当前区间内，落在左子树的元素个数（前缀和思想）
        left_count = right_node.left.count - left_node.left.count
        
        if k <= left_count:
            # 第 k 小在左子树
            return self._query_kth(left_node.left, right_node.left, l, mid, k)
        else:
            # 第 k 小在右子树，需要在右子树中找第 (k - left_count) 小
            return self._query_kth(left_node.right, right_node.right, mid + 1, r, k - left_count)

    def print_version_tree(self, version):
        """
        打印某个版本的简化树结构
        """
        print(f"=== 版本 {version} 树结构 ===")
        self._print_tree(self.roots[version], 0, self.max_idx, 0)

    def _print_tree(self, node, l, r, depth):
        if not node:
            return
        indent = "  " * depth
        if l == r:
            print(f"{indent}Leaf [{l},{r}] (值 {self.sorted_unique[l]}): count={node.count}")
        else:
            print(f"{indent}Node [{l},{r}]: count={node.count}")
            mid = (l + r) // 2
            self._print_tree(node.left, l, mid, depth + 1)
            self._print_tree(node.right, mid + 1, r, depth + 1)

    def print_visual_tree(self, version_idx):
        """
        可视化打印指定版本的树结构
        """
        root = self.roots[version_idx]
        print(f"\n[可视化树结构 - 版本 {version_idx}]")
        print("格式: [值域区间] (计数, 累加和)")
        self._recursive_print(root, 0, self.max_idx, "", True)

    def _recursive_print(self, node, l, r, indent, is_left):
        if not node or (node.count == 0 and node.sum == 0):
            return
        
        mid = (l + r) // 2
        if l != r:
            self._recursive_print(node.right, mid + 1, r, indent + ("    " if is_left else " |  "), False)
        
        prefix = indent + (" └── " if is_left else " ┌── ")
        if l == r:
            print(f"{prefix}Leaf [{self.sorted_unique[l]}] (c:{node.count}, s:{node.sum})")
        else:
            print(f"{prefix}Node [{self.sorted_unique[l]}~{self.sorted_unique[r]}] (c:{node.count}, s:{node.sum})")
        
        if l != r:
            self._recursive_print(node.left, l, mid, indent + (" |  " if is_left else "    "), True)

# 由于‘不同元素查询’需要基于下标维度并进行动态位置抹除，与基于值域维度的权值线段树存在维度冲突，因此我保留了两个类
class PersistentTreeDistinct:
    """
    可持久化线段树 - (根据数组下标建树)
    用于【可选加分项】：查询静态区间 [L, R] 中不同元素的个数
    原理：从左到右维护每一个元素的最新出现位置。对于版本 R，里面记录了每个元素在前 R 个数中最后一次出现的下标。
    查询 [L, R] 时，只需在版本 R 的线段树中，查询大于等于 L 的位置上有多少个有效记录。
    """
    def __init__(self, arr):
        self.n = len(arr)
        if self.n == 0:
            return
            
        # roots[i] 对应插入前 i 个元素后的线段树根节点
        self.roots = [self._build(0, self.n - 1)]
        self.last_pos = {}

        for i, val in enumerate(arr):
            prev_root = self.roots[-1]
            
            # 如果该元素之前出现过，需要在这个历史版本的基础上，把上一位置的计数减去 (-1)
            if val in self.last_pos:
                prev_pos = self.last_pos[val]
                curr_root = self._update(prev_root, 0, self.n - 1, prev_pos, -1)
            else:
                curr_root = prev_root
                
            # 在当前位置标记为出现 (+1)
            new_root = self._update(curr_root, 0, self.n - 1, i, 1)
            self.roots.append(new_root)
            # 更新最后出现位置
            self.last_pos[val] = i

    def _build(self, l, r):
        node = Node()
        if l == r:
            return node
        mid = (l + r) // 2
        node.left = self._build(l, mid)
        node.right = self._build(mid + 1, r)
        return node

    def _update(self, prev_node, l, r, idx, val):
        if prev_node is None:
            prev_node = Node(0, 0, None, None)
            
        new_node = Node(prev_node.count + val, 0, prev_node.left, prev_node.right)
        if l == r:
            return new_node
        mid = (l + r) // 2
        if idx <= mid:
            new_node.left = self._update(prev_node.left, l, mid, idx, val)
        else:
            new_node.right = self._update(prev_node.right, mid + 1, r, idx, val)
        return new_node

    def query_distinct(self, L, R):
        """
        查询原数组范围 [L, R] 内部有多少个不同的元素 (L, R 为原数组 0-based 索引)
        """
        if L > R or L < 0 or R >= self.n:
            return 0
        # 查询版本 R+1（即插入了元素 R 之后的版本）中，区间 [L, n-1] 也就是 [L, R] 的权值和
        return self._query(self.roots[R + 1], 0, self.n - 1, L, self.n - 1)

    def _query(self, node, tree_l, tree_r, q_l, q_r):
        if not node:
            return 0
        if q_l <= tree_l and tree_r <= q_r:
            return node.count
            
        mid = (tree_l + tree_r) // 2
        res = 0
        if q_l <= mid:
            res += self._query(node.left, tree_l, mid, q_l, q_r)
        if q_r > mid:
            res += self._query(node.right, mid + 1, tree_r, q_l, q_r)
        return res

    def print_visual_tree(self, version_idx):
        """
        可视化打印指定版本的树结构
        """
        root = self.roots[version_idx]
        print(f"\n[基于位置区间的线段树 - 版本 {version_idx}]")
        print("格式: [位置区间] (有效不同元素计数)")
        self._recursive_print(root, 0, self.n - 1, "", True)

    def _recursive_print(self, node, l, r, indent, is_left):
        if not node or node.count == 0:
            return
        
        mid = (l + r) // 2
        if l != r:
            self._recursive_print(node.right, mid + 1, r, indent + ("    " if is_left else " |  "), False)
        
        prefix = indent + (" └── " if is_left else " ┌── ")
        if l == r:
            print(f"{prefix}Leaf pos[{l}] (c:{node.count})")
        else:
            print(f"{prefix}Node pos[{l}~{r}] (c:{node.count})")
        
        if l != r:
            self._recursive_print(node.left, l, mid, indent + (" |  " if is_left else "    "), True)


# ====== 测试与输出 ======
if __name__ == "__main__":
    # 示例数组
    arr = [4, 1, 3, 2, 5, 2]
    print(f"=====================================")
    print(f"原始数组: {arr}")
    
    # 【功能1 & 2】离散化与初始化可持久化线段树
    pst = PersistentSegmentTree(arr)
    print(f"离散化结果: {pst.sorted_unique}")
    
    # 【功能3-1】区间第k小查询
    l, r, k = 1, 4, 2  # 下标1到4(包含4)，即数组元素 arr[1:5]
    res = pst.query_kth(l, r+1, k)
    expected_arr = sorted(arr[l:r+1])
    print(f"\n---> [功能演示] 区间第 K 小:")
    print(f"查询原数组区间 [{l}, {r}]（即 {arr[l:r+1]}）的第 {k} 小值")
    print(f"期望按升序排列为: {expected_arr} -> 答案应该是 {expected_arr[k-1]}")
    print(f"主席树查询结果: {res}")
    
    # 【扩展功能】查询区间内某元素的排名
    val_to_rank = 3
    rank = pst.query_rank(l, r+1, val_to_rank)
    print(f"\n---> [功能演示] 区间内元素排名:")
    print(f"元素 {val_to_rank} 在区间 [{l}, {r}] 中的排名是: {rank}")
    
    # 【加分项：功能3-2】区间不同元素个数查询
    pst_distinct = PersistentTreeDistinct(arr)
    dl, dr = 1, 5  # 查询区间 arr[1:6] => [1, 3, 2, 5, 2]
    distinct_count = pst_distinct.query_distinct(dl, dr)
    print(f"\n---> [功能演示] 区间不同元素个数查询 (加分项):")
    print(f"数组切片 arr[{dl}:{dr}] 的真实值为: {arr[dl:dr+1]}")
    print(f"该区间内不同的元素集合为: {set(arr[dl:dr+1])} (期待个数: {len(set(arr[dl:dr+1]))})")
    print(f"加分主席树计算的不同元素个数为: {distinct_count}")

    # 【功能4】打印版本树结构展示持久化机制
    print(f"\n---> [功能演示] 观察持久化的版本复用:")
    pst.print_version_tree(0)  # 空树
    pst.print_version_tree(1)  # 插入第一个元素 4 后的树

    # 可视化树结构演示
    print(f"\n---> [功能演示] 可视化树结构:")
    pst.print_visual_tree(1)  # 插入第一个元素 4 后的树
    pst.print_visual_tree(2)  # 插入前两个元素 4, 1 后的树
    pst.print_visual_tree(3)  # 插入前三个元素 4, 1, 3 后的树
    pst.print_visual_tree(4)  # 插入前四个元素 4, 1, 3, 2 后的树

    # 加分项：可视化打印不同元素的线段树版本
    print(f"\n---> [功能演示] 可视化不同元素线段树版本:")
    pst_distinct.print_visual_tree(0)  # 空树
    pst_distinct.print_visual_tree(1)  # 插入第一个元素 4 后的树
    pst_distinct.print_visual_tree(2)  # 插入前两个元素 4, 1 后的树
    pst_distinct.print_visual_tree(3)  # 插入前三个元素 4, 1, 3 后的树
    pst_distinct.print_visual_tree(4)  # 插入前四个元素 4, 1, 3, 2 后的树


# 实际上，离散化后的权值线段树通常不需要初始的 $4n$ 建树（除非有初始权值）。每次插入产生 $\lceil \log_2 N \rceil$ 个新节点。经验值通常开启 32倍或40倍 的 $N$