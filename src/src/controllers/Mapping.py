__author__ = 'stephanie'
import pandas as pd

from handlers.csvHandler import CSVReader

class Mapping():
    '''
    Model class representing a mapped pandas dataframe object.

    rawData : pandas.core.frame.DataFrame - Raw CSV data from the
                                            given file.
    table : pandas.core.frame.DataFrame - The finnished table to
                                            write to the database.
    mapping : dict - The YAML configuration mapping.
    '''
    def __init__(self, configDict):
        self.table = [] # Empty
        self.mapping = configDict
        self.rawData = pd.DataFrame # Empty
        if self.readFile(self.mapping['Settings']['FileLocation']):
            self.buildTable()

    def buildTable(self):

        for col, series in self.mapping['Mappings'].iteritems():
            print '$%$%$%$%$ col $%$%$%$%$', col
            df = self.rawData[col].reset_index()

            df.columns =["ValueDateTime", "DataValue"]

            if series['CalculateAggInterval']:

                # Calculate the aggregation interval based on distance
                # between points.

                df['AggregationInterval'] = 0
                df['AggregationIntervalUnitsID'] = 0

            else:
                df['AggregationInterval'] = series['IntendedTimeSpacing']
                df['AggregationIntervalUnitsID'] = series['IntendedTimeSpacingUnitID']

            df['QualityCode'] = 'None'
            df['CensorCode'] = 'Unknown'
            df['ResultID'] = series['ResultID']
            df['UTCOffset'] = self.mapping['Settings']['UTCOffset']

            #df.set_index(['DateTime'], inplace=True)
            self.table.append(df)
            print df

    def readFile(self, path):
        reader = CSVReader()
        self.rawData = reader.reader(path, \
            sep=self.mapping['Settings']['Delimiter'],
            datecol = self.mapping["Settings"]["DateTimeColumnName"],
            skip=self.mapping['Settings']['HeaderRowPosition'] - 1
                                     )
        #read csv into pandas
        if self.rawData.empty:
            return False
        else:
            return True

    def get(self):
        return self.table
