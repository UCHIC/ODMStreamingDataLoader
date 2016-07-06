
__author__ = 'Denver'

import sys
import logging
from datetime import datetime



# sys.path.append('/home/denver/Documents/ODM2PythonAPI')

from odm2api.ODMconnection import dbconnection
from odm2api.ODM2.services import *





logger = logging.getLogger('SDL_logger')

class Database:
    '''
    This class uses the ODM2 API to connect and interact with an
    ODM2 database.
    '''
    
    def createConnection(self, Credentials):
        '''
        createConnection is a public method that should be called 
        after obtaining login credentials (Credentials) and is used
        to set up a new connection to an ODM2 database.
        '''
        print Credentials.engine
        print Credentials.host
        print Credentials.db_name
        print Credentials.uid
        print Credentials.pwd

        self.session_factory = \
            dbconnection.createConnection(Credentials.engine, Credentials.host,
                                            Credentials.db_name,
                                            Credentials.uid,
                                            Credentials.pwd, 2.0)
        if not self.session_factory:
            logger.error("Unable to connect to database with host='%s', database='%s', user='%s', pwd='%s'." % (Credentials.host, Credentials.db_name, Credentials.uid, Credentials.pwd))
            return False
        
        return True


    def write(self, data, duplicateValuesCheck):
        '''
        write is a public method that is used to write data to an 
        ODM2 database. This method should only be called once a valid
        database connection has been established.
        '''
        cr = CreateODM2(self.session_factory)
        
        finished_data = data

        if duplicateValuesCheck == True:
            logger.info('Performing duplicate database value check. (This affects performance).')
            # Check if data is already in the database.
            rc = ReadODM2(self.session_factory)
            #TODO UPDATE API ON THIS CALL
            #dt = rc.getResultValidDateTime(data['ResultID'][0])
            r = rc.getResults(ids=[int(data['ResultID'][0])])
            dt = r[0].ValidDateTime
            finished_data = data[data['ValueDateTime'] > dt[0]]

        #print "FINISHED DATA:",finished_data
        if cr.createTimeSeriesResultValues(finished_data) is None:
            return False
        return True

    def getNoDataValue(self, resultID):
        '''
        getNoDataValue querys the ODM2 API and returns
        the "No data value" for the given ResultID.
        '''

        rc = ReadODM2(self.session_factory)
        result = rc.getResults([int(resultID)])
        #result = rc.getResultByID(int(resultID))
        print "result-----", result
        if len(result) == 0:
            logger.error("No matching result ID in database.")
            return None
        return result[0].VariableObj.NoDataValue

    def updateDateTime(self, seriesId, dateTime):
        '''
        updateDateTime uses the ODM2 API to update the latest
        date time added to the database.
        '''
        print "DATETIME:", dateTime, type(dateTime)
        cr = UpdateODM2(self.session_factory)
        cr.updateResultValidDateTime(seriesId, dateTime)
        return True

    def getWriteSession(self):
        '''
        '''
        _session = self.session_factory.getSession()
        return CreateODM2(self.session_factory)
    
    def getReadSession(self):
        '''
        '''
        _session = self.session_factory.getSession()
        return ReadODM2(self.session_factory)
