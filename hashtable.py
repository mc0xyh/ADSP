class LinkedListNode:
    """链表节点"""
    def __init__(self, start, Path):
        self.key = start
        self.value = Path
        self.next = None

class HashTable:
    """基于链接法的哈希表实现
    key：起点"""
    def __init__(self, size=102):
        self.size = size
        self.table = [None] * size

    def insert(self, start: int, Path):
        """插入操作，处理冲突时使用链表"""
        index = start
        if not self.table[index]:
            self.table[index] = LinkedListNode(start, Path)
        else:
            current = self.table[index]  # 初始化节点
            while (current.next is not None
                   and 
                   (int(current.next.value.end.id[1:]) < int(Path.end.id[1:])
                   or 
                   (int(current.next.value.end.id[1:]) == int(Path.end.id[1:])
                   and current.next.value.distance <= Path.distance))):
                current = current.next
            current.next = LinkedListNode(start, Path)
    def get(self, start, end):
        """获取操作，根据key查找值"""
        results = []
        index = start
        current = self.table[index]
        while current.next != None and int(current.next.value.end.id[1:]) <= end:
            current = current.next
            if int(current.value.end.id[1:]) == end:
                results.append(current.value)
        return results
    
    def print_all(self, start):
        index = start
        current = self.table[index]
        while current.next != None:
            print(current.value.end.id)
            current = current.next
        return current.value