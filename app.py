#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Sep 28 11:43:55 2021

@author: Hariharan Ashokan, Archana
"""

# Standard Library
import os
import time
import traceback, sys

# User-Defined Library
from EmailSender import EmailBox
from dlogger import initialize_logger
from Operations import ConfigStore
from Model import ElasticSearch


class EmailNotifier:
    def __init__(self,
                 config_fnames: str):
        self.email_config, self.query_config = config_fnames
        self.config_path = f"{os.path.dirname(os.path.realpath(__file__))}//StaticConfig"
        self.es_query, self.email_conf = ConfigStore(self.config_path,
                                                     elasticqueryfile=self.query_config,
                                                     emailconfigfile=self.email_config)
        #elf.es_conn = ElasticSearch()
        self.es_conn = ElasticSearch(True,username=self.email_conf.elasticsearch['username'],
                                      password=self.email_conf.elasticsearch['password'])
        self.es_uri = self.email_conf.elasticsearch["host"] + ":" + str(self.email_conf.elasticsearch["port"])
        self.es_idx = self.email_conf.elasticsearch["alerts_index"]
        self.es_archive_idx = self.email_conf.elasticsearch["alerts_archive_index"]
        self.es_head = self.email_conf.elasticsearch["header"]
        self.host = self.email_conf.emailsender["host"]
        self.port = self.email_conf.emailsender["port"]
        self.sender = self.email_conf.emailsender["sender"]
        self.Emailobj = EmailBox(host=self.host, 
                                port=self.port, 
                                sender=self.sender)

    def query_elastic_search(self, 
                             query: dict, 
                             index: str):
        """
        The function execute the supplied query in elastic search and return the result.
        If the execution failed during fetching the records then return empty list.

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
            logger.info(f"Query is :- {query}")
            res = self.es_conn.get_by(uri=self.es_uri
                                      , index=index
                                      , query=query
                                      , header=self.es_head)
            logger.info(f"Elastic search query executed successfully and fetched {len(res)} records")
            return res if res else []

        except Exception:
            logger.error("Elastic search query execution got failed")
            expection, expection_msg, tb = sys.exc_info()
            trace = traceback.format_exc()
            logger.error(f"Exception is {expection},happend due to {expection_msg.args} for more info check the trackback {trace}")

    def insert_record_into_es(self, 
                              record: dict, 
                              index: str, 
                              Hex_id=True):
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
            logger.info(f"Inserting hex_id {record.get('hex_id', '')} record in {index} index")
            res = self.es_conn.insert_by(uri=self.es_uri
                                         , index=index
                                         , data=record
                                         , header=self.es_head
                                         , Hex_id=Hex_id)

            if res['_id']:
                logger.info("Record got inserted successfully")
                return True
            else:
                return False

        except Exception:
            logger.error("insert_record_into_es function got failed")
            expection, expection_msg, tb = sys.exc_info()
            trace = traceback.format_exc()
            logger.error(f"Exception is {expection},happend due to {expection_msg.args} for more info check the trackback {trace}")

    def delete_record_from_index(self, 
                                 hex_id: str, 
                                 index: str):
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
            dlt_return_val = self.es_conn.delete_id(uri=self.es_uri
                                                    , _id=hex_id,
                                                    index=self.es_idx,
                                                    header=self.es_head)

            if dlt_return_val['_id']:
                logger.info("Record deleted successfully")
                return True
            else:
                return False

        except Exception:
            logger.error("delete_record_from_index function got failed")
            expection, expection_msg, tb = sys.exc_info()
            trace = traceback.format_exc()
            logger.error(f"Exception is {expection},happend due to {expection_msg.args} for more info check the trackback {trace}")

    def trigger_email(self,
                      sender: str,
                      receiver: str,
                      subject: str,
                      body: str
                      ):
        try:
            #!!!!!!!!!subject & body patter need to confirm with Harin, priya, keerthana
            logger.info(f"Sender value is {sender}")
            logger.info(f"Receiver value is {receiver}")
            logger.info(f"Subject value is {subject}")
            logger.info(f"Body value is {body}")

            responce_email=self.Emailobj.sendEmail(receiver=receiver,
                                                  subject=subject, 
                                                  body=body)
            return True if responce_email else False
        except Exception:
            logger.error("trigger_email function got failed")
            expection, expection_msg, tb = sys.exc_info()
            trace = traceback.format_exc()
            logger.error(f"Exception is {expection},happend due to {expection_msg.args} for more info check the trackback {trace}")

    def handle_alerts(self,
                      process_type: str,
                      query_name: str):
        try:
            logger.info(f"Process Type:- {process_type.upper()}, Checking alerts....")
            query = getattr(self.es_query, query_name)
            get_alerts = self.query_elastic_search(query,
                                                   self.es_idx
                                                   )

            if get_alerts:
                for record in get_alerts:
                    data = record['_source']
                    logger.info(
                        f"Process Type:- {process_type.upper()}, Sending email for the Hex_id is {data['hex_id']}")

                    sender = self.sender
                    receiver = ",".join(data['hex_email'])
                   #receiver = data['hex_email']
                    subject = 'New Kibana ' +data['hex_tickettype'].capitalize() + ' Alert: ' + data['hex_sourcehost'] + ': ' + data[
                        'hex_alerttext']
                    body = f"HOST Name: {data['hex_sourcehost']} \n Description: {data['hex_description']} \n KIBANA URL: {data['hex_kibana_url']}"

                    email_response = self.trigger_email(sender=sender,
                                                        receiver=receiver,
                                                        subject=subject,
                                                        body=body
                                                        ) 
                    #break
                    #email_response=True
                    if email_response:
                        logger.info(
                            f"Process Type:- {process_type.upper()}, Email triggered successfully for the Hex_id {data['hex_id']}")
                        if process_type == 'problem':
                            data['hex_email_sent'] = 'problem email sent'
                            #update only the required field
                            insert_res_es = self.insert_record_into_es(record=data,
                                                                       index=self.es_idx
                                                                       )
                            if not insert_res_es:
                                logger.error(
                                    f"Process Type:- {process_type.upper()}, Failed to update elastic search for the Hex id {data['hex_id']}")
                            else:
                                logger.info(
                                    f"Process Type:- {process_type.upper()}, Elastic search updated success for the Hex id {data['hex_id']}")
                        elif process_type == 'resolution':
                            data['hex_email_sent'] = 'resolution email sent'
                            insert_return = self.insert_record_into_es(data,
                                                                       self.es_archive_idx,
                                                                       Hex_id=False
                                                                       )
                            logger.info(f"insert_return is { insert_return }") 

                            if insert_return:
                                logger.info(
                                    f"Process Type:- {process_type.upper()},Hex_id {data['hex_id']} record moved to {self.es_archive_idx}")
                                delete_return = self.delete_record_from_index(data["hex_id"],
                                                                              self.es_idx
                                                                              )
                                if delete_return:
                                    logger.info(
                                        f"Process Type:- {process_type.upper()}, Deleted hex_id {data['hex_id']} from {self.es_idx} index successfully")
                                else:
                                    logger.error(
                                        f"Process Type:- {process_type.upper()}, Failed to delete hex_id {data['hex_id']} from {self.es_idx} index")
                            else:
                                logger.error(
                                    f"Process Type:- {process_type.upper()},Hex_id {data['hex_id']} record failed to insert into {self.es_archive_idx}")
                    else:
                        logger.error(
                            f"Process Type:- {process_type.upper()}, Email triggered got failed for the Hex_id {data['hex_id']}")

            else:
                logger.info("Problem Alert:- No records fetched for the processing")

        except Exception:
            logger.error(f"handle_problem_alert function got failed for the process type {process_type.upper()}")
            expection, expection_msg, tb = sys.exc_info()
            trace = traceback.format_exc()
            logger.error(
                f"Exception is {expection},happend due to {expection_msg.args} for more info check the trackback {trace}")


if __name__ == '__main__':
    logger = initialize_logger()
    ENObj = EmailNotifier(config_fnames=['emailer_config.yml', 'QueryConfig.yml'])
    while True:    
        ENObj.handle_alerts(process_type='problem',
                        query_name='problemalert')
        ENObj.handle_alerts(process_type='resolution',
                        query_name='resolutionalert')
    
    
        time.sleep(300)
