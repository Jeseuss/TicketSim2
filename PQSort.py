from HeapPriorityQueue import HeapPriorityQueue


def pq_sort(C):
    """Sort a collection using a priority queue."""
    n = len(C)
    P = HeapPriorityQueue()  # Use your concrete implementation
    
    for j in range(n):
        element = C.delete(C.first())
        P.add(element, element)
    
    for j in range(n):
        (k, v) = P.remove_min()
        C.add_last(v)



