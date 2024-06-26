import heapq, csv
from collections import defaultdict
import hashtable

class LocationError(Exception):
    def __init__(self, message: str):
        self.message = message


def dataReader(type:int) -> list:
    """
    读取数据。0、1、2分别代表建筑、路口、路径。返回二维数组。
    """
    file = {0:"data/jianzhu.csv", 1:"data/cross.csv", 2:"data/path.csv"}
    with open(file[type], 'r', encoding="utf-8") as f:
        reader = csv.reader(f)
        data = []
        for row in reader:
            data.append(row)
        return data

class Node:
    def __init__(self, id: str, x: float, y: float, name: str, distance = float('inf')):
        self.id = id  # 节点ID
        self.name = name  # 节点名称
        self.type = 1 if id[0] == "b" else 0  # 节点类型：0-交叉口，1-建筑
        self.neighbours = {}  # (class)Node : distance
        self.x, self.y = float(x), float(y)
        self.distance = distance
    
    def addNeighbour(self, node: str, distance: float):
        """
        添加邻居节点及其距离到图中。
        此方法用于维护图中当前节点与另一个节点之间的距离信息。它将接收一个节点名称和一个距离值，
        并将该节点及其距离添加到当前节点的邻居列表中。
        """ 
        self.neighbours[node] = distance
    
    def __lt__(self, other):
        return self.distance < other.distance
    
    def __gt__(self, other):
        return self.distance > other.distance
    
class Path:
    def __init__(self, start: Node, end: Node, path: list, distance: float):
        self.start = start
        self.end = end
        self.path = path
        self.distance = distance

class Graph:
    def __init__(self):
        self.nodes = {}  # 根据Node id获取Node对象
        self.paths = {}
    def _addNode(self, id: str, x: float, y: float, name: str = None):
        """
        添加节点到图中。
        此方法用于添加一个新的节点到图中。它将接收节点的ID、X坐标、Y坐标和可选的名称，
        并将该节点添加到图中。
        """
        self.nodes[id] = Node(id, x, y, name)
    def _addEdge(self, id1: str, id2: str):
        """
        添加边到图中。
        此方法用于添加一条边到图中。它将接收两个节点的ID，并将它们之间的边添加到图中。
        """
        distance = self.calculateDistance(id1, id2)
        self.nodes[id1].addNeighbour(self.nodes[id2], distance)
        self.nodes[id2].addNeighbour(self.nodes[id1], distance)
    def calculateDistance(self, id1: str, id2: str):
        """
        计算两个节点之间的距离。
        此方法用于计算两个节点之间的距离。它将接收两个节点的ID，并返回它们之间的距离。
        """
        x1, y1 = self.nodes[id1].x, self.nodes[id1].y
        x2, y2 = self.nodes[id2].x, self.nodes[id2].y
        return round(((x1-x2)**2 + (y1-y2)**2)**0.5, 2)
    
    def dijkstra(self, start: str) -> tuple:
        """
        使用Dijkstra算法计算从起点到所有其他节点的最短路径。
        :return: 一个元组，包含距离字典和路径字典，分别表示从起点到每个节点的最短距离和最短路径。
        """
        start = self.nodes[start]  # 将起点转换为节点对象
        # 初始化所有节点的距离为无穷大，表示尚未探索
        distances = {node: float('inf') for node in self.nodes.values()}
        # 初始化所有节点的路径为一个空列表，表示尚未发现路径
        paths = defaultdict(list)
        distances[start] = 0  # 设置起点的距离为0
        paths[start] = [start]  # 设置起点的路径为起点本身
        unvisited = [(0, start)]  # 初始化未访问节点的队列，使用堆优先队列以便按距离排序

        while unvisited:
            # 从队列中弹出距离最小的节点
            current_distance, current_node = heapq.heappop(unvisited)

            # 如果当前节点的距离大于已知的最短距离，则忽略该节点
            if current_distance > distances[current_node]:
                continue

            # 遍历当前节点的所有邻居节点
            for neighbour, distance in current_node.neighbours.items():
                # 计算从起点经过当前节点到邻居节点的路径成本
                path_cost = distances[current_node] + distance
                # 如果新计算的路径成本小于已知的最短距离，则更新最短距离和路径
                if path_cost < distances[neighbour]:
                    distances[neighbour] = path_cost
                    # 更新邻居节点的路径为当前节点的路径加上邻居节点
                    paths[neighbour] = paths[current_node].copy() + [neighbour]
                    # 将邻居节点及其路径成本加入未访问节点的队列
                    heapq.heappush(unvisited, (path_cost, neighbour))
        # 返回所有节点的最短距离和最短路径
        return distances, paths
    
