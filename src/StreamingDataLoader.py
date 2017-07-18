# !/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'Denver'

#from pandas.io.sql import SQLTable
#
#def _execute_insert(self, conn, keys, data_iter):
#    print "Using monkey-patched _execute_insert"
#    data = [dict((k, v) for k, v in zip(keys, row)) for row in data_iter]
#    conn.execute(self.insert_statement().values(data))
#
#SQLTable._execute_insert = _execute_insert

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from argparse import ArgumentParser
import logging

from src.models.YamlConfiguration import YamlConfiguration
from src.controllers.Mapper import Mapper
from src.lib.Appdirs.appdirs import user_config_dir

import numpy as np

import glob

import time
import pyodbc
import pymysql
import sqlite3

def _get_file(filename):
        #fn = util.resource_path('connection.config')
        fn = os.path.join(user_config_dir("SDL", "UCHIC"), filename)
        print fn

        return fn

def main(arguments):

    # Create logger.
    LOG_FILENAME = _get_file('logfile.txt')
    logger = logging.getLogger('SDL_logger')
    
    # Set logging verbosity to either DEBUG or INFO.
    if arguments.verbose:
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.INFO)

    # Set up logger to log to a file.
    if not os.path.exists(LOG_FILENAME):
        os.makedirs(LOG_FILENAME.strip('logfile.txt'))
    handler = logging.FileHandler(LOG_FILENAME)

    # Set up the formatting of the log strings.
    formatter = logging.Formatter("[%(asctime)s %(levelname)s] %(message)s", "%Y-%m-%d %H:%M:%S")
    handler.setFormatter(formatter)
    
    logger.addHandler(handler)
    
    logger.info('\n\nBeginning execution.')
    logger.debug("Using '%s' as YAML configuration." % arguments.yamlFile)

    if arguments.csvFile:
        logger.info('Using only the specified data file: %s' % arguments.csvFile)

    for arg, i in zip(arguments.yamlFile, range(len(arguments.yamlFile))):
        if os.path.isdir(arg):
            arguments.yamlFile[i] += "/*.yaml"

        else:
            if not arg.endswith('.yaml'):
                arguments.yamlFile[i] = ""
                logger.error("Invalid configuration file (must be .yaml).")

    print [r for r in arguments.yamlFile]
    for arg in arguments.yamlFile:
        for filepath in glob.glob(arg):
            # Create an object to represent the yaml coniguration
            # file.
            yamlModel = YamlConfiguration(filepath,\
                (arguments.csvFile if arguments.csvFile is not None else None),\
                (arguments.restart if arguments.restart is not False else False))

            # List to hold any changes made to the config file to be
            # saved when the program has completed.
            configParamsList = []
            failureList = []

            # Loop through each file given in the YAML configuration.
            files = yamlModel.get()
            for configParams in files:
                # Declare updatedParams to preserve scope.
                updatedParams = configParams 
                print configParams
                dataMapModel = Mapper(configParams.asTuple()[1])
                
                # If it's time to run...
                if not dataMapModel.isTimeToRun():
                    configParamsList.append(updatedParams)
                    continue
                
                # If able to connect to the database...
                if dataMapModel.getDatabase():
                    # If able to perform a mapping...
                    if dataMapModel.map():
                        # Loop through the tables in the mapping. 
                        for table in dataMapModel.getTables():
                            logger.debug('Writing %s...' % table[0])
                            # If able to save table to database...
                            if dataMapModel.save(table[1]):
                                #print "COLUMNS"
                                #print table[1].columns
                                #print "VDT"
                                #print type(table[1]['ValueDateTime'])
                                # Update the latest date time for the table.
                                dataMapModel.updateDateTime(table[1]['ResultID'][0],
                                    np.max(table[1]['ValueDateTime'])) 
                                logger.debug('...Success!')
                                # Update the last byte read.
                                updatedParams = yamlModel.updateLastRead(\
                                                    configParams, table[0])
                            # If not able to save to database.
                            else:
                                # Add table to list of failures
                                failureList.append(table[0])
                configParamsList.append(updatedParams)
            # Error with either YAML or CSV file path given on command line.
            if not files:
                logger.error('No matching configuration found using configuration file "%s" and data file "%s".' % (arguments.yamlFile, arguments.csvFile))
            # No errors. Update the config file with what the app has done.
            else:
                yamlModel.rebase(configParamsList)
            # If any failures exist, write them to the log file.
            if failureList:
                for fail in failureList:
                    logger.info('%s not added to the database.' % fail)

    for arg in arguments.yamlFile:
        if not glob.glob(arg):
            logger.error("No configuration files could be found given directory: '%s'" % arg)
            #print "[error] No configuration files could be found given directory: '%s'" % arguments.yamlFile

    logger.info('Completed execution.')


# Application entry point.
if __name__ == "__main__":
    parser = ArgumentParser(description="StreamingDataLoader")
    parser.add_argument('-r', '--restart', action='store_true', help="Read the entire CSV file to ensure that data is correct and accounted for. This option affects performance. While the integrity of the data is checked each time the program executes, it is still recommended to use this option if you have manually modified your data file between executions.")
    parser.add_argument('-v', '--verbose', action='store_true', help="Enable more verbose logging in the logfile.")
    parser.add_argument('-c', '--config', nargs='+', dest="yamlFile", help="Specify a YAML configuration file in the form of one of these formats:\n1. A single YAML (.yaml) file.\n2. A list of YAML files (.yaml), deliminated by white space.\n3. A directory containing multiple YAML (.yaml) files.", required=False, action="store")
    parser.add_argument('-f', '--file', dest="csvFile", help="Specify a single CSV data file to target instead of the one listed in the configuration file.", required=False, action="store")
    args = parser.parse_args()


    correct_path = ""

    os.chdir(os.getcwd())
    for filename in os.listdir('.'):
        if filename.endswith('.yaml'):
            correct_path = os.getcwd()
            correct_path += filename
            break;

    if args.yamlFile is not None:
        if args in args.yamlFile:
            correct_path = ""
            for path in args.yamlFile:
                correct_path += path + " "

    args.yamlFile = [correct_path.strip()]
    start_time = time.time()
    main(args)

    logger = logging.getLogger('SDL_logger')
    logger.info("Running time: %s seconds" % (time.time() - start_time))
