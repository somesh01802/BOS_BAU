#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jul 29 18:04:30 2021

@author: Sundar Muthuraman,Hariharan Ashokan
"""
#Standard Library
from datetime import datetime, timedelta, timezone
import traceback,sys
import time
import configparser, os
import yaml
import json
from pathlib import Path
import ast

#Third-party Library
from jinja2 import Template

#User defined Library
from Model import ElasticSearch, Symphony
from Operations import ConfigStore
from AdditionalPlugins import Plugins
from FieldCaseConversion import CaseConvertor
from Logging import controller
from dlogger import initialize_logger

class ProcessHandler:    
    """
    ProcessHandler is a main class for performing below operations in a sequential order
    
    1. Handle resolved alerts   
    2. Update priority
    3. Resolve to ITSM
    4. Resolve from ITSM
    5. Create ticket
    """
    
    process_lookup = {
        "create_ticket" : {
            "function_name" : "post_operation",
            "sn_property_val" : "fields_to_create_ticket",
            "es_property_val" : "fields_from_itsm"
            },
        "update_ticket" : {
            "function_name" : "post_operation",
            "sn_property_val" : "fields_to_update_ticket",
            "es_property_val" : "fields_to_update_ticket"
            },
        "resolve_ticket_to_itsm" : {
            "function_name" : "post_operation",
            "sn_property_val" : "fields_to_resolve_ticket",
            "es_property_val" : "fields_to_resolve_ticket"
            },
        "resolve_ticket_from_itsm" : {
            "function_name" : "get_details_operation",
            "sn_property_val" : "fields_from_itsm_resolve",
            "es_property_val" : "fields_to_resolve_ticket"
            },
        "update_missing_ticket_number" : {
            "function_name" : "get_ticket",
            "sn_property_val" : "fields_from_itsm_missing_ticket",
            "es_property_val" : "field_to_missing_ticket_number"
            },
        "change_alert_status": {
            "function_name": "get_details_operation",
            "sn_property_val": "fields_for_change_status",
            "es_property_val": "field_to_change_status"

            }
            }
    
   
    def __init__(self,config_path,tlog_path,api_interval,sn_additional_fields_update):
        
        try:
            self.config_path= config_path
            self.es_query, self.es_conf, self.tck_conf, self.tck_payload = ConfigStore(self.config_path,
                            elasticqueryfile = "QueryConfig.yml",
                            elasticconfigfile = "Elastic_Search_Config.yml",
                            ticketconfigfile = "Ticketing_Tool_Config.yml",
                            ticketpayloadfile = "Ticketing_Tool_Payload.yml")
            logger.info(f"Query Config,Elastic Search Config and Ticket Tool config has been parsed from {self.config_path} ")
            
            self.es_conn = ElasticSearch(True,username=self.es_conf.elastic_info['username'],
                                          password=self.es_conf.elastic_info['password'])
            logger.info("Connected object created for Elastic Search....")
            
            self.sy_conn = Symphony()
            logger.info("Connected object created for Symphony....")

            self.sy_uri = self.tck_conf.ticket_info["api_url"]
            self.sy_key = self.tck_conf.ticket_info["api_key"]
            # self.sn_user_uri = self.tck_conf.ticket_info["user_url"]

            self.payload_template = Path("Static_Config/Ticketing_Tool_Payload.yml").read_text(encoding="utf-8")

            self.es_uri = self.es_conf.elastic_info["host"]+":"+str(self.es_conf.elastic_info["port"])
            self.es_idx = self.es_conf.elastic_info["alerts_index"]
            self.es_archive_idx = self.es_conf.elastic_info["alerts_archieve_index"]
            self.es_head = self.es_conf.header
            self.tlogs_path = tlog_path
            self.api_refresh_interval=eval(api_interval)

            #Plugins
            self.plugins = Plugins(logger)
            self.sn_additional_fields_update = sn_additional_fields_update
            
            #Field Case Conversion
            self.fld_case_cnv = CaseConvertor(logger)
            self.reference_field_dict = self.es_conf.reference_field_dict
        except Exception:           
            logger.error ("ProcessHandler initialization failed.")
            expection,expection_msg,tb = sys.exc_info()
            trace = traceback.format_exc()
            logger.error(f"Exception is {expection},happend due to {expection_msg.args} for more info check the trackback {trace}")            
            

    def convert_string_to_date(self, source, timestamp_fields):  
        """
        The function iterate the timestamp_fields and check the field is in the dictionary.
        If the field is present, then convert the field value to date type.

        Parameters
        ----------
        source : dict
            A dictionary contains a key-value pair.
        timestamp_fields : list
            A list of keys(fields) which need to convert from string to date type

        Returns
        -------
        bool

        """
        
        try:
            logger.debug(f"Source recived is {source}")
            for field in timestamp_fields:
                logger.debug(f"Field name is {field}")
                if field in source and source[field]:
                    datetime_object = datetime.strptime(source[field], '%Y-%m-%d %H:%M:%S')
                    date_val = datetime_object.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3]+'Z'
                    source[field] = date_val
                    logger.debug(f"{field} value is set to {date_val}")
                else:
                    logger.info(f"Field name {field} is not in the source")
            return True
        except Exception:
            logger.error ("convert_string_to_date function got failed.")
            expection,expection_msg,tb = sys.exc_info()
            trace = traceback.format_exc()
            logger.error(f"Exception is {expection},happend due to {expection_msg.args} for more info check the trackback {trace}")
            
            
    def split_value(self,hex_id):
        """
        Split the string value by '-'
        If the '|' is present in string then splitting the value by '|' and returing it.

        Parameters
        ----------
        hex_id : Str

        Returns
        -------
        Str

        """

        try:
            logger.info(f"Split value function received hex_id is {hex_id}")
            s1 = hex_id.split("-",1)[1]
            logger.debug(f"Step 1 value is {s1}")
            if "|" in s1:
                s2 = s1.split("|")[0]
                logger.debug(f"Step 2 value is {s2}")
                return s2
            return s1
        except IndexError:
            if not hex_id:
                return "hostunknown"
            return hex_id
        except:
            logger.error ("Split value execution got failed")
            expection,expection_msg,tb = sys.exc_info()
            trace = traceback.format_exc()
            logger.error(f"Exception is {expection},happend due to {expection_msg.args} for more info check the trackback {trace}")
            
            
    def query_elastic_search(self,query,index):
        """
        The function execute the supplied query in elastic search and return the result.
        If the execution failed/failed during fetching record then return empty list.

        Parameters
        ----------
        query : Dict
            Query which need to execute in elastic search
        index : Str
            Index name in the elastic search

        Returns
        -------
        List
            Either its a empty list or list of dictionaries

        """
        
        try:
            logger.info(f"Executing the below query in {index} index")
            logger.debug(f"Query is :- {query}")
            res = self.es_conn.get_by(uri = self.es_uri
                             ,index = index
                             ,query=query
                             ,header= self.es_head)
            logger.info(f"Elastic search query executed successfully and fetched {len(res)} records")
            if res:
                cnv_fields_result = self.fld_case_cnv.convert_field_case(case_type = 'upper',
                                                                        source_data = res,
                                                                        reference_field_type = self.reference_field_dict
                                                                        )
                return cnv_fields_result
            else:
                return []
        
        except Exception:
            logger.error ("Elastic search query execution got failed")
            expection,expection_msg,tb = sys.exc_info()
            trace = traceback.format_exc()
            logger.error(f"Exception is {expection},happend due to {expection_msg.args} for more info check the trackback {trace}")

            
    def generate_es_payload(self,*,sy_res,record,req_fields):
        """
        Preparing payload for elastic search api call.
        Updating value to the required fields from service now response and appending that to source record.

        Parameters
        ----------
        * : TYPE
        sy_res : dict
            Response from service now
        record : dict
            Source record which we extracted from elastic search
        req_fields : dict
            The fields required to update in elastic search

        Returns
        -------
        bool
            return True if the process success otherwise returning False

        """
        
        try:            
            logger.info("Generating payload for elastic search")
            data = {k:sy_res[v] for k,v in req_fields.items()}
            
            data['Hex_LastUpdated'] = datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3]+'Z'
            return_val = self.convert_string_to_date(data,timestamp_fields = self.es_conf.timestamp_fields)
            if return_val:
                logger.info(f"Updating following payload into the main record for elastic search insert:- {data}") 
                record.update(data)
                return True
            else:
                logger.debug("Data convertion failed. convert_string_to_date function returned False")
                return False
            
        
        except Exception:
            logger.error ("generate_es_payload function got failed")
            expection,expection_msg,tb = sys.exc_info()
            trace = traceback.format_exc()
            logger.error(f"Exception is {expection},happend due to {expection_msg.args} for more info check the trackback {trace}")

            
    def insert_record_into_es(self, record, index, Hex_id=True):
        """
        The function will insert a record into elastic search.

        Parameters
        ----------
        record : dict
            Source dictionary which needs to be updated in elastic search
        index : Str
            Name of the index
        Hex_id : TYPE, optional
            When the Hex_id is true then the process will take Hex_id from source and insert/update with the ID in elastic search
            If the Hex_id value is False then it will insert a record without specifying the _id 
            By default Hex_id value is True.

        Returns
        -------
        bool
            If the _id key is found in insert response then return True otherwise False

        """
        
        try:
            #field case conversion
            storage = []
            storage.append(record)

            cnv_fields_result = self.fld_case_cnv.convert_field_case(case_type = 'lower',
                                                                    source_data = storage,
                                                                    reference_field_type = self.reference_field_dict
                                                                    )            

            logger.info(f"Inserting hex_id {cnv_fields_result[0].get('Hex_id','')} record in {index} index")
            logger.info(f" ####cnv_fields_result[0] is {cnv_fields_result[0]}")
            res = self.es_conn.insert_by(uri = self.es_uri
                         ,index = index
                         ,data=cnv_fields_result[0]
                         ,header= self.es_head
                         ,Hex_id=Hex_id)
            
            #if res['_id']:
            if res.get('_id'):
                logger.info("Record got inserted successfully")
                return True
            else:
                return False
        
        except Exception:
            logger.error (f"insert_record_into_es function got failed for the Hex_id {record['Hex_id']}")
            expection,expection_msg,tb = sys.exc_info()
            trace = traceback.format_exc()
            logger.error(f"Exception is {expection},happend due to {expection_msg.args} for more info check the trackback {trace}")


    def lookup_fields(self,source, lookup_fields, cls_obj):
        """
        The function will lookup a value of a key in the configuration file and update the source.

        Parameters
        ----------
        source : Dict
            A dictionary contains key-value pair. Lookup will happen using the value of a key.
        lookup_fields : list
            Fields which may required look up. The lookup will happen only if the field name is present in source dict value.
        cls_obj : class object
            Class object of a configuration file

        Returns
        -------
        bool
            Return True if success otherwise False

        """

        try:
            logger.debug(f"lookup_fields are:- {lookup_fields}")
            for field in lookup_fields:
                logger.debug(f"Checking for the field {field}")
                tck_property = getattr(cls_obj,field,None)
                if tck_property:
                    source_key = source.get(field,None)
                    logger.debug(f"Source key is {source_key}")
                    if source_key:
                        value = tck_property.get(source_key,None)
                        if value:
                            source[field] = value
                            logger.debug(f"Value is {value}")
                            logger.info(f"Updating lookup field {field} value is {value}")
                else:
                    logger.error(f"{field} is not exists in ticket config")
                    return False
            return True
                
        except Exception:
            logger.error ("lookup_fields function got failed")
            expection,expection_msg,tb = sys.exc_info()
            trace = traceback.format_exc()
            logger.error(f"Exception is {expection},happend due to {expection_msg.args} for more info check the trackback {trace}")

    
    def update_req_field_tck(self,record,property_val):
        """
        The function update required fields for service now payload.
        Required field dictionary is maintaining in ticketToolConf file and the values will get updated dynamically using source record from elastic search

        Parameters
        ----------
        record : dict
            Source record from elastic search
        property_val : Str
            Dict/object name in the configuration file

        Returns
        -------
        Dict
            Return a payload dictionary or empty dictionary 

        """

        pay_load= {}
        origin = getattr(self.tck_conf, property_val, None)
        pay_load.update(origin)
        logger.info(f"Symphony payload before change {pay_load}")
        if pay_load:
            try:
                logger.info("updating required field for symphony payload")
                for key,value in pay_load.items():
                        if value:
                            ref_val = record.get(value,False)
                            if ref_val: 
                                pay_load[key] = ref_val
                                logger.debug(f"Update required field key is {key} and value is {ref_val}")
                logger.info(f"Symphony payload generated as follow {pay_load}")
                return pay_load
                            
                    
            except Exception:
                logger.error ("update_req_field_tck function got failed")
                expection,expection_msg,tb = sys.exc_info()
                trace = traceback.format_exc()
                logger.error(f"Exception is {expection},happend due to {expection_msg.args} for more info check the trackback {trace}")

        else:
            logger.error("{} property is not exists in ticket config".format(property_val))
            return {}
        
    def delete_record_from_index(self,hex_id,index):
        """
        Function is used to delete a particular record/document from a index

        Parameters
        ----------
        hex_id : Str
            Hex_id of the record
        index : Str
            Name of a index in elastic search

        Returns
        -------
        bool
            Return True if delete success or False

        """
        try:
            logger.info(f"Deleting hex_id {hex_id} in {index} index")
            dlt_return_val = self.es_conn.delete_id(uri = self.es_uri
                                    ,_id=hex_id,
                                    index=self.es_idx,
                                    header=self.es_head)
            
            if dlt_return_val['_id']:
                logger.info("Record deleted successfully")
                return True
            else:
                return False
        
        except Exception:
                logger.error ("delete_record_from_index function got failed")
                expection,expection_msg,tb = sys.exc_info()
                trace = traceback.format_exc()
                logger.error(f"Exception is {expection},happend due to {expection_msg.args} for more info check the trackback {trace}")
    
        
    def check_aging(self,source):
        """
        Below are the process happening in the function in the order
        1.Checking the particular record met the aging condition using Hex_id & ticket resolve date
        2.Return False if the record not met the condition
        3.If the record met the condition then updating the required field and reopening the ticket in service now
        4.Again updating the required fields with service now response and insert/updating it in elastic search

        Parameters
        ----------
        source : dict
            Record/document from a elastic search

        Returns
        -------
        bool/dict
            Return False if the record not met the condition for aging.
            Return service now response for reopen when it met the condition 

        """
        
        try:
            logger.info(f"Executing aging process for the Hex_id:- {source['Hex_id']}")
            aquery = {}
            origin = self.es_query.aging
            aquery.update(origin)
            aging_query = Template("""{}""".format(aquery))
            aging_query = eval(aging_query.render(hex_id=source["Hex_id"].replace("\\", "\\\\")))

            check_aging = self.query_elastic_search(aging_query,self.es_archive_idx)
            if check_aging:
                source.update({"Hex_TicketNumber": check_aging[0]['_source']['Hex_TicketNumber']})
                pay_load = {}
                aging_fld = self.tck_conf.archive_fields_for_aging
                pay_load.update(aging_fld)
                alert_req_fields = self.update_req_field_tck(source,property_val="alert_fields_for_aging")
                self.lookup_fields(alert_req_fields,lookup_fields=self.tck_conf.lookup_fields,cls_obj=self.tck_conf)
                pay_load.update(alert_req_fields)
                pay_load.update({"api_key": str(self.sy_key)})
                
                logger.info(f"Aging Service now payload is:- {pay_load}")

                update_yaml_str = self.payload_template
                for key, value in pay_load.items():
                    placeholder = f"{{{key}}}"
                    update_yaml_str = update_yaml_str.replace(placeholder, str(value))

                payload_dict = yaml.safe_load(update_yaml_str)
                payload_dict = payload_dict['Reopen_incident_payload']
                logger.info(f"Symphony payload :- {payload_dict}")
                
                sy_res = self.sy_conn.post_operation(self.sy_uri, 
                                                    payload=payload_dict)
                
                if sy_res['Errors'] != '':
                    logger.error(f"Hex_id :- {source['Hex_id']}")
                    logger.error(f"symphony payload for reopen is :- {payload_dict}")
                    logger.error(f"symphony response for reopen is :- {sy_res}")
                    logger.error(f"Error while performing action in symphony...")
                    logger.error("*"*80)
                    return False
                    
                if sy_res['TicketNo'] != "" or sy_res['TicketNo'] != "NA":
                    get_data = {"api_key": str(self.sy_key), "ticket_no": sy_res['TicketNo']}
                    get_yaml_str = self.payload_template
                    for key, value in get_data.items():
                        placeholder = f"{{{key}}}"
                        get_yaml_str = get_yaml_str.replace(placeholder, str(value))

                    payload_dict = yaml.safe_load(get_yaml_str)
                    payload_dict = payload_dict['Get_single_incident_payload']
                    logger.info(f"Symphony get payload :- {payload_dict}")

                    sy_res = getattr(self.sy_conn, "get_details_operation")(self.sy_uri, payload_dict, api_refresh_interval=self.api_refresh_interval)
                    logger.info("Request sent to symphony....")

                if sy_res['Errors'] != '':
                    logger.error(f"Hex_id :- {source['Hex_id']}")
                    logger.error(f"symphony payload for get_details_operation is :- {payload_dict}")
                    logger.error(f"symphony response for get_details_operation is :- {sy_res}")
                    logger.error(f"Error while performing action in symphony...")
                    logger.error("*"*80)
                    return False
                
                logger.info(f"Aging Service now response for reopen is:- {sy_res}")
                return sy_res
                
            else:
                logger.info(f"No aging for the Hex_id {source['Hex_id']}")
                return False
            
        except Exception:
                logger.error ("check_aging function got failed")
                expection,expection_msg,tb = sys.exc_info()
                trace = traceback.format_exc()
                logger.error(f"Exception is {expection},happend due to {expection_msg.args} for more info check the trackback {trace}")
    

    def tlookup(self,*keys,source):
        """
        Parameters
        ----------
        *keys : positional argument
            Keys which needs to look into the source
        source : dict
            A dictionary contains a key value pair

        Returns
        -------
        dict
            if the keys are not passed returning empty dictionary
            otherwise passing output dictionary which contains passed keys and it's value

        """
        if keys:
            output = {key: source.get(key,"") for key in keys}
            return output
        else:
            return {}
                
    
    def es_sy_operations(self,source,process_name,es_index,sy_res=False,Hex_id=True):
        """
        The function is common for all the below process
        1.create_ticket
        2.update_ticket
        3.resolve_ticket_to_itsm
        4.resolve_ticket_from_itsm
        5.update_missing_ticket_number
        
        Below are the process happening in the function in the order
        1. If the aging returns service now response then will directly start from lookup fields for elastic search
        2. Otherwise, updating required fields for service now payload
        3. Doing lookup for service now payload
        4. Choosing service now operation based on the process name and executing the service now operation
        5. Doing lookup for elastic search insert
        5. Generating required fields for elastic search insert based on service now response
        6. Insert into elastic search

        Parameters
        ----------
        source : Dict
            Record/document from a elastic search
        process_name : Str
            Name of a process. Eg{create_ticket}
        es_index : Str
            Name of the index in elastic search for insert operation
        sy_res : bool/dict, optional
            By default the value will be False. Otherwise it will have aging service now response
        Hex_id : bool, optional
            By default the value will be True. It won't consider the _id value while update if the Hex_id flag is set to false

        Returns
        -------
        bool
            Return True after the successful execution of the process.

        """
        
        try:

            sn_property_val = self.process_lookup[process_name]['sn_property_val']
            function_name = self.process_lookup[process_name]['function_name']
            es_property_val = self.process_lookup[process_name]['es_property_val']
            
            if not sy_res:

                data = self.update_req_field_tck(source,property_val=sn_property_val)
                data.update({"api_key": str(self.sy_key)})
                self.lookup_fields(data,lookup_fields=self.tck_conf.lookup_fields,cls_obj=self.tck_conf)
                
                if process_name == 'create_ticket' or process_name == 'update_ticket' or process_name == 'resolve_ticket_to_itsm':
                    if process_name == 'create_ticket':
                        yaml_str = self.tck_payload.create_incident_payload
                    elif process_name == 'update_ticket':
                        yaml_str = self.tck_payload.update_priority_payload
                    elif process_name == 'resolve_ticket_to_itsm':
                        yaml_str = self.tck_payload.resolve_incident_payload                        

                    template_str = json.dumps(yaml_str)
                    for key, value in data.items():
                        placeholder = f"~{key}~"
                        value = value.replace("\r\n", "").replace("\n","").replace('"',"'").replace('\\"', '"').replace('\\','\\\\')
                        template_str = template_str.replace(placeholder, str(value))

                    payload_dict = json.loads(template_str)
                    logger.info(f"Symphony payload :- {payload_dict}")

                    sy_res = getattr(self.sy_conn, function_name)(self.sy_uri, payload_dict, api_refresh_interval=self.api_refresh_interval)
                    logger.info("Request sent to symphony....")

                # elif process_name == 'resolve_ticket_to_itsm':
                #     yaml_str = self.payload_template
                #     for key, value in data.items():
                #         placeholder = f"{{{key}}}"
                #         yaml_str = yaml_str.replace(placeholder, str(value))

                #     payload_dict = yaml.safe_load(yaml_str)
                    
                #     if process_name == 'resolve_ticket_to_itsm':
                #         payload_dict = payload_dict['Resolve_incident_payload']
                #     logger.info(f"Symphony payload :- {payload_dict}")

                #     sy_res = getattr(self.sy_conn, function_name)(self.sy_uri, payload_dict, api_refresh_interval=self.api_refresh_interval)
                #     logger.info("Request sent to symphony....")
                elif process_name == 'resolve_ticket_from_itsm' or process_name == 'update_missing_ticket_number' or process_name == 'change_alert_status':
                    get_yaml_str = self.payload_template
                    for key, value in data.items():
                        placeholder = f"{{{key}}}"
                        get_yaml_str = get_yaml_str.replace(placeholder, str(value))

                    payload_dict = yaml.safe_load(get_yaml_str)
                    payload_dict = payload_dict['Get_single_incident_payload']
                    logger.info(f"Symphony get payload :- {payload_dict}")

                    sy_res = getattr(self.sy_conn, function_name)(self.sy_uri, payload_dict, api_refresh_interval=self.api_refresh_interval)
                    logger.info("Request sent to symphony....")
                else:
                    sy_res = getattr(self.sy_conn, function_name)(self.sy_uri, sys_id=data['sys_id'],data=data,api_refresh_interval=self.api_refresh_interval)
                    logger.info("Request sent to symphony....")
            
            logger.info(f"symphony response for {process_name} is :- {sy_res}")

            if sy_res['Errors'] != '':
               logger.error(f"Hex_id :- {source['Hex_id']}")
               logger.error(f"symphony payload for {process_name} is :- {payload_dict}")
               logger.error(f"symphony response for {process_name} is :- {sy_res}")
               logger.error(f"Error while performing action in symphony...")
               logger.error("*"*80)
               return False
            
            if "TicketNo" in sy_res and sy_res['TicketNo'] != "NA" and (process_name == 'create_ticket' or process_name == 'update_ticket' or process_name == 'resolve_ticket_to_itsm'):
                get_data = {"api_key": str(self.sy_key), "ticket_no": sy_res['TicketNo']}
                get_yaml_str = self.payload_template
                for key, value in get_data.items():
                    placeholder = f"{{{key}}}"
                    get_yaml_str = get_yaml_str.replace(placeholder, str(value))

                payload_dict = yaml.safe_load(get_yaml_str)
                payload_dict = payload_dict['Get_single_incident_payload']
                logger.info(f"Symphony get payload :- {payload_dict}")

                sy_res = getattr(self.sy_conn, "get_details_operation")(self.sy_uri, payload_dict, api_refresh_interval=self.api_refresh_interval)
                logger.info("Request sent to symphony....")

            if sy_res['Errors'] != '':
               logger.error(f"Hex_id :- {source['Hex_id']}")
               logger.error(f"symphony payload for get_details_operation is :- {payload_dict}")
               logger.error(f"symphony response for get_details_operation is :- {sy_res}")
               logger.error(f"Error while performing action in symphony...")
               logger.error("*"*80)
               return False
            
            logger.info(f"symphony response for get_details_operation is :- {sy_res}")

            if sy_res:
                self.lookup_fields(sy_res,lookup_fields=self.es_conf.lookup_fields,cls_obj=self.tck_conf)

                if sy_res['Status'] != "Resolved" and  process_name == 'resolve_ticket_from_itsm':
                    logger.info(f"Ticket not resolved for the Hex_id:- {source['Hex_id']}")
                else:
                    es_req_fld = {}
                    get_es_fld_attribute = getattr(self.es_conf, es_property_val)
                    es_req_fld.update(get_es_fld_attribute)
                    self.generate_es_payload(sy_res=sy_res
                                          ,record=source
                                          ,req_fields = es_req_fld)

                    if process_name == "create_ticket" and source['Hex_AlertText'] != "":
                        logger.info(f"Adding Hex_TicketAlertText to source")
                        source.update({"Hex_TicketAlertText": source['Hex_AlertText']})
                    if process_name == "update_ticket" and source['Hex_AlertText'] != source['Hex_TicketAlertText']:
                        logger.info(f"Updating alert text from Hex_TicketAlertText:{source['Hex_TicketAlertText']} to Hex_AlertText:{source['Hex_AlertText']}")
                        source.update({"Hex_TicketAlertText": source['Hex_AlertText']})  

                    # if process_name == "change_alert_status":
                    #     assng_grp_link = sy_res['assignment_group']['link']
                    #     assng_grp_res = self.sy_conn.get_ticket_details(assng_grp_link)
                    #     assng_grp_name = assng_grp_res['name']
                    #     logger.info(f"Updating assingment group {assng_grp_name} recived from service now.")
                    #     source.update({"hex_ticketassingmentgroup": assng_grp_name})                                            
                    
                    insert_res_es = self.insert_record_into_es(source,es_index,Hex_id)
                    if not insert_res_es:
                            logger.error(f"{process_name} process:- Insert got failed")
                    else:
                        logger.info("es_sy_operations function completed successfully")
                        logger.info(f"source is {source}")
                        tlogs = controller(self.tlogs_path,self.split_value(source["Hex_id"]))
                        data = self.tlookup("Hex_Hostname","Hex_id","Hex_DeviceType",
                                            "Hex_AlertText","Hex_Status","hex_ticketcreationdate",
                                            "Hex_LastUpdated",source = source)
                        tlogs(*data.values(),
                            f"Operation: {process_name}, Incident number : {source.get('Hex_TicketNumber','')}, Sys id : {source.get('sys_id','')}"
                            )
                       
                        return True
            else:
                logger.error(f"{process_name} process:- Service now response is {sy_res}")
            

        except Exception:
                logger.error (f"es_sy_operations in {process_name} process got failed")
                expection,expection_msg,tb = sys.exc_info()
                trace = traceback.format_exc()
                logger.error(f"Exception is {expection},happend due to {expection_msg.args} for more info check the trackback {trace}")

       
        
    def create_new_ticket(self):
        """
        1. Execute the new alert query in elastic search and run all the records in a loop
        2. Executing aging otherwise go to next record
        3. Aging will return either a dict(service now response) or False to the es_sy_operations function

        Returns
        -------
        None.

        """

        try:
            logger.info("Executing ticket creation process.....")
            query = self.es_query.new_alert
            get_new_alert = self.query_elastic_search(query,self.es_idx) 
        
            if get_new_alert:
                for record in get_new_alert:
                    logger.info(f"record is:- {record}")
                    logger.info(f"Create ticket process starting for the Hex_id:- {record['_source']['Hex_id']}")

                    if str(record['_source']['alert_type']) not in self.es_conf.Excluded_types_create_ticket:
                        if self.es_conf.settings['aging']:
                            sy_res = self.check_aging(record['_source'])
                        else:
                            sy_res =  False
                            logger.info("Skipping the Aging process since the aging Flag is set to False in elastic config.")
                        
                        logger.info(f"check_aging function return value is :- {sy_res}")
                    self.es_sy_operations(source = record['_source'],
                                            process_name="create_ticket"
                                            ,es_index=self.es_idx
                                            ,sy_res=sy_res)
                    logger.info(f"Create ticket process completed for the Hex_id:- {record['_source']['Hex_id']}")

                logger.info("Ticket creation process completed.....")
                    
            else:
                logger.info("Ticket creation process:- No records fetched for the processing")
        
        except Exception:
                logger.error ("create_new_ticket function got failed")
                expection,expection_msg,tb = sys.exc_info()
                trace = traceback.format_exc()
                logger.error(f"Exception is {expection},happend due to {expection_msg.args} for more info check the trackback {trace}")

        
    def update_priority(self):
        """
        1. Execute the priority change alert query in elastic search and run all the records in a loop
        2. Passing the records one by one to the es_sy_operations with the required parameter

        Returns
        -------
        None.

        """

        try:
            logger.info("Executing update priority process.....")
            query = self.es_query.priority_change_alert
            get_prty_chng_rec = self.query_elastic_search(query,self.es_idx)
       
            if get_prty_chng_rec:
                for record in get_prty_chng_rec:
                    logger.info(f"Updated ticket priority starting for the Hex_id:- {record['_source']['Hex_id']}")
                    self.es_sy_operations(source = record['_source'],
                                             process_name="update_ticket"
                                             ,es_index=self.es_idx)
                    logger.info(f"Updated ticket priority completed for the Hex_id:- {record['_source']['Hex_id']}")
                logger.info("Update priority process completed.....")
            else:
                logger.info("Update priority process:- No records fetched for the processing")
        except Exception:
                logger.error ("update_priority function got failed")
                expection,expection_msg,tb = sys.exc_info()
                trace = traceback.format_exc()
                logger.error(f"Exception is {expection},happend due to {expection_msg.args} for more info check the trackback {trace}")


    def update_missing_ticket_number(self):
        """
        1. Execute the update missing ticket number query in elastic search and run all the records in a loop
        2. Passing the records one by one to the es_sy_operations with the required parameter
        3. Get the ticket number from service now using sys_id and update ticketnumber in elastic search

        Returns
        -------
        None.

        """

        try:
            logger.info("Executing update missing ticket number process.....")
            query = self.es_query.update_ticket_number_alert
            missing_tck = self.query_elastic_search(query,self.es_idx)
       
            if missing_tck:
                for record in missing_tck:
                    logger.info(f"Updating missing ticket number for the Hex_id:- {record['_source']['Hex_id']}")
                    self.es_sy_operations(source = record['_source'],
                                             process_name="update_missing_ticket_number"
                                             ,es_index=self.es_idx)
                    logger.info(f"Update missing ticket number process got completed for the Hex_id:- {record['_source']['Hex_id']}")
                logger.info("Update missing ticket number process completed.....")
            else:
                logger.info("Update missing ticket number process:- No records fetched for the processing")
        except Exception:
                logger.error ("update_missing_ticket_number function got failed")
                expection,expection_msg,tb = sys.exc_info()
                trace = traceback.format_exc()
                logger.error(f"Exception is {expection},happend due to {expection_msg.args} for more info check the trackback {trace}")

        
    def resolve_ticket_to_itsm(self):
        """
        1. Execute the resolve ticket to itsm query in elastic search and run all the records in a loop
        2. Passing the records one by one to the es_sy_operations with the required parameter
        3. Deleting the record in alert-index if the record inserted successfully in alert archive index in es_sy_operations function

        Returns
        -------
        None.

        """

        try:
            logger.info("Executing resolve ticket to itsm process.....")
            query = self.es_query.resolution_alert_to_itsm
            to_itsm_record = self.query_elastic_search(query,self.es_idx) 
        
            if to_itsm_record:
                for record in to_itsm_record:
                    logger.info(f"Resolve ticket to itsm starting for the Hex_id:- {record['_source']['Hex_id']}")
                    
                    """
                    if str(record['_source']['alert_type']) not in self.es_conf.excluded_types_resolve_to_itsm:
                        ticket_creation_time = record['_source']['Hex_TicketCreationDate']
                        difference_in_time = self.get_time_difference(ticket_creation_time)
                        logger.info(f"Received time difference value: {difference_in_time}")
                        if not difference_in_time:
                            logger.info(f"Skipping Resolve ticket to ITSM for Hex_id:- {record['_source']['Hex_id']} because time difference is less than 4 hours")
                            continue
                    """
                    
                    logger.info(f"Service now additional fields update plugin value is:- {self.sn_additional_fields_update}")

                    # get_assigned_data = self.sy_conn.get_ticket(self.sy_uri,
                    #                                             sys_id = record['_source'].get('sys_id'),
                    #                                             api_refresh_interval=self.api_refresh_interval)
                    if self.sn_additional_fields_update.lower() == 'true':
                        fields_to_update = self.tck_conf.additional_fields_to_update
                        fields_to_update.update({"api_key": str(self.sy_key), "ticket_no": str(record['_source']['Hex_TicketNumber'])})

                        yaml_str = self.payload_template
                        for key, value in fields_to_update.items():
                            placeholder = f"{{{key}}}"
                            yaml_str = yaml_str.replace(placeholder, str(value))

                        payload_dict = yaml.safe_load(yaml_str)
                        payload_dict = payload_dict['Assign_user_payload']
                        logger.info(f"Symphony payload :- {payload_dict}")

                        sy_res = getattr(self.sy_conn, "post_operation")(self.sy_uri, payload_dict, api_refresh_interval=self.api_refresh_interval)
                        logger.info("Request sent to symphony....")
                        logger.info(f"symphony response for assign user is :- {sy_res}")

                        if sy_res['Errors'] != '':
                            logger.error(f"symphony payload for assign user is :- {payload_dict}")
                            logger.error(f"symphony response for assign user is :- {sy_res}")
                            logger.error(f"Error while performing action in symphony...")
                            logger.error("*"*80)
                            #return False
                            continue

                        # method_args={'uri':self.sy_uri,'sys_id':record['_source'].get('sys_id'),
                        #                 'data':fields_to_update,
                        #                 'api_refresh_interval':self.api_refresh_interval}
                        # self.plugins.update_additional_fields(process = 'servicenow',
                        #                                         method=self.sy_conn.update_ticket,
                        #                                         method_args=method_args)
                        
                        sleep_seconds = 5
                        logger.info(f"Process is in sleep state for {sleep_seconds} seconds")
                        time.sleep(sleep_seconds)
                    # assigned_data = self.sy_conn.get_ticket(self.sy_uri,
                    #                                         sys_id = record['_source'].get('sys_id'),
                    #                                         api_refresh_interval=self.api_refresh_interval)
                    # if assigned_data.get('assigned_to'):
                    #     assigned_to =  assigned_data.get('assigned_to').get('value')
                    #     assigned_user = self.sy_conn.get_ticket(self.sn_user_uri,
                    #                                             sys_id = assigned_to,
                    #                                             api_refresh_interval=self.api_refresh_interval).get('u_qualified_name')
                    #     logger.info(f"assigned_user is {assigned_user}")
                    #     record['_source']['Hex_Assigned_To'] = assigned_to
                    #     record['_source']['Hex_Work_Notes'] = f'Resolving the incident on behalf of {assigned_user} by {self.tck_conf.ticket_info["caller_id"]} '
                    
                    if "TicketNo" in sy_res and sy_res['TicketNo'] != "NA":
                        get_yaml_str = self.payload_template
                        for key, value in fields_to_update.items():
                            placeholder = f"{{{key}}}"
                            get_yaml_str = get_yaml_str.replace(placeholder, str(value))

                        payload_dict = yaml.safe_load(get_yaml_str)
                        payload_dict = payload_dict['Get_single_incident_payload']
                        logger.info(f"Symphony get payload :- {payload_dict}")

                        sy_res = getattr(self.sy_conn, "get_details_operation")(self.sy_uri, payload_dict, api_refresh_interval=self.api_refresh_interval)
                        logger.info("Request sent to symphony....")
                        logger.info(f"assigned_user is {sy_res}")

                    if sy_res['Errors'] != '':
                        logger.error(f"symphony payload for get_details_operation is :- {payload_dict}")
                        logger.error(f"symphony response for get_details_operation is :- {sy_res}")
                        logger.error(f"Error while performing action in symphony...")
                        logger.error("*"*80)
                        #return False
                        continue

                    if "Assigned_Engineer_Name" in sy_res and (sy_res['Assigned_Engineer_Name'] != "" or sy_res['Assigned_Engineer_Name'] != "NA"):
                        record['_source']['Hex_Assigned_To'] = sy_res['Assigned_Engineer_Name']
                        record['_source']['Hex_Work_Notes'] = f'Resolving the incident on behalf of {sy_res["Assigned_Engineer_Name"]} by {self.tck_conf.ticket_info["caller_id"]} '
                    
                    insert_return = self.es_sy_operations(source = record['_source'],
                                             process_name="resolve_ticket_to_itsm"
                                             ,es_index=self.es_archive_idx
                                             ,Hex_id=False)
                    if not insert_return:
                        logger.error("Update resolution to itsm process:- es_sy_operations got failed")
                    else:
                        delete_return = self.delete_record_from_index(record['_source']["Hex_id"],self.es_idx)
                        if not delete_return:
                            logger.error(f"Update resolution to itsm process:- delete from {self.es_idx} index got failed")
                    logger.info(f"Resolve ticket to itsm completed for the Hex_id:- {record['_source']['Hex_id']}")
                    
                logger.info("Resolve ticket to itsm process completed.....")
            else:
                logger.info("Update resolution to itsm process:- No records fetched for the processing")
                
        except Exception:
                logger.error ("resolve_ticket_to_itsm function got failed")
                expection,expection_msg,tb = sys.exc_info()
                trace = traceback.format_exc()
                logger.error(f"Exception is {expection},happend due to {expection_msg.args} for more info check the trackback {trace}")
      
        
    def resolve_ticket_from_itsm(self):
        """
        1. Execute the resolve ticket from itsm query in elastic search and run all the records in a loop
        2. Passing the records one by one to the es_sy_operations with the required parameter
        3. Deleting the record in alert-index if the record inserted successfully in alert archive index in es_sy_operations function

        Returns
        -------
        None.

        """
        try:
            logger.info("Executing resolve ticket from itsm process")
            query = self.es_query.resolution_alert_from_itsm
            from_itsm_record = self.query_elastic_search(query,self.es_idx)
        
            if from_itsm_record:
                for record in from_itsm_record:
                    logger.info(f"Resolve ticket from itsm starting for the Hex_id:- {record['_source']['Hex_id']}")
                    insert_return = self.es_sy_operations(source = record['_source'],
                                             process_name="resolve_ticket_from_itsm"
                                             ,es_index=self.es_archive_idx
                                             ,Hex_id=False)
                    if insert_return == None:
                        logger.info("Update resolution received None and process has stopped. Please check the above logs")
                    elif not insert_return:
                        logger.error("Update resolution from itsm process:- es_sy_operations got failed")
                    else:
                        delete_return = self.delete_record_from_index(record['_source']["Hex_id"],self.es_idx)
                        if not delete_return:
                            logger.error(f"Update resolution from itsm process:- delete from {self.es_idx} got failed")
                    logger.info(f"Resolve ticket from itsm completed for the Hex_id:- {record['_source']['Hex_id']}")
                logger.info("Resolve ticket from itsm process completed")
            else:
                logger.info("Update resolution from itsm process:- No records fetched for the processing")
                
        except Exception:
                logger.error ("resolve_ticket_from_itsm function got failed")
                expection,expection_msg,tb = sys.exc_info()
                trace = traceback.format_exc()
                logger.error(f"Exception is {expection},happend due to {expection_msg.args} for more info check the trackback {trace}")


    def get_time_difference(self, ticket_creation_time):
        """
        1. This methods calculates the time difference between current time and the provided time.
        Returns:
            bool
        """
        try:
            ticket_creation_time = datetime.strptime(ticket_creation_time, "%Y-%m-%dT%H:%M:%S.%fZ").replace(tzinfo=timezone.utc)
            current_time = datetime.now(timezone.utc)
            time_difference = current_time - ticket_creation_time
            logger.info(f"Ticket creation time : {ticket_creation_time}")
            logger.info(f"Current time : {current_time}")
            logger.info(f"Time difference : {time_difference}")
            if time_difference > timedelta(hours=4):
                return True
            return False
        except Exception:
            logger.error("get_time_difference function got failed")
            expection, expection_msg, tb = sys.exc_info()
            trace = traceback.format_exc()
            logger.error(
                f"Exception is {expection},happend due to {expection_msg.args} for more info check the trackback {trace}")
 

    def handle_resolved_alerts(self):
        """
        If the ticketType is resolution and ticketnumber is blank then
        we moving the record to archive index and deleting the record in alert index

        Returns
        -------
        None.

        """
        try:
            logger.info("Handling resolved alerts")
            query = self.es_query.resolved_alert
            resolved_alerts = self.query_elastic_search(query,self.es_idx)
            if resolved_alerts:
                for record in resolved_alerts:
                    logger.info(f"Handle resolved alert starting for the Hex_id:- {record['_source']['Hex_id']}")
                    insert_res_es = self.insert_record_into_es(record['_source']
                                                               ,self.es_archive_idx
                                                               ,Hex_id= False)
                    if insert_res_es:
                        delete_return = self.delete_record_from_index(record['_source']["Hex_id"],self.es_idx)
                        if not delete_return:
                            logger.error(f"Handling resolved alerts:- delete from {self.es_idx} got failed")
                        else:
                            tlogs = controller(self.tlogs_path,self.split_value(record['_source']["Hex_id"]))
                            data = self.tlookup("Hex_Hostname","Hex_id","Hex_DeviceType",
                                            "Hex_AlertText","Hex_Status","Hex_TicketCreationDate",
                                            "Hex_LastUpdated",source = record['_source'])
                            tlogs(*data.values(),
                              f"Operation: Handling_resolved_alert, Incident number : {record['_source'].get('Hex_TicketNumber','')}, Sys id : {record['_source'].get('sys_id','')}"
                              )
                        logger.info(f"Handle resolved alert completed for the Hex_id:- {record['_source']['Hex_id']}")
                   
                    else:
                        logger.error(f"Handling resolved alerts:- insert into {self.es_archive_idx} index got failed")
            else:
                logger.info("Handling resolved alerts:- No records fetched for the processing")
        except Exception:
                logger.error ("handle_resolved_alerts function got failed")
                expection,expection_msg,tb = sys.exc_info()
                trace = traceback.format_exc()
                logger.error(f"Exception is {expection},happend due to {expection_msg.args} for more info check the trackback {trace}")


    def change_alerts_status(self):
        """
        1. Execute the change status alerts query in elastic search and run all the records in a loop
        2. Passing the records one by one to the es_sy_operations with the required parameter

        Returns
        -------
        None.

        """
        try:
            logger.info("Executing change alerts status process.....")
            query = self.es_query.change_status_alert
            to_itsm_record = self.query_elastic_search(query, self.es_idx)

            if to_itsm_record:
                for record in to_itsm_record:
                    logger.info(
                        f"Check Status change starting for the Hex_id:- {record['_source']['Hex_id']}")

                    self.es_sy_operations(source=record['_source'],
                                        process_name="change_alert_status", es_index=self.es_idx)
                    logger.info(
                        f"Change status process completed for the Hex_id:- {record['_source']['Hex_id']}")

                logger.info("Change status process completed.....")

            else:
                logger.info(
                    "Change status process:- No records fetched for the processing")

        except Exception:
            logger.error("change_alerts_status function got failed")
            expection, expection_msg, tb = sys.exc_info()
            trace = traceback.format_exc()
            logger.error(
                f"Exception is {expection},happend due to {expection_msg.args} for more info check the trackback {trace}")


if __name__ == "__main__":
    logger = initialize_logger()

    while True: 
        CONFIGFILE = "settings.ini"
        #Config Manager
        #src_dir = os.path.dirname(os.path.realpath(__file__))
        settings_path = os.path.join(".",CONFIGFILE)
        config = configparser.ConfigParser()
    
        logger.info(f"{datetime.now()} - Reading {CONFIGFILE} now.")
        config.read(settings_path)
    
        #Path config
        cpath = config.get('configpath','config_path')
        tpath = config.get('configpath','transaction_log_path')
    
        #MISC
        SVERSION = config.get('misc','SVERSION')
        SDATE = config.get('misc','SDATE')
        CHECKTIME = int(config.get('misc','CHECKTIME'))
    
        #API Interval config
        api_refresh_interval = config.get('misc','APIINTERVAL')

        #PLUGINS
        sn_additional_fields_update = config.get('plugins','sn_additional_fields_update')
        logger.info(f"Using pyconnect version {SVERSION} and deployed on {SDATE}")
    
        objPH = ProcessHandler(config_path= cpath, tlog_path= tpath, api_interval = api_refresh_interval,sn_additional_fields_update=sn_additional_fields_update) 

        #objPH.update_missing_ticket_number()
        objPH.handle_resolved_alerts()    
        objPH.create_new_ticket()
        objPH.update_priority()
        #objPH.change_alerts_status()
        objPH.resolve_ticket_to_itsm()
        #objPH.resolve_ticket_from_itsm()
        logger.info(f"Process is in sleep state for {CHECKTIME} seconds")
        time.sleep(CHECKTIME)
