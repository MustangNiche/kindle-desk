import random

def make_manifest(count,anchor):
    order=list(range(1,count+1))
    random.Random(20260920).shuffle(order)
    return {'count':count,'anchor':anchor,'order':order,'order_version':1}
