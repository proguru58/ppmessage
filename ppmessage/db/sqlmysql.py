# -*- coding: utf-8 -*-
# Copyright (C) 2010-2016 PPMessage.
# Guijin Ding, dingguijin@gmail.com
# All rights reserved
#
# mdm/db/sqlmysql.py
#

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import scoped_session
from sqlalchemy import create_engine

from sqlalchemy import exc
from sqlalchemy import event
from sqlalchemy.pool import Pool

from ppmessage.core.singleton import singleton
from ppmessage.core.constant import DB_HOST
from ppmessage.core.constant import DB_NAME
from ppmessage.core.constant import DB_USER
from ppmessage.core.constant import DB_PASS

import traceback

BaseModel = declarative_base()

@event.listens_for(Pool, "checkout")
def ping_connection(dbapi_connection, connection_record, connection_proxy):
    try:
        cursor = dbapi_connection.cursor()
        cursor.execute("SELECT 1")
        cursor.close()
    except:
        # optional - dispose the whole pool
        # instead of invalidating one at a time
        # connection_proxy._pool.dispose()

        # raise DisconnectionError - pool will try
        # connecting again up to three times before raising.
        raise exc.DisconnectionError()
    
    
@singleton
class SQLMysql():

    def __init__(self):
        self.dbhost = DB_HOST
        self.dbname = DB_NAME
        self.dbuser = DB_USER
        self.dbpassword = DB_PASS
        self.dbengine = None
        self.dbsession_class = None
        
    def createEngine(self):
                
        db_string = "mysql+mysqlconnector://%s:%s@%s/%s?charset=utf8" % (self.dbuser, 
                                                     self.dbpassword,
                                                     self.dbhost,
                                                     self.dbname)
        if self.dbengine == None:
            engine = create_engine(db_string, echo_pool=True)
            self.dbengine = engine
# it will create a thread local session for every single web request
        return self.dbengine

    def getSessionClass(self):
        assert(self.dbengine)
        return scoped_session(sessionmaker(bind=self.dbengine))
    
    def createDatabase(self):

        """
        this method should be called when system initialization

        """

        self.dbengine.execute("CREATE DATABASE %s default charset utf8" % (self.dbname))
        self.dbengine.execute("USE %s" % (self.dbname))
        BaseModel.metadata.create_all(self.dbengine)

