
import wx

from view.clsDataConfigPanel import DataConfigPanelView
from handlers.csvHandler import CSVReader
from copy import deepcopy

class DataConfigPanelController(DataConfigPanelView):
    def __init__(self, daddy, **kwargs):
        super(DataConfigPanelController, self).__init__(daddy, **kwargs)
        self.parent = daddy
        
        self.prev_data_x = {}

    def getInput(self):
        '''
        A method which returns a dict of data.
        Used to share data between panels.
        '''
        return {}

    def populate(self, data):
        '''
        A method to populate the controls/widgets with the contents
        of the given data parameter.
        '''
        print 'data', data
        print 'prev_data', self.prev_data_x
        # Update the list control only if the new data is different.
        if cmp(self.prev_data_x, data) != 0:
            print 'NEW DATA'
            # Create a CSV reader object.
            csv = CSVReader()
            
            # Clear the list control of previous data.
            self.m_listCtrl1.RefreshAllItems()

            # Read the file to get the csv data.
            df = csv.dataFrameReader(data['dataFilePath'],
                skip=data['dataBegin'])
            
            # Get column headers and InsertColumn for each of them.
            columns = csv.getColumnNames(df)
            for column in columns:
                self.m_listCtrl1.InsertColumn(columns.index(column),\
                    column)
            
            # Set the number of items because this is
            # a virtual list ctrl.
            self.m_listCtrl1.SetItemCount(len(df))
    
            # Give the virtual list ctrl a data source.
            self.m_listCtrl1.setData(csv.getData(df))
            # Adjust column width.
            for column_index in range(\
                    self.m_listCtrl1.GetColumnCount()):
                self.m_listCtrl1.SetColumnWidth(column_index,
                    wx.LIST_AUTOSIZE)

        print 'Changing self.prev_data (%s) to %s' % (self.prev_data_x, data)
        self.prev_data_x = deepcopy(data)
        
