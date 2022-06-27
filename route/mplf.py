
import numpy as np


def similarity(vec1, vec2):
    assert vec1.shape[-1] == vec2.shape[-1]

    tmp = np.sum(vec1 ** 2) * np.sum(vec2 ** 2, axis=1)
    tmp = tmp ** 0.5
    tmp = np.sum(vec2 * vec1, axis=1) / tmp
    return tmp


class MPLF:
    def __init__(self,*args, **kwargs):
        fwds_all = kwargs['fwds_all']
        self.adj_table ={}
        for fwd in fwds_all:
            src = fwd[4:9]
            dst = fwd[10:]
            if src not in self.adj_table.keys():
                self.adj_table[src]=[]
            self.adj_table[src].append(dst)

        pass
    def restParam(self):
        pass
    def get_adj_positions(self,sat,positions):
        adj_positions=[]
        for p in self.adj_table[sat]:
            adj_positions.append(positions[p])
        return np.array(adj_positions)





    def __call__(self, *args, **kwargs):
        src = kwargs['src']
        dst = kwargs['dst']
        positions = kwargs['positions']
        dst_position =np.array(positions[dst])
        current_position = np.array(positions[src])
        current_sat = src
        routes = [src]
        max_hop = 30
        cnt=0
        route_positions=[]
        while True:

            vec = dst_position - current_position
            adj_pos = self.get_adj_positions(current_sat,positions)
            cmp_vecs = adj_pos - current_position
            cos_sim = similarity(vec,cmp_vecs)
            current_sat = self.adj_table[current_sat][np.argmax(cos_sim)]
            if len(routes)>2 and current_sat == routes[-2]:
                routes.pop(-1)
                # print("-> un-routable")
                break
            elif current_sat == dst:
                # print("-> successful route")
                routes.append(current_sat)

                break
            if cnt>max_hop :
                break
            routes.append(current_sat)
            current_position = positions[current_sat]
            cnt+=1



        for sat in routes:
            route_positions.append(positions[sat])
        return routes,route_positions
