#!/usr/bin/env python
# -*- coding: utf-8 -*-
##import common library
import os
import datetime
import logging
import logging.config
import requests
from requests.exceptions import ReadTimeout

#########################
##Debug Log Function
#########################
def InitialDebugLog(level=logging.INFO):
    ''' InitialDebugLog : Declare log file path and initial log algorithmic
            Input argu :
                level - logger level (logging.DEBUG / logging.INFO / logging.WARNING / logging.ERROR / logging.CRITICAL)
            Return code:
                logger - return logger instance
    '''

    logger_name = './log/' + datetime.datetime.now().strftime('%Y%m%d-%H%M%S').format() + '_Api_SQATest.log'

    ##If the directory does not exist in the target path
    if not os.path.exists("./log"):
        os.mkdir("./log")

    ##Loggers definition
    logging.basicConfig(filename=logger_name, filemode='w', encoding='utf-8', format='%(asctime)s-[%(levelname)s]||%(message)s', level=level)

    ##Return logger instance
    return logging.getLogger(logger_name)

##Define api logger
apilogger = InitialDebugLog(level=logging.INFO)

##For Send HTTP packets to API interface
class APIController():
    def SendAPIPacket(self, http_method, url, body_data_format = False, body=None, files=None, headers=None, session=None, cookies=None, params=None, auth=None, verify=True):
        ''' SendAPIPacket : Send API Packet
                Input argu :
                    http_method - get, patch, post
                    url - url for http request
                    body_data_format - False (Use "data" format to send payload, the default data format of data is form) / 
                                       Ture (Use "json" format to send payload, if the api url only accept json data)
                    body - body for http request
                    headers - headers for http request
                    session - session for http request
                    cookies - cookies for http request
                    params - url parameters for http request (update session usage)
                    auth - api token
                    verify - SSL verify
                Return code :
                    http response - session / status / text
                    0 - fail
        '''
        response = ""

        try:
            ##HTTP Get
            if http_method == "get":
                response = requests.get(url=url, params=params, json=body, headers=headers, cookies=cookies, auth=auth, verify=verify)

            #HTTP PATCH
            elif http_method == "patch":
                ##Check data(body) is rawdata or json dumps
                if body_data_format:
                    apilogger.info("PATCH data is use \"json\" key")
                    response = requests.patch(url=url, json=body, headers=headers, cookies=cookies, auth=auth, verify=verify)
                ##Send Post request directly
                else:
                    apilogger.info("PATCH data is use \"data\" key")
                    response = requests.patch(url=url, data=body, headers=headers, cookies=cookies, auth=auth, verify=verify)

            #HTTP POST
            elif http_method == "post":
                ##Check data(body) is rawdata or json dumps
                if body_data_format:
                    apilogger.info("POST data is use \"json\" key")
                    response = requests.post(url=url, json=body, headers=headers, cookies=cookies, auth=auth, verify=verify)
                ##Send Post request directly
                else:
                    apilogger.info("POST data is use \"data\" key")
                    response = requests.post(url=url, data=body, headers=headers, cookies=cookies, auth=auth, verify=verify)

            else:
                apilogger.error("!!!!Please check your http_method!!!!")
                return 1

            if response.status_code != 200:
                apilogger.info("Send to api url: %s" % (url))
                apilogger.info("Send headers to api: %s" % (headers))
                # apilogger.info("Send cookies to api: %s" % (cookies))
                apilogger.info("Send body to api: %s" % (body))
                apilogger.info("Send auth to api: {}".format(auth))
                apilogger.info("Send verify to api: %s" % (verify))
                apilogger.info("Send params to api: {}".format(params))
                apilogger.info("%s -> Response headers: %s" % (http_method, response.headers))
                apilogger.info("%s -> Response status code : %d" % (http_method, response.status_code))
                apilogger.info("%s -> Response text: %s" % (http_method, response.text))
            return response

        ##Handle ReadTimeOut from http request
        except ReadTimeout:
            apilogger.error("!!!!Timeout occurred!!!!")
            return 1

        except ConnectionError:
            apilogger.error("!!!!Error Connecting!!!!")
            return 1

        except requests.exceptions.RequestException:
            apilogger.error('!!!!HTTP Request failed!!!!')
            return 1

def SendHttpRequest(arg):
    ''' SendHttpRequest : Send Http Request
            Input argu :
                http_method - Send http request, you can use get / patch / post
                url - url for http request
                auth - api token
                verify - SSL verify
                params - url parameters for http request (update session usage)
                body - body for http request
                body_data_format - False (Use "data" format to send payload, the default data format of data is form) / 
                                   Ture (Use "json" format to send payload, if the api url only accept json data)
                headers - headers for http request (default content-type is application/json)
            Return code :
                1 - success
                0 - fail
                -1 - error
    '''
    http_method = arg["http_method"]
    url = arg["url"]

    if "auth" in arg:
        auth = arg["auth"]
    else:
        auth = None

    if "verify" in arg:
        verify = arg["verify"]
    else:
        verify = True

    if "params" in arg:
        params = arg["params"]
    else:
        params = None

    if "body" in arg:
        body = arg["body"]
    else:
        body = None

    if "body_data_format" in arg:
        body_data_format = arg["body_data_format"]
    else:
        body_data_format = None

    if "headers" in arg:
        headers = arg["headers"]
    else:
        headers = { 'content-type': "application/json",
                    'cache-control': "no-cache",
                    'user-agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.130 Safari/537.36"
                    }

    ##Intial API Controller
    AP = APIController()

    ##Send API request and assign response to global
    response = AP.SendAPIPacket(
                                http_method=http_method,
                                url=url,
                                params=params,
                                body=body,
                                body_data_format=body_data_format,
                                headers=headers,
                                auth=auth,
                                verify=verify)

    return response