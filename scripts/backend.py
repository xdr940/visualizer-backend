
from utils.yaml_wrapper import YamlHandler
import functools
import time
import argparse
import json
import datetime
import matplotlib.pyplot as plt
import os
import websockets
import asyncio
from path import Path
from utils.tool import json2dict,dict2json,to_csv,read_csv

from route.mplf import MPLF
from itertools import combinations
import json
import numpy as np
import random
random.seed(1234)
from tqdm import tqdm


def cmd(template,arg):
    msg_to_frontend = template.copy()
    msg_to_frontend['arg'] =arg
    return  json.dumps(msg_to_frontend)


def make_fwds(template,fwds_add,fwds_mv=None,):
    msg_to_frontend = template.copy()
    msg_to_frontend['add'] = fwds_add
    msg_to_frontend['remove'] =[]
    return  json.dumps(msg_to_frontend)

def route2fwds(routes):
    add_fwds = []
    i = 0
    j = 1
    while j < len(routes):
        add_fwds.append("FWD-{}-{}".format(routes[i], routes[j]))
        j += 1
        i += 1
    return add_fwds


class BackEnd:
    def __init__(self,args):
        yml = YamlHandler(args.settings)
        config = yml.read_yaml()
        self.cmd_list = config['cmd_list']
        root = Path(config['root'])
        self.templates = json2dict(root / config['templates_path'])

        self.save_path = config['save_path']

        pass


        # self.time_stamps = [
        #     "2000-01-01T00:00:00Z",
        #     "2000-01-01T00:15:00Z",
        #     "2000-01-01T00:30:00Z",
        #     "2000-01-01T00:45:00Z",
        #     "2000-01-01T01:00:00Z",
        #     "2000-01-01T01:15:00Z",
        #     "2000-01-01T01:30:00Z",
        #     "2000-01-01T01:45:00Z",
        #     "2000-01-01T02:00:00Z",
        #     "2000-01-01T02:15:00Z",
        #     "2000-01-01T02:30:00Z",
        #     "2000-01-01T02:45:00Z",
        #     "2000-01-01T03:00:00Z",
        #     "2000-01-01T03:15:00Z",
        #     "2000-01-01T03:30:00Z",
        #     "2000-01-01T03:45:00Z",
        #     "2000-01-01T04:00:00Z",
        #     "2000-01-01T04:15:00Z",
        #     "2000-01-01T04:30:00Z",
        #     "2000-01-01T04:45:00Z",
        #     "2000-01-01T05:00:00Z",
        #     "2000-01-01T05:15:00Z",
        #     "2000-01-01T05:30:00Z",
        #     "2000-01-01T05:45:00Z",
        #     "2000-01-01T06:00:00Z"
        #
        # ]
        self.time_stamps=[
            "2000-01-01T00:10:00Z",
            "2000-01-01T00:11:00Z",
            "2000-01-01T00:12:00Z",
            "2000-01-01T00:13:00Z",
            "2000-01-01T00:14:00Z",
            "2000-01-01T00:15:00Z",
            "2000-01-01T00:16:00Z",
            "2000-01-01T00:17:00Z",
            "2000-01-01T00:18:00Z",
            "2000-01-01T00:19:00Z",
            "2000-01-01T00:20:00Z"

        ]



    async def exp1(self,websocket,routing):
        time_stamps = self.time_stamps
        yy=datetime.datetime.now().year
        mm=datetime.datetime.now().month
        dd=datetime.datetime.now().day
        hh=datetime.datetime.now().hour
        mi=datetime.datetime.now().minute
        ss=datetime.datetime.now().second
        stem = "{}{:02d}{:02d}_{:02d}{:02d}{:02d}".format(yy,mm,dd,hh,mi,ss)
        save_dir = Path(self.save_path)/stem
        save_dir.mkdir_p()

        sat_num = len(self.sats_all)

        hour = 0

        for time_stamp in tqdm(time_stamps):
            pass


            # get positions
            tmp_cmd = {
                "id": 0 ,
                "do": "get",
                "arg":"positions"
            }
            await websocket.send(json.dumps(tmp_cmd))
            msg = await websocket.recv()
            msg = json.loads(msg)

            positions = msg['data']

            # set time
            tmp_cmd2 = {
                "id": 0,
                "do": "set",
                "arg": "time"
            }
            tmp_cmd2['value'] = time_stamp
            await websocket.send(json.dumps(tmp_cmd2))
            msg2 = await websocket.recv()




            idx_sats = np.linspace(0, sat_num - 1, sat_num).astype(np.int32)
            random.shuffle(idx_sats)



            results = []
            MAX_LENGTH=1000
            cnt=0
            for src_idx,dst_idx in combinations(idx_sats,2):
                src = self.sats_all[src_idx]
                dst = self.sats_all[dst_idx]

                routes, route_positions = routing(positions=positions, src=src, dst=dst)
                # print(routes)
                # time.sleep(1)
                item={}
                item['src,dst'] = (src,dst)
                item['routes'] = routes
                # item['positions'] = route_positions
                results.append(item)
                cnt +=1
                if cnt >MAX_LENGTH:
                    break
            dict2json(save_dir/'{:02d}_routes.json'.format(hour),results)
            dict2json(save_dir/'{:02d}_positions.json'.format(hour),positions)
            hour+=1
        print("-> exp1 over, save at {}".format(save_dir))

    async def exp2(self, websocket, routing):
        src_gs = 'Harbin'
        dst_gs = 'London'

        yy = datetime.datetime.now().year
        mm = datetime.datetime.now().month
        dd = datetime.datetime.now().day
        hh = datetime.datetime.now().hour
        mi = datetime.datetime.now().minute
        ss = datetime.datetime.now().second
        stem = "{}{:02d}{:02d}_{:02d}{:02d}{:02d}".format(yy, mm, dd, hh, mi, ss)
        save_dir = Path(self.save_path) / stem
        save_dir.mkdir_p()



        # set time
        cnt = 0
        src_sats = []
        dst_sats = []
        for time_stamp in tqdm(self.time_stamps):
        #     pass

            # time
            tmp_cmd0 = {
                "id": 0,
                "do": "set",
                "arg": "time"
            }
            tmp_cmd0['value'] = time_stamp
            await websocket.send(json.dumps(tmp_cmd0))
            msg0 = await websocket.recv()


            # gsl
            tmp_cmd = {
            "id": 0,
            "do": "get",
            "arg": "gsls"
            }


            await websocket.send(json.dumps(tmp_cmd))
            msg = await websocket.recv()
            msg = json.loads(msg)
            gsls = msg['data']

            # positions
            tmp_cmd2 = {
                "id": 0,
                "do": "get",
                "arg": "positions"
            }
            # tmp_cmd['value'] = time_stamp
            await websocket.send(json.dumps(tmp_cmd2))
            msg2 = await websocket.recv()
            msg2 = json.loads(msg2)
            positions = msg2['data']




            for gsl in gsls:
                sat_name = gsl[4:9]
                gs_name = gsl[10:]
                if gs_name ==src_gs:
                    src_sats.append(sat_name)
                elif gs_name == dst_gs:
                    dst_sats.append(sat_name)


            print("\nsrcs: {}".format(src_sats))
            print("dsts: {}".format(dst_sats))

            print('gsls: {}'.format(gsls))
            hited =[]
            for src_sat in src_sats:
                for dst_sat in dst_sats:
                    routes, route_positions = routing(positions=positions, src=src_sat, dst=dst_sat)
                    if routes[-1] == dst_sat:
                        hited.append(routes)


            if len(hited)==0:
                print("none at {}".format(cnt))
            else:
                print('hited at {}'.format(cnt))
                print(hited)

                dict2json(save_dir / '{:02d}_routes.json'.format(cnt), hited)
                dict2json(save_dir / '{:02d}_positions.json'.format(cnt), positions)
            src_sats.clear()
            dst_sats.clear()
            time.sleep(3)
            cnt+=1


    def parse_cmd(self,line):
        cmd_packet = {
            "id":0
        }
        isFinish = False
        words = line.split(" ")
        if words[0] =='set':
            cmd_packet['do'] = words[0]

            if words[1] =='time':
                cmd_packet['arg'] = words[1]

                if len(words[2]) == 20:
                    cmd_packet['value'] = words[2]
                    isFinish = True


            if words[1] =='start':
                cmd_packet['arg'] = words[1]
                isFinish = True

            if words[1] =='stop':
                cmd_packet['arg'] = words[1]
                isFinish = True

            pass
        elif words[0]=='get':
            cmd_packet['do'] = words[0]

            if words[1] =='positions':
                cmd_packet['arg'] = words[1]
                isFinish = True

            elif words[1] == 'links':
                cmd_packet['arg'] = words[1]
                isFinish = True
            elif words[1] =='gsls':
                cmd_packet['arg'] = words[1]
                isFinish = True

            pass
        elif words[0] == 'clear':
            cmd_packet['do'] = words[0]
            if words[1]=='fwds':
                cmd_packet['arg'] = words[1]
                isFinish = True



        if isFinish:
            return cmd_packet
        else:
            return None


    async def main(self,websocket,path):

        print("Connection established.")
        print("Listening...")

        while True:
            first_msg = await websocket.recv()
            if first_msg == "hello":
                print("hello from web")
                break

        # init
        await websocket.send(cmd(self.templates[0], "links"))
        msg = await websocket.recv()
        msg = json.loads(msg)
        fwds_all = msg['data']
        routing = MPLF(fwds_all=fwds_all)
        print("fwds_all ok")



        await websocket.send(cmd(self.templates[0], "sats"))
        msg = await websocket.recv()
        msg = json.loads(msg)
        self.sats_all = msg['data']
        print("sats_all ok")




        positions=None
        msg_to_frontend=None

        while True:

            # test
            cmd_str = input("Server>")

            packet = self.parse_cmd(cmd_str)



            if cmd_str=="exp1":
                await self.exp1(websocket,routing)
            elif cmd_str =="exp2":
                await  self.exp2(websocket,routing)
            elif cmd_str == "route":
                # caculate fwds and send
                src_dst = input("src,dst:")
                src1, dst1 = src_dst.split(' ')
                routes, _ = routing(positions=positions, src=src1, dst=dst1)
                fwds_add = route2fwds(routes)
                # print(fwds_add)
                await websocket.send(make_fwds(template=self.templates[2], fwds_add=fwds_add))
                print("send fwds ok")
            elif packet:
                print(packet)
                await websocket.send(json.dumps(packet))
            else:
                print("-> wrong cmd, retry")
                continue


            print("-> Wating msg from frontend...")




            # recv from frontend
            msg_from_frontend = await websocket.recv()
            print("recv msg from frontend.") #test
            # print(msg_from_frontend)
            msg_from_frontend = json.loads(msg_from_frontend)


            if msg_from_frontend['do']=='transmit':
                if msg_from_frontend['arg']=='links':
                    fwds_all = msg_from_frontend['data']
                    print("links loaded")
                elif msg_from_frontend['arg']=='positions':
                    positions = msg_from_frontend['data']
                    print("positions loaded")



            elif msg_from_frontend['do']=="nack":
                break
            elif msg_from_frontend['do']=='ack':
                continue
            del msg_from_frontend






if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="constellation-information")
    if os.path.exists('../configs/config.yaml'):
        parser.add_argument("--settings", default='../configs/config.yaml')
    else:
        parser.add_argument("--settings", default='./configs/config.yaml')

    args = parser.parse_args()
    backend = BackEnd(args)
    start_server = websockets.serve(backend.main, "192.168.3.2", 5678)

    asyncio.get_event_loop().run_until_complete(start_server)
    print("open frontend please...")

    asyncio.get_event_loop().run_forever()


