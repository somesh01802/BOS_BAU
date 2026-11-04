# -*- coding: utf-8 -*-
"""
Created on Sun May 30 19:13:29 2021

@author: Sundar Muthuraman
"""


#######################################################



#API BASE ABSTRACT

import requests
from requests.auth import HTTPBasicAuth
import json

import traceback,sys

class ApiCallFlow:
    def __init__(self,use_auth=False,*,
                 username='',password='',
                 use_response_code=True):
        
        self.use_response_code = use_response_code
        if use_auth == True and username!= "" and password!="":
            self._username = username
            self._password = password
            
        elif use_auth == True and username== "" and password=="":
            raise ValueError("Username and Password cannot be null")
        elif use_auth==False and  username!= "" and password!="":
           raise ValueError("use_auth is set to False")
        elif use_auth==False and  username== "" and password=="":
          self._username = username
          self._password = password 

          
    def crud(self,function,url,header={},
             payload={},output='json',
             wait=(60,90),verify=False,**kwargs):
        if self.use_response_code == True:
            print(f"use_response_code is set to {self.use_response_code}")
            codes = {"get":200,
                     "post":201,
                     "put":200,
                     "patch":200,
                     "delete":204}
        elif self.use_response_code ==False:
            print(f"use_response_code is set to {self.use_response_code}")
            codes ={}.fromkeys(["get","put",
                                "delete","patch"],
                                200) 
            codes["post"] = 201
        
        action = getattr(requests, 
                       function,
                       "Invalid method passed to 'requests' module, check doc https://docs.python-requests.org/en/master/")
        
        if isinstance(action, str):
            raise AttributeError(action)
            
        
        try:
            if header == {}:
                header = {"Accept":"application/json"}
            
            if payload == {}:
                response = action(url,
                                            
                                   auth = HTTPBasicAuth(self._username,self._password),
                                   headers=header,
                                   timeout = wait,
                                   verify = verify,
                                   **kwargs)
            else:
                params=json.dumps(payload)
                response = action(url,
                                  data=params,
                                  auth = HTTPBasicAuth(self._username,self._password),
                                  headers=header,
                                  timeout = wait,
                                  verify = verify,
                                  **kwargs)
            
            if response.status_code != codes[function]:
                print(f"Status Code is {response.status_code} Message is {response.headers}")
                return response.json()
            
            else:
                print(f"Status Code is {response.status_code}")
                return response.json()
        
        except Exception:
            print("-"*40)
            traceback.print_exception(*sys.exc_info())
            raise             
    

