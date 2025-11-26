from PriorityQueueBase import PriorityQueueBase


class HeapPriorityQueue(PriorityQueueBase): #base class defins _Item, A min-oriented priority queue implemented with a binary heap.

    #non public behaviors------------------

    def _parent(self, j):
        return (j-1)//2

    def _left(self, j):
        return 2*j+1

    def _right(self, j):
        return 2*j+2

    def _has_left(self, j):
        return self._left(j) < len(self._data) #index beyond end of list?

    def _has_right(self, j):
        return self._right(j) < len(self._data) #index beyond end of list?

    def _swap(self, i, j):
        self._data[i], self._data[j], = self._data[j], self._data[i]

    def _upheap(self, j):
        parent = self._parent(j)
        if j > 0 and self._data[j] < self._data[parent]:
            self._swap(j, parent)
            self._upheap(parent) # recur at position of parent

    def _downheap(self, j):
        if self._has_left(j):
            left = self._left(j)
            small_child = left
            if self._has_right(j):
                right = self._right(j)
                if self._data[right] < self._data[left]:
                    small_child = right
            if self._data[small_child] < self._data[j]:
                self._swap(j, small_child)
                self._downheap(small_child)

    #Public behaviors ------------------------------------------------------------------------------

    def __init__(self, contents=()):
        self._data = [self._Item(k, v) for k, v in contents] #create new empty priority queue
        if len(self._data) > 1:
            self._heapify()

    def _heapify(self):
        start = self._parent(len(self) -1) #start at PARENT of last leaf
        for j in range(start, -1, -1): #going to and including the root              

            self._downheap(j)
            
    def is_empty(self):
        return len(self._data) == 0

    def __len__(self):
        return len(self._data) #return the number of items in the priority queue (pq)

    def add(self, key, value):
        #add a key value pair to the pq
        self._data.append(self._Item(key, value))
        self._upheap(len(self._data) - 1) #upheap newly added position

    def min(self): 
        #return but do not remove (k, v) tuple with minimum key, raise exception if empty

        if self.is_empty():
            raise IndexError("Priority queue is empty")
        item = self._data[0]
        return (item._key, item._value)

    def remove_min(self):
        #remove and return (k, v) tuple with minimum key, raise exception if empty.
        if self.is_empty():
            raise Exception("Queue is Empty")
        self._swap(0, len(self._data) - 1) #put minimum item at the end of the queue
        item = self._data.pop() #and remove it from the list
        self._downheap(0)
        return (item._key, item._value)

#An implemntation of a priority queue using an array - based heap


    
