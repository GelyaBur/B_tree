from struct import pack, unpack, calcsize
import timeit

class Node:
    def __init__(self, t, index, n = 0,  keys = None, leaf = 1, child = None):
        self.t = t
        self.index= index
        self.leaf = leaf
        self.n = n
        if keys != None:
            self.keys = keys
        else:    
            self.keys = [0] * (2 * self.t - 1)
            
        #self.n = len(self.keys)   
        #if keys != None:         
        self.values = [10*self.keys[i] for i in range(len(self.keys))]
        #else:    
         #   self.values = [0] * (2 * self.t - 1)    
        if child != None:
            self.child = child
        else:    
            self.child = [0] * (2 * self.t)
        
        
    def __str__(self):
        return str([(self.keys[i],self.values[j]) for i in range(len(self.keys)) for j in range(len(self.values)) if i == j]) + str([self.child[i] for i in range(len(self.child)) ]) + str(self.leaf) + str(self.n)
        
                   
        

                                          
            
class Btree:
     

    def __init__(self,t,filename):
        self.file = filename
        self.t = t
        self.root = None
        self.size = 0
        self.count = 0
        
    # Write and read data from disk    
        
    def write_node(self,node):
        self.count += 1   
        f = open(self.file, 'r+b')
        f.seek(1 + node.index*(4*(4*self.t+1)))
        f.write(pack('i',node.n)) 
        for x in node.keys:
            f.write(pack('i',x))
        f.seek(1 + node.index*(4*(4*self.t+1)) + 4*(2*self.t ))
        f.write(pack('i',node.leaf))    
        for x in node.child: 
                 
            f.write(pack('i',x))
        f.close()   
        
    def read_node(self,index,node):
        self.count += 1
        f = open(self.file, 'rb')        
        f.seek(1 + index*(4*(4*self.t+1)))
        node.n = (unpack('i',(f.read(4))))[0]        
        for i in range(2*self.t-1):
            node.keys[i] = (unpack('i',(f.read(4))))[0]            
        f.seek(1 + index*(4*(4*self.t+1)) + 4*(2*self.t))
        node.leaf = (unpack('i',(f.read(4))))[0]
        for i in range(2*self.t):
            node.child[i] = (unpack('i',(f.read(4))))[0]
        f.close() 
        #node.values = [10*node.keys[i] for i in range(len(node.keys))]      
        
    #Tree traversal and search of the key       
        
    def traverse_help(self,node,ind):
        
        for i in range(node.n):
            if node.leaf == 0:
                child = Node(self.t,node.child[i])
                self.read_node(child.index,child)
                self.traverse_help(child,ind + 1)
            #if node.keys[i] != 0:    
            print (2*ind*' ' + str(node.keys[i]))
        if node.leaf == 0:
            child = Node(node.t,node.child[i+1])
            self.read_node(child.index,child)
            self.traverse_help(child,ind + 1)
            
    def search_help(self,node, k):
        i = 0
        while i < node.n and k > node.keys[i]:
            i += 1
        if i < node.n and k == node.keys[i]:
            return node
        elif node.leaf == 1:
            return None
        else:
            child = Node(node.t,node.child[i])
            self.read_node(child.index,child)
            return self.search_help(child,k)         
            
    def traverse(self):
        if self.root:            
            return self.traverse_help(self.root,0)                       
        
    def __len__(self):
        return self.size        
           
    def search(self, k):
        if self.root:
            return self.search_help(self.root,k) 
            
            
    # Insertion of the key        
    
    def split(self,x,i):
        self.size += 1
        z = Node(self.t,self.size)        
        y = Node(self.t,x.child[i])        
        self.read_node(y.index,y)
        z.n = self.t - 1
        z.leaf = y.leaf
        for j in range(self.t-1):
            z.keys[j] = y.keys[j+self.t]
            y.keys[j+self.t] = 0
        if y.leaf == 0:
            for j in range(self.t):
                z.child[j] = y.child[j+self.t]
                y.child[j+self.t] = 0
        y.n = self.t - 1        
        for j in range(x.n,i,-1):
            x.child[j+1] = x.child[j]
            
        x.child[i+1] = z.index
        for j in range(x.n-1,i-1,-1):
            x.keys[j+1] = x.keys[j]            
        x.keys[i] = y.keys[self.t-1]
        y.keys[self.t-1] =0
        x.n = x.n + 1        
        self.write_node(x)
        self.write_node(y)
        self.write_node(z)   
    
    def insert(self,k):
        if self.root == None:
            x = Node(self.t,1)
            self.size = 1
            x.keys[0] = k
            x.n = 1
            self.root = x
            self.write_node(x)
        else:
            x = Node(self.t,self.root.index)
            self.read_node(self.root.index,x)            
            if x.n == 2*self.t - 1:
                self.size += 1
                s = Node(self.t,self.size) 
                self.root = s
                s.leaf = 0
                s.n = 0
                s.child[0] = x.index
                self.split(s,0)
                self.insert_nonfull(s,k) 
            else:       
                self.insert_nonfull(x,k) 
    
    def insert_nonfull(self,x,k):
        i = x.n - 1               
        if x.leaf == 1:            
            while i >= 0 and x.keys[i] > k:
                x.keys[i+1] = x.keys[i]
                i -= 1
            x.keys[i+1] = k
            x.n += 1
            if self.size == 1:
                self.root = x          
               
            self.write_node(x)
        else:
            while i >= 0 and x.keys[i] > k:
                i -= 1   
            i = i + 1
            child = Node(self.t, x.child[i])
            self.read_node(x.child[i],child)                         
            if child.n == 2*self.t - 1:
                if x.index == self.root.index:                    
                    temp = self.root
                else:    
                    temp = x
                self.split(temp,i)    
                if k > temp.keys[i]:
                    i += 1
                x = temp 
                child = Node(self.t,x.child[i])
                self.read_node(child.index,child)   
            #ch = Node(self.t,x.child[i])
            #self.read_node(ch.index,ch)        
            self.insert_nonfull(child,k) 
            
    # Delete the key               
            
    def getPr(self,node,i):
        cur = Node(self.t,node.child[i])
        self.read_node(node.child[i],cur)
        while cur.leaf == 0:            
            x = Node(self.t,cur.child[cur.n])
            self.read_node(cur.child[cur.n],x)
            cur = x
        return cur.keys[cur.n-1]   
    
    def getSuc(self,node,i):
        cur = Node(self.t,node.child[i+1])
        self.read_node(node.child[i+1],cur)
        while cur.leaf == 0:
            x = Node(self.t,cur.child[0])
            self.read_node(cur.child[0],x)
            cur = x
        return cur.keys[0]  
        
    def remove(self,index,k):
        cur = Node(self.t,index)
        self.read_node(index,cur)
        i = 0
        while i < cur.n and cur.keys[i] < k:
            i += 1            
        if i < cur.n and cur.keys[i] == k:            
            if cur.leaf == 1:
                self.remove_from_leaf(cur,i)
            else:
                self.remove_from_non_leaf(cur,i)
        else:            
            child_i = Node(self.t,cur.child[i])
            self.read_node(cur.child[i],child_i)
            if child_i.n < self.t:
                child_im1 = Node(self.t,cur.child[i-1])
                self.read_node(cur.child[i-1],child_im1)
                
                if i != 0 and child_im1.n >= self.t:
                    self.borrow_Pr(cur,child_i,child_im1,i)
                    self.remove(child_i.index,k)
                    
                else:
                    
                    child_ip1 = Node(self.t,cur.child[i+1])
                    self.read_node(cur.child[i+1],child_ip1)                                           
                    if i != cur.n and child_ip1.n >= self.t:
                        self.borrow_Suc(cur,child_i,child_ip1,i)
                        self.remove(child_i.index,k)                       
                        
                    else:
                        
                        if i != cur.n:                            
                            self.merge(cur,child_i,child_ip1,i)                    
                        else:
                            print i
                            print child_i
                            print child_im1
                            self.merge(cur,child_im1,child_i,i-1)   
                            print child_i
                            print child_im1     
                            #self.remove(child_im1.index,k) 
                            child_i =child_im1
                        for j in range(i+1,cur.n,1): 
                            cur.keys[j-1] = cur.keys[j]
                        cur.keys[cur.n-1] = 0
            
                        for j in range(i+2,cur.n+1,1): 
                            cur.child[j-1] = cur.child[j]
                        cur.child[cur.n] = 0
                        cur.n -= 1        
                        if cur.index == self.root.index:
                            self.root = cur
                        if cur.n == 0:
                            self.root = child_i
                        self.remove(child_i.index,k)
                        self.write_node(cur)    
            else:
                self.remove(child_i.index,k)                               
    
    
    def borrow_Suc(self,cur,child1,child2,i):
        child1.keys[child1.n] = cur.keys[i]    
        if child1.leaf == 0:
            child1.child[child1.n + 1] = child2.child[0]
        cur.keys[i] = child2.keys[0]

        child1.n += 1
        for j in range(1,child2.n,1):
            child2.keys[j-1] = child2.keys[j]            
        child2.keys[child2.n-1] = 0
        if child2.leaf == 0:
            for j in range(1,child2.n+1,1):
                child2.child[j-1] = child2.child[j]
        child2.child[child2.n] = 0
        child2.n -= 1 
        if cur.index == self.root.index:
            self.root = cur
        self.write_node(cur)
        self.write_node(child1)
        self.write_node(child2) 


    def borrow_Pr(self,cur,child1,child2,i):

        for j in range(child1.n-1,-1,-1):
            child1.keys[j+1] = child1.keys[j]
        child1.keys[0] = cur.keys[i-1]
        if child1.leaf == 0:       
            for j in range(child1.n,-1,-1):
                child1.child[j+1] = child1.child[j]
            cild1.child[0] = child2.child[child2.n] 
        cur.keys[i-1] = child2.keys[child2.n - 1]
        child2.keys[child2.n-1] = 0        
        child2.n -= 1 
        child1.n += 1
        if cur.index == self.root.index:
            self.root = cur

        self.write_node(cur)
        self.write_node(child1)
        self.write_node(child2) 
              
          
        
       
    def remove_from_leaf(self,cur,i):
        for j in range(i+1,cur.n,1):
            cur.keys[j-1] = cur.keys[j]            
        cur.keys[cur.n-1] = 0            
        cur.n -= 1
        if cur.index == self.root.index:
            self.root = cur
        self.write_node(cur)
        
        
    def remove_from_non_leaf(self,cur,i):       
        childPr = Node(self.t,cur.child[i])
        self.read_node(cur.child[i],childPr)
        if childPr.n >= self.t:
            cur.keys[i] = self.getPr(cur,i)
            if cur.index == self.root.index:
                self.root = cur
            self.remove(cur.child[i],self.getPr(cur,i))
            
        else:            
            childSuc = Node(self.t,cur.child[i+1])
            self.read_node(cur.child[i+1],childSuc)            
            if childSuc.n >= self.t:  
                 
                cur.keys[i] = self.getSuc(cur,i)
                if cur.index == self.root.index:
                    self.root = cur
                self.remove(cur.child[i+1],self.getSuc(cur,i))                                      
            else:                
                self.merge(cur,childPr,childSuc,i)
                for j in range(i+1,cur.n,1): 
                    cur.keys[j-1] = cur.keys[j]
                cur.keys[cur.n-1] = 0
                
                for j in range(i+2,cur.n+1,1): 
                    cur.child[j-1] = cur.child[j]
                cur.child[cur.n] = 0
                cur.n -= 1
                if cur.index == self.root.index:
                    self.root = cur
                if cur.n == 0:
                    self.root = childPr              
                self.remove(childPr.index,childPr.keys[self.t-1])                
        self.write_node(cur)
        
                
    def merge(self,cur,child1,child2,i):
        print i
        child1.keys[self.t-1] = cur.keys[i]
        for j in range(self.t-1):
            child1.keys[j + self.t] = child2.keys[j]
            child2.keys[j] = 0
        if child1.leaf == 0:
            for j in range(child2.n+1):
                child1.child[j + self.t] = child2.child[j]                        
                child2.child[j] = 0
        child1.n += child2.n + 1
        #print child1
        #print child2
        self.write_node(child1)
               
                          
                                     
                    
        
                
                               
