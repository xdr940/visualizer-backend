
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

async def recv_msg(websocket):
    while True:
        # recv_text = await websocket.recv()
        try:
            first_msg = await websocket.recv()
            print("from frontend :{}".format(first_msg))
            if first_msg =="hello":
                return
        except:
            print("little error")
        # recv_dict = dict(recv_dict)
        # response_text = f"your submit context: {recv_text}"


s1="00001"
s2 ="01010"

def modifyData(dct):
    ret = str(dct).replace('\'','\"')
    return ret

async def main(websocket,path,args):
    # yml = YamlHandler(args.settings)
    # config = yml.read_yaml()


    # link to
    print("listening frontend....")

    while True:
        first_msg = await websocket.recv()
        if first_msg == "hello":
            print("hello from frontend")
            print("connected")
            break


    # get static status here



    fwds_all=None
    positions=None
    msg_to_frontend=None
    while True:

        # test
        cls = input("msg2frontend:")
        msg_firstto_frontend={}
        msg_firstto_frontend['cls'] = cls
        await websocket.send(modifyData(msg_firstto_frontend))
        print("send firt data:{}".format(msg_firstto_frontend))
        print("wating msg from frontend...")

        # run
        # msg_to_frontend = {}
        # msg_to_frontend['cls'] = "GET current status"
        # await websocket.send(modifyData(msg_firstto_frontend))



        msg_from_frontend = await websocket.recv()
        print("msg_from_frontend:{}".format(msg_from_frontend)) #test
        msg = json.loads(msg_from_frontend)


        if msg['cls']=='static status':
            fwds_all = parseStaticStatus(msg)
            print("static_status loaded")
        elif msg['cls'] =="current status":
            positions = parseCurrentStatus(msg)
            print("current satus loaded")

            fwds = caculate_route(static_status=fwds_all,current_status=positions,s1='00205',s2='00307')
            msg_to_frontend={}
            msg_to_frontend['cls']="fwds"
            msg_to_frontend['fwds']=fwds
            await websocket.send(modifyData(msg_to_frontend))
            time.sleep(1)
            print("send fwds ok")




def parseStaticStatus(msg):
    fwds_all = msg['fwds_all']
    return fwds_all
def parseCurrentStatus(msg):
    return  msg["positions"]

def caculate_route(static_status,current_status,s1,s2):
    dic = json2dict("./example_routes.json")
    return dic[0]
    pass







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

