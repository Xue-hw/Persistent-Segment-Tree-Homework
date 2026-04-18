class SegmentTree:
    """
    通用型线段树实现 (基础+进阶版)
    支持功能：
    1. 区间构建 (O(N))
    2. 单点修改 (O(log N))
    3. 区间修改 (区间加值) - 借助 Lazy Tag 实现 (O(log N))
    4. 区间查询 (区间求和与区间最大值) (O(log N))
    """
    
    def __init__(self, data):
        self.n = len(data)
        self.data = data
        
        # 线段树数组，大小通常开到原数组大小的 4 倍
        self.tree_sum = [0] * (4 * self.n)
        self.tree_max = [0] * (4 * self.n)
        
        # 懒惰标记数组 (Lazy Tag)，用于区间修改时的延迟更新
        self.lazy = [0] * (4 * self.n)
        
        if self.n > 0:
            self._build(0, 0, self.n - 1)
            
    def _push_up(self, node):
        """
        向上更新：根据左右子节点的信息更新当前节点
        """
        left_child = 2 * node + 1
        right_child = 2 * node + 2
        self.tree_sum[node] = self.tree_sum[left_child] + self.tree_sum[right_child]
        self.tree_max[node] = max(self.tree_max[left_child], self.tree_max[right_child])
        
    def _push_down(self, node, start, end):
        """
        向下传递懒惰标记 (Lazy Tag)
        """
        if self.lazy[node] != 0:
            mid = (start + end) // 2
            left_child = 2 * node + 1
            right_child = 2 * node + 2
            val = self.lazy[node]
            
            # 更新左子节点
            self.lazy[left_child] += val
            self.tree_sum[left_child] += val * (mid - start + 1)
            self.tree_max[left_child] += val
            
            # 更新右子节点
            self.lazy[right_child] += val
            self.tree_sum[right_child] += val * (end - mid)
            self.tree_max[right_child] += val
            
            # 清空当前节点的标记
            self.lazy[node] = 0

    def _build(self, node, start, end):
        """
        递归构建线段树
        """
        if start == end:
            self.tree_sum[node] = self.data[start]
            self.tree_max[node] = self.data[start]
            return
            
        mid = (start + end) // 2
        left_child = 2 * node + 1
        right_child = 2 * node + 2
        
        self._build(left_child, start, mid)
        self._build(right_child, mid + 1, end)
        self._push_up(node)

    def update_point(self, index, val, node=0, start=0, end=None):
        """
        单点修改：将 index 位置的值更新为 val (覆盖)
        """
        if end is None:
            end = self.n - 1
            
        if start == end:
            self.tree_sum[node] = val
            self.tree_max[node] = val
            return
            
        mid = (start + end) // 2
        left_child = 2 * node + 1
        right_child = 2 * node + 2
        
        # 单点修改前也需要下放标记，避免覆盖被挂起的更新
        self._push_down(node, start, end)
        
        if index <= mid:
            self.update_point(index, val, left_child, start, mid)
        else:
            self.update_point(index, val, right_child, mid + 1, end)
            
        self._push_up(node)

    def update_range(self, L, R, val, node=0, start=0, end=None):
        """
        区间修改：将 [L, R] 范围内的所有元素增加 val
        """
        if end is None:
            end = self.n - 1
            
        # 若当前区间完全被包含在目标区间 [L, R] 内部，直接更新当前节点并打上 Lazy 标记
        if L <= start and end <= R:
            self.tree_sum[node] += val * (end - start + 1)
            self.tree_max[node] += val
            self.lazy[node] += val
            return

        # 下放之前的标记
        self._push_down(node, start, end)
        
        mid = (start + end) // 2
        left_child = 2 * node + 1
        right_child = 2 * node + 2
        
        # 递归更新左右子区间
        if L <= mid:
            self.update_range(L, R, val, left_child, start, mid)
        if R > mid:
            self.update_range(L, R, val, right_child, mid + 1, end)
            
        self._push_up(node)

    def query_sum(self, L, R, node=0, start=0, end=None):
        """
        区间求和查询
        """
        if end is None:
            end = self.n - 1
            
        if L <= start and end <= R:
            return self.tree_sum[node]
            
        self._push_down(node, start, end)
        
        mid = (start + end) // 2
        total = 0
        if L <= mid:
            total += self.query_sum(L, R, 2 * node + 1, start, mid)
        if R > mid:
            total += self.query_sum(L, R, 2 * node + 2, mid + 1, end)
            
        return total

    def query_max(self, L, R, node=0, start=0, end=None):
        """
        区间最大值查询
        """
        if end is None:
            end = self.n - 1
            
        if L <= start and end <= R:
            return self.tree_max[node]
            
        self._push_down(node, start, end)
        
        mid = (start + end) // 2
        max_val = float('-inf')
        if L <= mid:
            max_val = max(max_val, self.query_max(L, R, 2 * node + 1, start, mid))
        if R > mid:
            max_val = max(max_val, self.query_max(L, R, 2 * node + 2, mid + 1, end))
            
        return max_val

# ====== 测试与示例用法 ======
if __name__ == "__main__":
    arr = [1, 3, 5, 7, 9, 11]
    print(f"原始数组: {arr}")
    
    # 1. 构建线段树
    st = SegmentTree(arr)
    
    # 2. 区间查询 (求和 & 极值)
    print(f"区间 [1, 3] 的和 (3+5+7): {st.query_sum(1, 3)}")
    print(f"区间 [1, 3] 的最大值: {st.query_max(1, 3)}")
    
    # 3. 单点修改
    print("\n修改: 索引 2 的元素 5 修改为 6")
    st.update_point(2, 6)
    print(f"区间 [1, 3] 的和现在是: {st.query_sum(1, 3)}")
    
    # 4. 区间修改 (Lazy Propagation)
    print("\n区间修改: 区间 [2, 4] 上的所有元素增加 2")
    st.update_range(2, 4, 2)
    # 数组此时对应: [1, 3, 8(6+2), 9(7+2), 11(9+2), 11]
    print(f"区间 [1, 5] 的和现在是: {st.query_sum(1, 5)}")
    print(f"区间 [1, 5] 的最大值现在是: {st.query_max(1, 5)}")
