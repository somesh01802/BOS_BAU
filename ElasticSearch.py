# -*- coding: utf-8 -*-
"""
Created on Mon May 31 15:22:56 2021

@authors: Sundar Muthuraman,Hariharan Ashokan
"""


from Model.ApiCallFlow import ApiCallFlow

class ElasticSearch:
    """
    Class ElasticSearch is base class for performing api calls to perform any operation on the Elastic Search Tool and this class uses all the base concepts of ApiCallFlow 
    
    Instantiate the object with or without auth based on the requirements 

    """
    
    def __init__(self,verify:bool=False,*,
                 username:str='',password:str=''):
        if verify == True:
            self.username = username
            self.password = password
            self._base = ApiCallFlow(use_auth=True,
                                     username = self.username,
                                    password =self.password,
                                    use_response_code=False)
            
        else:
            self._base = ApiCallFlow(use_response_code=False)
            
        self._call = self._base.crud
       
        
    
    def _urljoin(self,base:str,*args:tuple):
        """
        Joins any number of path from uri and make 
        a URL

        Parameters
        ----------
        base : str
            Base URI path.
        *args : tuple
            Additonal Paths.

        Returns
        -------
        URL
            Creates a complete URL.

        """
        args = tuple(map(lambda x:str(x).replace('/',''),args))
        return '/'.join((str(base),*args))
    
    
    def refresh_index_by(self, *, method:str, uri:str,
                         index:str,header:dict={},
                         verify:bool,**kwargs:dict):
        """
        refresh_index_by :Refreshes one or more indices. 
        For data streams, the API refreshes the stream’s backing indices.

        Parameters
        ----------
        Keyword-only Args:
            method:str
                DESCRIPTION. Provide only get or post
            uri:str
            index : str
            header : dict, optional
                DESCRIPTION. The default is {}.
            query : dict, optional
                DESCRIPTION. The default is {}.
            verify: bool
            **kwargs : dict

        Returns
        -------
        None.

        """
    
        fquery = '_refresh'
        URL =  self._urljoin(uri,index,fquery)
        if method.lower() in ['get','post']:
            process = self._call(method.lower(),
                            URL,header,
                            verify=verify,
                            **kwargs)
            return process
        else:
            raise ValueError("refresh_index_by method expecting only get or post")
        
    
    def get_by(self,uri:str,*,index:str,
               header:dict={},query:dict={},
               verify:bool=True,**kwargs:dict):
        """
        get_by method is used to "GET" the 
        records based on the payload/query

        Parameters
        ----------
        uri : str
        
        Keyword-only Args:
            index : str
            header : dict, optional
                DESCRIPTION. The default is {}.
            query : dict, optional
                DESCRIPTION. The default is {}.
            **kwargs : dict

        Returns
        -------
        List
            Records are returned if fetched else 
            empty list is returned.

        """
        
        # refresh = self.refresh_index_by(method='get',uri=uri,
        #                       index=index,header=header,
        #                       verify=verify,
        #                       **kwargs)
        # print(f"Refreshing index {index}")
        # print(refresh)
        # print(f"Refresh completed for the index {index}")
        fquery = '_search?pretty'
        URL =  self._urljoin(uri,index,fquery)
        process = self._call('get',
                            URL,header,
                            payload=query,
                            verify=verify,
                            **kwargs)
        if process.get("hits","na") != "na" and process['hits'].get("hits","na") != "na":
            return process["hits"]["hits"]
        else:
            return []
        
           
    def insert_by(self,uri:str,data:dict,*,
                  index:str,
                  header:dict={},
                  Hex_id=False,
                  verify:bool=True,**kwargs:dict):
        """
        insert_by method is used to "POST" the 
        records based on the payload and Hex_id is 
        True then uses same for _id in document 
        creation else _id is random generated
        value taken care by Elastic Search.

        Parameters
        ----------
        uri : str
        data : dict
            Payload passed to the index.
        Keyword-only Args:
            index : str
            header : dict, optional
                DESCRIPTION. The default is {}.
            **kwargs : dict

        Returns
        -------
        process : json/dict
            returns json response for the operation.

        """
        
        # refresh = self.refresh_index_by(method='post',uri=uri,
        #                       index=index,header=header,
        #                       verify=verify,
        #                       **kwargs)
        # print(f"Refreshing index {index}")
        # print(refresh)
        # print(f"Refresh completed for the index {index}")
        
        fquery = '_doc'
        if Hex_id:
            _id = data.get("hex_id","NA")
        else:
            _id = "NA"
        if _id == "NA":
            URL =  self._urljoin(uri,index,
                                 fquery)
        else:
            URL =  self._urljoin(uri,index
                                 ,fquery,_id)
        process = self._call('post',
                        URL,header,
                        payload=data,
                        verify=verify,
                        **kwargs)
        return process
        
              
    def delete_by(self,uri:str,query:dict,*,
                  index:str,
                  header:dict={},
                  verify:bool=True,**kwargs:dict):
        """
        delete_by method is used to "POST" the 
        records based on the payload and used
        _delete_by_query is  and its 
        deleted in Elastic Search.
        

        Parameters
        ----------
        uri : str
        query : dict
            Payload passed to the index.
        Keyword-only Args:
            index : str
            header : dict, optional
                DESCRIPTION. The default is {}.
            **kwargs : dict

        Returns
        -------
        process : json/dict
            returns json response for the
            operation.

        """
        fquery = '_delete_by_query'
        URL =  self._urljoin(uri,index,fquery)
        process = self._call('post',
                            URL,header=header,
                            payload=query,
                            verify=verify,
                            **kwargs)
        
        return process
    
    def delete_id(self,uri:str,_id:str,*,
                  index:str,
                  header:dict={},
                  verify:bool=True,**kwargs):
        """
        delete_id method is used to "DLETE" the 
        records based on _id from the records and 
        its deleted in Elastic Search.
        

        Parameters
        ----------
        uri : str
        _id : str
        Keyword-only Args:
            index : str
            header : dict, optional
                DESCRIPTION. The default is {}.
            **kwargs : dict

        Returns
        -------
        process : json/dict
            returns json response for the
            operation.

        """
        
        fquery = '_doc'
        URL =  self._urljoin(uri,index,fquery,_id)
        process = self._call('delete',
                            URL,header=header,
                            verify=verify,
                            **kwargs)
        return process
