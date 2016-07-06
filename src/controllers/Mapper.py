__author__ = 'stephanie, denver'
import pandas as pd
import numpy as np
from collections import namedtuple
import logging
import datetime
from dateutil.parser import parse
from handlers.csvHandler import CSVReader
from controllers.Database import Database

logger = logging.getLogger('SDL_logger')

class Mapper():
    '''
    Class representing a mapped pandas dataframe object.
    
    Attributes:
        rawData : pandas.core.frame.DataFrame - Raw CSV data from the
                                                given file.
        tables : pandas.core.frame.DataFrame - The finnished tables to
                                                write to the database.
        mapping : dict - The YAML configuration mapping.
        dbWriter : Database - The database object that will be used.
    '''
    
    
    
    def __init__(self, configDict):
        self.tables = [] # Empty
        self.mapping = configDict
        self.rawData = pd.DataFrame # Empty

        self.dbWriter = Database()
        self.performDuplicateValueChecks = False

    def isTimeToRun(self):
        """
        isTimeToRun is a public method that checks whether this
        configuration should run or not (based on it's schedule.)
        """
        startDate = parse(str(self.mapping['Schedule']['Beginning']))
        lastUpdate = str(self.mapping['Schedule']['LastUpdate'])
        if str(lastUpdate) == '--':
            lastUpdate = parse(str(self.mapping['Schedule']['Beginning']))
        else:
            lastUpdate = parse(str(self.mapping['Schedule']['LastUpdate']))
            
        print "last updated:", lastUpdate
        period = self.mapping['Schedule']['Time']
        periodUnit = self.mapping['Schedule']['Frequency']
        # Get period in terms of seconds.
        if periodUnit == 'Week':
            period = period * 604800
        elif periodUnit == 'Day':
            period = period * 86400
        elif periodUnit == 'Hour':
            period = period * 3600
        elif periodUnit == 'Minute':
            period = period * 60
        elif periodUnit == 'Second':
            period = period * 1
        else:
            logger.error("Unknown frequency: %s" % periodUnit)
            return False

        now = parse(datetime.datetime.strftime(datetime.datetime.now(), '%Y-%m-%d %H:%M:%S'))
        print "current time:", now
        delta = lastUpdate + datetime.timedelta(seconds=period)
        print "Due:", delta
        if startDate > now:
            logger.info("Not beginning until %s" % startDate)
            return False
        if delta <= now:
            self.recordLastUpdate(now)
            return True
        else:
            logger.info("Not running until %s" % delta)
            return False

    def recordLastUpdate(self, time):
        """
        Updates the "LastUpdate" atribute of the config file.
        """
        self.mapping['Schedule']['LastUpdate'] = str(time)

    def getDatabase(self):
        '''
        getDatabase is a public method that should be called before
        interacting with the database. It snatches up the database
        credentials from the YAML file object (mapping) and returns
        a named-tuple called Credentials.
        '''
        Credentials = namedtuple('Credentials', 'engine host, db_name,\
                                    uid, pwd')
        return self.dbWriter.createConnection(Credentials(\
                            self.mapping['Database']['Engine'],
                            self.mapping['Database']['Address'],
                            self.mapping['Database']['DatabaseName'],
                            self.mapping['Database']['UserName'],
                            self.mapping['Database']['Password']))
    
    
    
    def map(self):
        '''
        This public method begins the process of mapping the data
        into something that we can write to the database. First,
        the file is read from the config file (mapping), if that
        works, we begin to build a new Pandas dataframe.
        '''
        #if self._readFile(self.mapping['Settings']['FileLocation']):
        try:
            if self._readFile(self.mapping['Settings']['FileLocation']):
                self._buildTables()
            #self._buildTables()
        except KeyError as e:
            logger.error("Unable to create mapping. Check your data & configuration files. %s" %e)
            return False
        return True
    
    
    
    def _readFile(self, path):
        '''
        readFile gathers the raw data (rawData) from the given CSV
        file (path). If rawData ends up being empty, we return False,
        otherwise we return as True.
        '''
        
        reader = CSVReader()

        # Collect the smallest 'LastByteRead' in the file.
        byte = self._getStartByte()
        
        logger.debug('Last successful byte read: %s' % byte)
       
        logger.info("Data file location: '%s'" % path)
        self.rawData = reader.byteReader(path,
                start_byte=byte,
                datecol=self.mapping['Settings']['DateTimeColumnName'],
                sep=self.mapping['Settings']['Delimiter'],
                header=self.mapping['Settings']['HeaderRowPosition'],
                dataBegin=self.mapping['Settings']['DataRowPosition'])

        if self.rawData.empty:
            return False
        else:
            return True
    
    
    
    def _getStartByte(self):
        '''
        getStartByte is a private method which determines the smallest
        byte number of the given columns.
        '''
        m = [value['LastByteRead'] for key,value in \
            self.mapping['Mappings'].items()]
        
        # If all of the bytes are the same, don't do a
        # duplicate values check when writing to database.
        self.performDuplicateValueChecks = not len(set(m)) <= 1

        # Starting byte will be the lowest value.
        startByte = int(min(m))
        
        # But if it's less than 0 (AKA running in restart mode)
        # then just set it to 0.
        if startByte < 0:
            startByte = 0
        
        return startByte
    
    
    
    def _buildTables(self):
        '''
        buildTables creates a brand new Pandas dataframe (tables),
        gathering the needed columns from the YAML file (mapping)
        and raw data (rawData).
        '''
        for col, series in self.mapping['Mappings'].iteritems():
            logger.info("*********doing column: %s" % col)
            df = self.rawData[col].reset_index()
            df.columns = ['ValueDateTime', 'DataValue']
           
            if series['CalculateAggInterval'] not in [False, 'False', 'false']:

                df['TimeAggregationInterval'] = 0
                df['TimeAggregationIntervalUnitsID'] = 102

            else:
                df['TimeAggregationInterval'] = series['IntendedTimeSpacing']
                df['TimeAggregationIntervalUnitsID'] = series['IntendedTimeSpacingUnitID']
            
            # FIXME change to none when released.
            # SDL Test Data is just for our testing purposes.
            #df['QualityCodeCV'] = 'None'
            df['QualityCodeCV'] = 'SDL Test Data'
            # TODO add unknown to database.
            #df['CensorCodeCV'] = 'Unknown'
            df['CensorCodeCV'] = 'Non-detect'
            df['ResultID'] = series['ResultID']
            df['ValueDateTimeUTCOffset'] = self.mapping['Settings']['UTCOffset']

            noDataValue = self._getNoDataValue(df['ResultID'][0])

            df = df.replace(to_replace=[np.nan, '-INF'],
                            value=[noDataValue, noDataValue],
                            regex=True)
            
            replaced = df.isin([noDataValue]).sum().sum()

            #print "BEFORE",df.ValueDateTime
            df.ValueDateTime = pd.to_datetime(\
                                pd.Series(df.ValueDateTime))
            #print "AFTER",df.ValueDateTime
            self.tables.append((col, df))
            
            logger.info('Result: %s Total Values: %d, Non-data Values: %d' % (col, len(df), replaced))
    
    def _getNoDataValue(self, resultID):
        '''
        _getNoDataValue is a wrapper method to the database object's
        getNoDataValue method.
        '''
        #print "-------resultID", resultID
        return self.dbWriter.getNoDataValue(resultID)
    
    
    
    def getTables(self):
        '''
        getTables is a public method that returns a Pandas dataframe.
        It should be called after a mapping has been made.
        '''
        #logger.info("TABLES: %s" % self.tables)
        return self.tables
    
    
    
    def save(self, data):
        '''
        save is a public method that wraps the Database.write method.
        '''
        return self.dbWriter.write(data,
            self.performDuplicateValueChecks)

    def updateDateTime(self, seriesId, dateTime):
        '''
        updateDateTime is a public method that wraps the
        Database.updateDateTime method. It's part of this module
        because the database connection is only accessable through
        here.
        '''
        return self.dbWriter.updateDateTime(seriesId, dateTime)      


