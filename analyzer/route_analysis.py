
from path import Path
from utils.tool import json2dict,dict2json
import numpy as np
import matplotlib.pyplot as plt
class RouteAnalysis:
    def __init__(self):
        self.dir = Path("/home/roit/models/mplf/20220628_004404")
        pass
    def end2end_route_stat(self,dir_path):
        dir_path = Path(dir_path)
        description_p = dir_path/"description.json"
        description = json2dict(description_p)
        time_stamps = description['time_stamps']
        hited_index = description['hited_index']

        position_files = dir_path.files('*_positions.json')
        route_files = dir_path.files('*_routes.json')

        position_files.sort()
        route_files.sort()
        p2p_distance_time = {}
        for position_file,route_file,index in zip(position_files,route_files,hited_index):
            p2p_distance = []


            position = json2dict(position_file)
            multi_route = json2dict(route_file)
            route=multi_route[0]
            i=0
            while i +1< len(route):
                p1 =np.array( position[route[i]])
                p2 =np.array( position[route[i+1]])


                p2p_distance.append(np.linalg.norm(p1- p2))
                i+=1
            p2p_distance_time[time_stamps[index]] = p2p_distance

        return p2p_distance_time

        pass
    def routable(self,route_file):
        routes = json2dict(route_file)
        routeable=0
        for item in routes:
            src,dst = item['src,dst']
            if dst== item['routes'][-1]:
                routeable+=1

        ret = routeable / len(routes)
        return ret
    def routable_stat(self):
        files = self.dir.files("*.json")
        files.sort()
        probalities =[]
        for file in files:
            if file.stem[3:] =="routes":
                probalities.append(self.routable(file))
        print(probalities)
        return probalities

    def last_dis(self):
        files = self.dir.files("*.json")
        files.sort()
        probalities = []
        cnt =0
        distance_time=[]
        while cnt+1 < len(files):
            positions = json2dict(files[cnt])
            routes = json2dict(files[cnt+1])
            distance_random=[]
            for item in routes:
                src,dst = item['src,dst']
                end = item['routes'][-1]
                # if end!=dst:
                dis = np.array(positions[end]) - np.array(positions[dst])
                dis = dis**2
                dis = dis.sum()
                dis **=0.5
                distance_random.append(dis)
            distance_time.append(distance_random)
            cnt+=2
        distance_time = np.array(distance_time)
        return distance_time.mean(axis=1)


# ps = RouteAnalysis().last_dis()
# ps = list(ps)
# print('[',end=' ')
# for item in ps:
#     print("{:.2f}".format(float(item/1000)),end=', ')
# print(']')
#
# plt.plot(ps)
# plt.show()