def test_ins(n,t):                            
    r = Btree(t,'B_tree.txt')
    for i in range(7,n,1):
        r.insert(i)
    #r.insert(1)
  
    r.traverse()
    #print r.getPr(r.root,0)
    #print r.getSuc(r.root,0) 
    x = Node(t,r.root.index)
    r.read_node(r.root.index,x)
    r.remove(r.root.index,7)
    r.remove(r.root.index,10)
    print('\n')
    r.traverse()         
test_ins(11,2) 
#print r.getPr(self.root,1)                 
                        
"""            
m1 = Node(2,3,[10,11]) 
m2 = Node(2,4,[21,22])
m3 = Node(2,5,[45])
m4 = Node(2,6,[52])
m5 = Node(2,7,[65,67])
m6 = Node(2,8,[76])                                           

y = Node(2,1,[20,40], False,[m1,m2,m3])
z = Node(2,2,[60,70],False,[m4,m5,m6])

x = Node(2, 0, [50],False, [y,z])
    
x = Node(2,1)
x.n = 1
x.keys = [50,0,0]
x.leaf = 0
x.child = [2,3,0,0]
m1 = Node(2,2) 
m1.n = 3
m1.keys = [10,11,16]
m2 = Node(2,3)
m2.n = 2
m2.keys = [61,62]
"""
#print x.child[1].child[0]  
#r = Btree(50,'B_tree.txt')
#for i in range(10900):
 #   r.insert(i)
#print r.size   
#open('B_tree.txt','w')
#print calcsize('i')
#for t in range(10,100,10):
 #   s = test_ins(5000,t)
#for t in range(100,1000,100):
#   t1 = timeit.Timer("test_ins(5000,t)", "from __main__ import test_ins,t")
#   print(t1.timeit(number = 1),t,4*(4*t+1))


#t1 = timeit.Timer("r.search(1000)", "from __main__ import r")
#print(t1.timeit(number = 1),t,4*(4*t+1))