class Map(Graph):
    def __init__(self):
        super().__init__()
        self.path_hash = [None for node in self.nodes if node.type == 1]
        self.addNode()
        self.addEdge()
        self.hashtable = None
        self.name_to_id = {node.name: node.id for node in self.nodes.values() if node.type == 1}
        self.buildHash()
    
    def addNode(self):
        Buildings = dataReader(0)
        Crosses = dataReader(1)
        for row in Buildings:
            self._addNode(row[0], row[1], row[2], row[3])
        for row in Crosses:
            self._addNode(row[0], row[1], row[2])
    
    def addEdge(self):
        Paths = dataReader(2)
        for row in Paths:
            self._addEdge(row[0], row[1])

    def buildHash(self):
        self.hashtable = hashtable.HashTable()
        for i in range(102):
            lengths, paths = self.dijkstra(f"b{str(i)}")
            for to in lengths.keys():
                if to.type == 1:
                    self.hashtable.insert(i, Path(self.nodes[f"b{str(i)}"], to, paths[to], lengths[to]))
    
    def getPath(self, startname, endname) -> Path:
        try:
            start, end = self.name_to_id[startname], self.name_to_id[endname]
        except KeyError:
            raise LocationError("Invalid location")

        start = int(start[1:])
        end = int(end[1:])
        return self.hashtable.get(start, end)[0]
    
    def getVisitRoute(self, startname: str) -> Path:
        around_nodes = ['c16', 'c15', 'c14', 'c13', 'b32', 'c30', 'b56', 'c48', 'c49', 'b57', 'c50', 'c52', 'b71', 'c56', 'b69', 'b70', 'c57', 'c79', 'b82', 'c98', 'c80', 'c88', 'c94', 'b100', 'c89', 'c90', 'c91', 'c73', 'c74', 'c69', 'c68', 'c67', 'c66', 'b78', 'b75', 'b74', 'b73', 'c47', 'b55', 'c41', 'c95', 'b33', 'b52', 'c32', 'b40', 'b37', 'c10', 'b3', 'c9', 'b0', 'c8', 'b7', 'b6', 'c18', 'b20', 'c17']
        try:
            startid = self.name_to_id[startname]
        except KeyError:
            raise LocationError("Invalid location")
        if startid in around_nodes:
            pathnodeid = around_nodes[around_nodes.index(startid):] + around_nodes[:around_nodes.index(startid)+1 ]
            paths = [self.nodes[nodeid] for nodeid in pathnodeid]
            return Path(self.nodes[startid], self.nodes[startid], paths, 0)
        else:
            distances, paths = self.dijkstra(startid)
            nodes = [self.nodes[nodeid] for nodeid in around_nodes]
            li = []
            for to in distances.keys():
                if to in nodes:
                    li.append((to, paths[to], distances[to]))
            li.sort(key=lambda x: x[2])
            goid = li[0][0].id
            pathnodeid = around_nodes[around_nodes.index(goid) +1:] + around_nodes[:around_nodes.index(goid) ]
            paths = li[0][1] + [self.nodes[nodeid] for nodeid in pathnodeid] + list(reversed(li[0][1]))
            print(paths)
            return Path(self.nodes[startid], self.nodes[startid], paths, 0)





if __name__ == "__main__":
    map = Map()
    map.greedyPathFrom('文德楼')