#!/usr/bin/env python3

from threading import Thread
import socket, logging, ssl, json
import string
import random
import bumper
import time
from datetime import datetime, timedelta
import asyncio
import contextvars
from aiohttp import web

class ConfServer():
    bumper_clients = contextvars.ContextVar

    def __init__(self, address, usessl=False, run_async=True, bumper_clients=contextvars.ContextVar, helperbot=None):
        self.bumper_clients = bumper_clients
        self.helperbot = helperbot
        self.usessl = usessl
        self.run_async = run_async
        self.address = address  
        

        try:                        
            if run_async:
                logging.debug("Starting ConfServer Thread: 1")
                confserver = Thread(name="ConfServer_Thread",target=self.run_server)
                self.server = confserver
                confserver.setDaemon(True)
                confserver.start()
                
            else:
                try:
                    self.run_server()
                except KeyboardInterrupt:
                    self.disconnect()
        except Exception as e:
            logging.error('ConfServer: {}'.format(e))


    def run_server(self):
        try:
            loop = asyncio.get_event_loop()
        except:
            loop = asyncio.new_event_loop()
        
        loop.run_until_complete(self.start_server())
        loop.run_forever()
                

    async def start_server(self):              
        app = web.Application()        
        
        app.add_routes([
            web.get('/{apiversion}/private/{country}/{language}/{devid}/{apptype}/{appversion}/{devtype}/{aid}/user/login', self.handle_login),
            web.get('/{apiversion}/private/{country}/{language}/{devid}/{apptype}/{appversion}/{devtype}/{aid}/user/logout', self.handle_login),
            web.get('/{apiversion}/private/{country}/{language}/{devid}/{apptype}/{appversion}/{devtype}/{aid}/user/getAuthCode', self.handle_getAuthCode),
            web.get('/{apiversion}/private/{country}/{language}/{devid}/{apptype}/{appversion}/{devtype}/{aid}/user/checkAgreement', self.handle_checkAgreement),
            web.get('/{apiversion}/private/{country}/{language}/{devid}/{apptype}/{appversion}/{devtype}/{aid}/common/getAuthCode', self.handle_checkVersion),
            web.get('/{apiversion}/private/{country}/{language}/{devid}/{apptype}/{appversion}/{devtype}/{aid}/campaign/homePageAlert', self.handle_homePageAlert),

            web.post('/api/users/user.do', self.handle_usersapi),
            web.post('/api/pim/product/getProductIotMap', self.handle_getProductIotMap),
            web.post('/api/iot/devmanager.do', self.handle_devmanager)
        ])    
           

        runner = web.AppRunner(app, access_log=None) #access_log=None so the output isn't nuts
        await runner.setup()
        
        if self.usessl:
            ssl_ctx = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
            ssl_ctx.load_cert_chain('./certs/cert.pem', './certs/key.pem')
            site = web.TCPSite(runner, host=self.address[0], port=self.address[1],ssl_context=ssl_ctx)
            
        else:    
            site = web.TCPSite(runner, host=self.address[0], port=self.address[1])
      
        await site.start()
    

    async def handle_login(self, request):              
        #Could implement basic auth if you wanted, or just accept anything    
        countrycode = request.match_info.get('country', "us")            
        body = {
                "code": "0000",
                "data": {
                "accessToken": "tempaccesstoken", #Random chars 32 length
                "country": countrycode,
                "email": "null@null.com",
                "uid": "fuid_1", #Date(14)_RandomChars(32)
                "username": "fusername_1" #Random chars 8
                },
                "msg": "操作成功",
                "time": bumper.get_milli_time(time.time())
                }    
                                            
        return web.json_response(body)

    async def handle_logout(self, request):                      
        body = {"code": "0000","data": None,"msg": "操作成功", "time": bumper.get_milli_time(time.time())}
                                            
        return web.json_response(body)        

    async def handle_getAuthCode(self, request):                      
        countrycode = request.match_info.get('country', "us")       
        body = {
                "code": "0000",
                "data": {
                "authCode": "{}_tempauthcode".format(countrycode), #countrycode_randomchars(32)
                "ecovacsUid": "fuid_1" #Date(14)_RandomChars(32)
                },
                "msg": "操作成功",
                "time": bumper.get_milli_time(time.time())
                }         
                                                    
        return web.json_response(body)     

    async def handle_checkVersion(self, request):              
        body = {
                "code": "0000",
                "data": {
                    "c": None,
                    "img": None,
                    "r": 0,
                    "t": None,
                    "u": None,
                    "ut": 0,
                    "v": None
                },
                "msg": "操作成功",
                "time": bumper.get_milli_time(time.time())
            }        
                                                    
        return web.json_response(body)            

    async def handle_checkAgreement(self, request):              
        body = {
                "code": "0000",
                "data": [],
                "msg": "操作成功",
                "time": bumper.get_milli_time(time.time())
            
            }     
                                                    
        return web.json_response(body)  

    async def handle_homePageAlert(self, request):              
        nextAlert = bumper.get_milli_time((datetime.now() + timedelta(hours=12)).timestamp())
        
        body = {
                "code": "0000",
                "data": {
                    "clickSchemeUrl": None,
                    "clickWebUrl": None,
                    "hasCampaign": "N",
                    "imageUrl": None,
                    "nextAlertTime": nextAlert,
                    "serverTime": bumper.get_milli_time(time.time())
                },
                "msg": "操作成功",
                "time": bumper.get_milli_time(time.time())
            }   
                                                
        return web.json_response(body)          

    async def handle_getProductIotMap(self, request):              
        #json_body = json.loads(await request.text())  
        body = {"code":0,"data":[{"classid":"dl8fht","product":{"_id":"5acb0fa87c295c0001876ecf","name":"DEEBOT 600 Series","icon":"5acc32067c295c0001876eea","UILogicId":"dl8fht","ota":False,"iconUrl":"https://portal-ww.ecouser.net/api/pim/file/get/5acc32067c295c0001876eea"}},{"classid":"02uwxm","product":{"_id":"5ae1481e7ccd1a0001e1f69e","name":"DEEBOT OZMO Slim10 Series","icon":"5b1dddc48bc45700014035a1","UILogicId":"02uwxm","ota":False,"iconUrl":"https://portal-ww.ecouser.net/api/pim/file/get/5b1dddc48bc45700014035a1"}},{"classid":"y79a7u","product":{"_id":"5b04c0227ccd1a0001e1f6a8","name":"DEEBOT OZMO 900","icon":"5b04c0217ccd1a0001e1f6a7","UILogicId":"y79a7u","ota":True,"iconUrl":"https://portal-ww.ecouser.net/api/pim/file/get/5b04c0217ccd1a0001e1f6a7"}},{"classid":"jr3pqa","product":{"_id":"5b43077b8bc457000140363e","name":"DEEBOT 711","icon":"5b5ac4cc8d5a56000111e769","UILogicId":"jr3pqa","ota":True,"iconUrl":"https://portal-ww.ecouser.net/api/pim/file/get/5b5ac4cc8d5a56000111e769"}},{"classid":"uv242z","product":{"_id":"5b5149b4ac0b87000148c128","name":"DEEBOT 710","icon":"5b5ac4e45f21100001882bb9","UILogicId":"uv242z","ota":True,"iconUrl":"https://portal-ww.ecouser.net/api/pim/file/get/5b5ac4e45f21100001882bb9"}},{"classid":"ls1ok3","product":{"_id":"5b6561060506b100015c8868","name":"DEEBOT 900 Series","icon":"5ba4a2cb6c2f120001c32839","UILogicId":"ls1ok3","ota":True,"iconUrl":"https://portal-ww.ecouser.net/api/pim/file/get/5ba4a2cb6c2f120001c32839"}}]}
        return web.json_response(body)  

    async def handle_usersapi(self, request):               
        json_body = json.loads(await request.text())
        todo = json_body['todo']
        if todo == 'FindBest':
            service = json_body['service']
            if service == 'EcoMsgNew':
                body = {"result":"ok","ip":socket.gethostbyname(socket.gethostname()),"port":5223}
            elif service == 'EcoUpdate':
                body = {"result":"ok","ip":"47.88.66.164","port":8005}
        elif todo == 'loginByItToken':
            body = {
                "resource": json_body["resource"],
                "result": "ok",
                "todo": "result",
                "token": json_body["token"], #RandomChar(32) 
                "userId": json_body["userId"] #RandomChar(16)
                }   
        elif todo == 'GetDeviceList':
            active_bots = self.bumper_clients.get()
            body = {
                    "devices": active_bots,
                    "result": "ok",
                    "todo": "result"
                    }            
                                                        
        return web.json_response(body)      

    async def handle_devmanager(self, request):
        json_body = json.loads(await request.text())
        randomid = ''.join(random.sample(string.ascii_letters,6))
        retcmd = await self.helperbot.send_command(json_body, randomid)
        body = retcmd

        return web.json_response(body)   

    def disconnect(self):
        logging.info('ConfServer: shutting down...')        
        if(self.run_async):
            self.server.join()
        else:
            self.server.disconnect()
        logging.info('ConfServer: bye')        
    