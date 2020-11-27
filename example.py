from collections import defaultdict 
  
class Graph(): 
    def __init__(self,vertices): 
        self.graph = defaultdict(list) 
        self.V = vertices 
        self.cycles = [[]]
  
    def addEdge(self,u,v): 
        self.graph[u].append(v)

    def getCycles(self):
        return self.cycles
  
    def dfs(self, v, visited, start, stack): 
  
        # Mark current node as visited and  
        # adds to recursion stack 
        stack.append(v)

        self.cycles[-1].append(v)
        # Recur for all neighbours 
        # if any neighbour is visited and in  
        # recStack then graph is cyclic 
        for neighbour in self.graph[v]: 
            if visited[neighbour] == False: 
                visited[neighbour] = True
                self.dfs(neighbour, visited, start, stack)
            if len(self.graph[v]) > 1:
                new_arr = stack.copy()
                self.cycles.append(new_arr)
            
        visited[v] = False
        stack.pop()

  
    # Returns true if graph is cyclic else false 
    def isCyclic(self): 
        visited = {72:False,8:False,9:False,13:False,6:False,4:False,26:False}
        stack = []
        visited[72] = True
        self.dfs(72,visited,72,stack) 
  
g = Graph(7) 
g.addEdge(72, 8) 
g.addEdge(8, 9) 
g.addEdge(9, 4) 
g.addEdge(9, 13) 
g.addEdge(9, 26) 
g.addEdge(13, 6) 
g.addEdge(6, 4) 
g.addEdge(4, 26) 
g.addEdge(26,72) 
g.isCyclic()

c = g.getCycles()
c.pop()
print(c)
  
# Thanks to Divyanshu Mehta for contributing this code 