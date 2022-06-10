
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


src="00001"
dst ="00109"



def cmd(cmd_str):
    msg_to_frontend = templates[CMD_TEM]
    msg_to_frontend['value'] =cmd_str
    msg_to_frontend = str(msg_to_frontend).replace('\'','\"')
    return msg_to_frontend


def make_fwds(fwds_add,fwds_mv=None):
    msg_to_frontend = templates[FWDS_TEM].copy()
    msg_to_frontend['add'] = fwds_add
    msg_to_frontend['remove'] =[]
    msg_to_frontend = str(msg_to_frontend).replace('\'','\"')

    return msg_to_frontend



async def main(websocket,path,args):
    # yml = YamlHandler(args.settings)
    # config = yml.read_yaml()
    print("Connection established.")
    print("Listening...")

    while True:
        first_msg = await websocket.recv()
        if first_msg == "hello":
            print("hello from frontend")
            break


    # get static status here
    await websocket.send(cmd("get links"))
    msg = await websocket.recv()
    msg = json.loads(msg)
    fwds_all = msg['value']
    print(fwds_all)





    routeing = MPLF(fwds_all=fwds_all)




    positions=None
    msg_to_frontend=None

    while True:

        # test
        cmd_value = input("Sending:")
        if cmd_value in CMD_LIST:
            await websocket.send(cmd(cmd_value))
        else:
            print("wrong cmd, retry")
            continue


        print("Wating msg from frontend...")
        time.sleep(2)




        # recv from frontend
        msg_from_frontend = await websocket.recv()
        # print("recv msg from frontend:{}".format(msg_from_frontend)) #test
        print("recv msg from frontend.") #test
        msg_from_frontend = json.loads(msg_from_frontend)


        if msg_from_frontend['cls']=='links':
            fwds_all = msg_from_frontend['value']
            print("links loaded")
        elif msg_from_frontend['cls'] =="positions":
            positions = msg_from_frontend['value']
            print("positions loaded")

            # caculate fwds and send
            src_dst = input("src,dst:")
            src1,dst1 = src_dst.split(' ')
            fwds_add = routeing(positions=positions, src=src1, dst=dst1)
            print(fwds_add)
            time.sleep(1)

            await websocket.send(make_fwds(fwds_add=fwds_add))
            print("send fwds ok")
        elif msg_from_frontend['cls']=="nack":
            break
        elif msg_from_frontend['cls']=='ack':
            continue



def parseStaticStatus(msg):
    fwds_all = msg['fwds_all']
    return fwds_all
def parseCurrentStatus(msg):
    return  msg["positions"]

def caculate_route(static_status,current_status,s1,s2):
    dic = json2dict("./templates.json")
    #TODO
    return dic[0]
    pass


CMD_LIST=[
    "get links",#例如邻接信息
    "get positions",# 例如位置
    "clear fwds"
]
# fwds_template =  {
#         "cls":"fwds",
#         "id":"0",
#         "stamp":"2000-01-01T00:00:44+00:00",
#         "add":None,
#         "remove":None
#     }

templates =  json2dict("./templates.json")
FWDS_TEM = 0
CMD_TEM=1


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="constellation-information")
    if os.path.exists('../configs/config.yaml'):
        parser.add_argument("--settings", default='../configs/config.yaml')
    else:
        parser.add_argument("--settings", default='./configs/config.yaml')

    args = parser.parse_args()
    print("open frontend please...")
    start_server = websockets.serve(functools.partial(main, args=args), "192.168.3.2", 5678)
    asyncio.get_event_loop().run_until_complete(start_server)
    asyncio.get_event_loop().run_forever()

