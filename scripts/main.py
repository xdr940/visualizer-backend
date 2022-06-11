
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





def cmd(template,cmd_str):
    msg_to_frontend = template
    msg_to_frontend['value'] =cmd_str
    msg_to_frontend = str(msg_to_frontend).replace('\'','\"')
    return msg_to_frontend


def make_fwds(template,fwds_add,fwds_mv=None,):
    msg_to_frontend = template.copy()
    msg_to_frontend['add'] = fwds_add
    msg_to_frontend['remove'] =[]
    msg_to_frontend = str(msg_to_frontend).replace('\'','\"')

    return msg_to_frontend



async def main(websocket,path,args):
    yml = YamlHandler(args.settings)
    config = yml.read_yaml()
    cmd_list = config['cmd_list']
    templates = json2dict(config['templates_path'])

    print("Connection established.")
    print("Listening...")

    while True:
        first_msg = await websocket.recv()
        if first_msg == "hello":
            print("hello from frontend")
            break


    # get static status here
    await websocket.send(cmd(templates[0],"get links"))
    msg = await websocket.recv()
    msg = json.loads(msg)
    fwds_all = msg['value']





    routeing = MPLF(fwds_all=fwds_all)




    positions=None
    msg_to_frontend=None

    while True:

        # test
        cmd_value = input("Sending:")
        if cmd_value in cmd_list:
            await websocket.send(cmd(templates[0],cmd_value))
        else:
            print("wrong cmd, retry")
            continue


        print("Wating msg from frontend...")




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

            await websocket.send(make_fwds(template=templates[1],fwds_add=fwds_add))
            print("send fwds ok")
        elif msg_from_frontend['cls']=="nack":
            break
        elif msg_from_frontend['cls']=='ack':
            continue
        del msg_from_frontend






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

