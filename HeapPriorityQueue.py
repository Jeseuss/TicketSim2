from PriorityQueueBase import PriorityQueueBase

# HeapPriorityQueue Class Documentation:
# This is a MIN-HEAP implementation of a priority queue using a binary heap data structure.
# In a min-heap, the smallest key (highest priority) is always at the root.
# Implemented using an array-based representation of a binary tree.

class HeapPriorityQueue(PriorityQueueBase): 
    # Inherits from PriorityQueueBase which defines the _Item nested class
    # _Item objects store (key, value) pairs and support comparison operations
    
    # ------------------------------------------------------------------
    # PRIVATE HELPER METHODS (Internal heap operations)
    # ------------------------------------------------------------------
    
    def _parent(self, j):
        """Return the index of the parent node of node at index j"""
        return (j - 1) // 2  # Integer division to find parent in array representation

    def _left(self, j):
        """Return the index of the left child of node at index j"""
        return 2 * j + 1  # Binary heap formula for left child

    def _right(self, j):
        """Return the index of the right child of node at index j"""
        return 2 * j + 2  # Binary heap formula for right child

    def _has_left(self, j):
        """Check if node at index j has a left child"""
        return self._left(j) < len(self._data)  # Check if calculated index is within bounds

    def _has_right(self, j):
        """Check if node at index j has a right child"""
        return self._right(j) < len(self._data)  # Check if calculated index is within bounds

    def _swap(self, i, j):
        """Swap elements at indices i and j in the heap array"""
        self._data[i], self._data[j] = self._data[j], self._data[i]

    def _upheap(self, j):
        """Restore heap order by moving element at index j upward toward root"""
        parent = self._parent(j)  # Find parent index
        if j > 0 and self._data[j] < self._data[parent]:
            # If current node is smaller than its parent (violates min-heap property)
            self._swap(j, parent)  # Swap with parent
            self._upheap(parent)    # Recursively check/swap with new parent
            
    def _downheap(self, j):
        """Restore heap order by moving element at index j downward in the tree"""
        if self._has_left(j):  # If node has at least one child
            left = self._left(j)
            small_child = left  # Assume left child is the smaller
            
            # Check if right child exists and is smaller than left child
            if self._has_right(j):
                right = self._right(j)
                if self._data[right] < self._data[left]:
                    small_child = right  # Right child is actually smaller
            
            # If the smallest child is smaller than current node, swap them
            if self._data[small_child] < self._data[j]:
                self._swap(j, small_child)
                self._downheap(small_child)  # Recursively continue downheap

    # ------------------------------------------------------------------
    # PUBLIC INTERFACE METHODS
    # ------------------------------------------------------------------

    def __init__(self, contents=()):
        """Initialize the priority queue, optionally with initial contents
        
        Args:
            contents: Optional sequence of (key, value) pairs to initialize the heap
        """
        # Convert initial contents to _Item objects and store in list
        self._data = [self._Item(k, v) for k, v in contents]
        
        # If we have more than one element, we need to heapify
        if len(self._data) > 1:
            self._heapify()  # Build heap from initial contents

    def _heapify(self):
        """Transform an arbitrary list into a valid heap (Floyd's heap construction)
        
        Complexity: O(n) - More efficient than adding elements one by one (O(n log n))
        Starts from the last non-leaf node and works backward to the root.
        """
        start = self._parent(len(self) - 1)  # Start at parent of last leaf (last non-leaf node)
        
        # Process all nodes from last non-leaf up to root (inclusive)
        for j in range(start, -1, -1):  # Count down to 0 (root)
            self._downheap(j)  # Fix heap property at node j
            
    def is_empty(self):
        """Return True if priority queue is empty"""
        return len(self._data) == 0

    def __len__(self):
        """Return number of items in the priority queue"""
        return len(self._data)

    def add(self, key, value):
        """Add a key-value pair to the priority queue
        
        Args:
            key: The priority key (lower = higher priority in min-heap)
            value: The value associated with the key
            
        Complexity: O(log n) - Height of the heap
        """
        # Create new item and append to end of array (maintains complete binary tree property)
        self._data.append(self._Item(key, value))
        
        # Restore heap property by bubbling the new item up if needed
        self._upheap(len(self._data) - 1)  # Start from last position

    def min(self):
        """Return (key, value) tuple with minimum key without removing it
        
        Returns:
            Tuple (key, value) with the minimum key
            
        Raises:
            IndexError: If priority queue is empty
            
        Complexity: O(1) - Minimum is always at root (index 0)
        """
        if self.is_empty():
            raise IndexError("Priority queue is empty")
        
        item = self._data[0]  # Root contains minimum element in min-heap
        return (item._key, item._value)  # Return as tuple

    def remove_min(self):
        """Remove and return (key, value) tuple with minimum key
        
        Returns:
            Tuple (key, value) with the minimum key that was removed
            
        Raises:
            Exception: If priority queue is empty
            
        Complexity: O(log n) - Downheap operation after removal
        """
        if self.is_empty():
            raise Exception("Queue is Empty")
        
        # Step 1: Swap root (min element) with last element
        self._swap(0, len(self._data) - 1)
        
        # Step 2: Remove the last element (which was the minimum)
        item = self._data.pop()
        
        # Step 3: Restore heap property by bubbling the new root down if needed
        self._downheap(0)
        
        # Step 4: Return the removed item as (key, value) tuple
        return (item._key, item._value)

# End of HeapPriorityQueue implementation