
import wx
from copy import deepcopy
from collections import namedtuple 
from src.wizard.view.clsDataConfigPanel \
    import DataConfigPanelView, MyColLabelRenderer
from src.handlers.csvHandler import CSVReader
from src.common.functions import searchDict
from src.controllers.Database import Database
from src.wizard.controller.frmSeriesWizard import SeriesWizardController
from src.wizard.controller.frmVirtualGrid import GridBase
from src.wizard.controller.frmSeriesDialog import SeriesSelectDialog
from src.wizard.models.ResultMapping import ResultMapping
from odm2api.ODM2.services.readService import ReadODM2

class DataConfigPanelController(DataConfigPanelView):
    def __init__(self, daddy, **kwargs):
        super(DataConfigPanelController, self).__init__(daddy, **kwargs)
        self.parent = daddy
        
        self.prev_data = {}
        self.inputDict = {}
        self.m_listCtrl3.Bind(wx.EVT_LIST_ITEM_RIGHT_CLICK, self.rightClick)


    def rightClick(self, event):
        if len(event.GetEventObject().GetSelectedObjects()) < 1:
            return

        menu = wx.Menu()
        menu.Append(11, "Edit Mapping")
        menu.Append(12, "Delete Mapping")
        
        wx.EVT_MENU(menu, 11, self.editMapping)
        wx.EVT_MENU(menu, 12, self.deleteMapping)
        
        if len(event.GetEventObject().GetSelectedObjects()) > 1:
            menu.Enable(11, False)
            menu.SetLabel(12, "Delete Mappings")

        self.PopupMenu(menu)
        menu.Destroy()
        event.Skip()

    def editMapping(self, event):
        self.selectedColumn = \
            self.m_listCtrl3.GetSelectedObject().variableName
        self.runSeriesSelectDialog()
        event.Skip()
    
    def deleteMapping(self, event):
        names = [obj.variableName for obj in \
            self.m_listCtrl3.GetSelectedObjects()]
        for i in range(0, self.m_listCtrl1.GetNumberCols()):
            if str(self.m_listCtrl1.GetColLabelValue(i)) in names:
                self.m_listCtrl1.SetColLabelRenderer(\
                    i,
                    MyColLabelRenderer('#f0f0f0'))
                self.m_listCtrl1.Refresh()
       
        # Instead of deleting from mapping right now,
        # add to a list that can be deleted when finish
        # button is clicked.
        for name in self.m_listCtrl3.GetSelectedObjects():
            self.deletedMappings.append(name.variableName)
        #for name in self.m_listCtrl3.GetSelectedObjects():
        #    self.inputDict['Mappings'].pop(name.variableName)

        self.m_listCtrl3.RemoveObjects(\
            self.m_listCtrl3.GetSelectedObjects())
        self.m_listCtrl3.RepopulateList()
        
        event.Skip()
    
    def getInput(self):
        '''
        A method which returns a dict of data.
        Used to share data between panels.
        '''
        try:
            lastUpdate = str(self.inputDict['Schedule']['LastUpdate'])
        except KeyError: 
            self.inputDict['Schedule']['LastUpdate'] = "--"
        
        i = self.choiceTimeCol.GetSelection()
        self.inputDict['Settings']['DateTimeColumnName'] = \
            str(self.choiceTimeCol.GetString(i))
        
        self.inputDict['Settings']['FillGaps'] = 'false'
        
        # Add mappings.
        for mapping in self.newMappings:
            self.inputDict['Mappings'].update(mapping)
        
        # Delete mappings.
        for mapping in self.deletedMappings:
            self.inputDict['Mappings'].pop(mapping)
        
        for k,v in self.inputDict['Mappings'].iteritems():
            #print v
            v['IntendedTimeSpacing'] = self.spinTimeSpacing.GetValue()
            i = self.choiceUnitID.GetSelection()
            unitID = self.timeUnits[str(self.choiceUnitID.GetString(i))]
            v['IntendedTimeSpacingUnitID'] = unitID
        
        self.inputDict['Settings']['UTCOffset'] = \
            self.spinUTCOffset.GetValue()
        
        return self.inputDict


    def setInput(self, data):
        """
        setInput: Populates the form with pre-existing data.
        """
        self.deletedMappings = []
        self.newMappings = []
        read = self.parent.db.getReadSession()
        self.inputDict.update(data)
        
        self.setInputGrid(data)
        self.setInputTimeColumn()
        self.setInputMappingList(self.inputDict, read)
        self.setInputIntendedTimeSpacing()
        self.setInputUTCOffset()
        self.setInputUnit(read)

    def setInputGrid(self, data):
        """
        getInputGrid: Populate the grid that
        displays the csv data file.
        """
        csv = CSVReader()
        df = csv.dataFrameReader(searchDict(data, 'FileLocation'),
            header=searchDict(data, 'HeaderRowPosition'), sep=searchDict(data, 'Delimiter'),
            dataBegin=searchDict(data, 'DataRowPosition'))
        
        self.columns = csv.getColumnNames(df)
        # Create the underlying table of data for
        # the grid control. Having a virtual table
        # enables the control to display millions of
        # cells of data efficiently.
        base = GridBase(csv.getData(df[:50]), self.columns)
        # Assign the table to the grid control.
        self.m_listCtrl1.setTable(base)

        for column in range(self.m_listCtrl1.GetNumberCols()):
            self.m_listCtrl1.AutoSizeColLabelSize(column)

    def setInputMappingList(self, existingData, read):
        """
        setInputMappingList: Populates the list of mappings
        with any mappings that already exist *and*
        match the variables from the configuration file. 
        """
        # Determine if any mappings exist.
        try:
            existingData["Mappings"]
        except KeyError:
            existingData.update({"Mappings": {}})
        
        self.m_listCtrl3.DeleteAllItems()
        self.m_listCtrl3.RepopulateList()
        
        popThese = []
        # Iterate through the mappings 
        for variableName, values in existingData["Mappings"].iteritems():
            # Fist check if the variable name appears in the data file.
            if str(variableName) not in self.columns:
                # If it doesn't exist, then remove it.
                popThese.append(variableName)
                continue
            # Add the variable name to the mapping list.
            mapping = read.getDetailedResultInfo(\
                "Time series coverage",
                values['ResultID'])
            mapped = mapping[0]
            self.m_listCtrl3.AddObject(
                ResultMapping(mapped.resultID,
                    mapped.samplingFeatureCode,
                    mapped.samplingFeatureName,
                    mapped.methodCode,
                    mapped.methodName,
                    mapped.variableCode,
                    mapped.variableNameCV,
                    mapped.processingLevelCode,
                    mapped.processingLevelDef,
                    mapped.unitsName,
                    variableName))
        if popThese:
            wx.MessageBox("Mappings for the following variables exist, but do not appear in the selected data file:\n'%s'\n\nThese mappings will be deleted if you continue." \
                % (", ".join(popThese)),
                "No matching variables")
            for var in popThese:
                existingData["Mappings"].pop(var)
        # Color columns with mappings.
        for i in range(0, self.m_listCtrl1.GetNumberCols()):
            if str(self.m_listCtrl1.GetColLabelValue(i)) \
            in existingData["Mappings"].keys():
                self.m_listCtrl1.SetColLabelRenderer(\
                    i,
                    MyColLabelRenderer('#50c061'))
            else:
                self.m_listCtrl1.SetColLabelRenderer(i,
                    MyColLabelRenderer('#f0f0f0'))
                
    
    
    def setInputTimeColumn(self):
        """
        setInputTimeColumn: Populates the combo box
        used to define which column is the time column.
        """
        self.choiceTimeCol.Clear()
        [self.choiceTimeCol.Append(column) \
            for column in self.columns]
        try:
            dateCol = self.inputDict['Settings']['DateTimeColumnName']
            i = self.choiceTimeCol.FindString(str(dateCol))
            self.choiceTimeCol.SetSelection(i)
        except Exception as e:
            self.choiceTimeCol.SetSelection(0)

    def setInputIntendedTimeSpacing(self):
        """
        setInputUTCOffset: Attempts to set the value of 
        intended time spacing spin ctrl to a pre-existing number.
        """

        try:
            self.spinTimeSpacing.SetValue(\
                searchDict(self.inputDict['Mappings'],
                    'IntendedTimeSpacing'))
        except KeyError:
            self.spinTimeSpacing.SetValue(0)

    def setInputUTCOffset(self):
        """
        setInputUTCOffset: Attempts to set the value of 
        UTC offset to a pre-existing number.
        """
        try:
            offset = self.inputDict['Settings']['UTCOffset']
            self.spinUTCOffset.SetValue(int(offset))
        except KeyError:
            self.spinUTCOffset.SetValue(0)

    def setInputUnit(self, read):
        """
        setInputUTCOffset: Attempts to set the units
        combo box to a pre-existing value.
        """
        self.choiceUnitID.Clear()

        timeUnits = read.getUnits(type='Time')
        self.timeUnits = {}
        try:
            [self.timeUnits.update({i.UnitsName:i.UnitsID}) for i in timeUnits]
        except Exception as e:
            print e
            wx.MessageBox("Error reading time units from database.", "Time Units Error")

        for unit in timeUnits:
            self.choiceUnitID.Append(unit.UnitsName)
        try:
            unitID = searchDict(self.inputDict['Mappings'],
                'IntendedTimeSpacingUnitID')
            #unit = read.getUnitById(int(unitID))
            unit = read.getUnits(ids = [int(unitID)])[0]
            i = self.choiceUnitID.FindString(unit.UnitsName)
            self.choiceUnitID.SetSelection(i)
        except KeyError:
            self.choiceUnitID.SetSelection(0)


    def onAddNew(self, event):
        self.runSeriesSelectDialog()
        # event.Skip()
   
    def onCellClick(self, event):
        event.Skip()
    
    def onColClick(self, event): 
        if event.GetCol() > -1:
            # Get the column header.
            self.selectedColumn = \
                self.m_listCtrl1.GetColLabelValue(event.GetCol())
        # event.Skip
    
    def onColDoubleClick(self, event):
        if event.GetCol() > -1:
            self.selectedColumn = \
                self.m_listCtrl1.GetColLabelValue(event.GetCol())
            if self.selectedColumn == str(self.choiceTimeCol.GetStringSelection()):
                msg = wx.MessageBox('This column is not mappable because you have chosen it as your date time column.', 'Configuration Error')
            else:
                if self.runSeriesSelectDialog():
                    self.m_listCtrl1.SetColLabelRenderer(\
                        int(event.GetCol()),
                        MyColLabelRenderer('#50c061'))
                    self.m_listCtrl1.Refresh()
        event.Skip()
    
    def onTimeSelect(self, event):
        index = self.choiceTimeCol.GetSelection()
        self.selectedDateColumn = self.choiceTimeCol.GetString(index)

        event.Skip()
   
    def onTimeChoice(self, event):
        self.selectedDateColumn = event.GetEventObject().GetString(event.GetEventObject().GetSelection())
        event.Skip()


    def runSeriesSelectDialog(self):
        dlg = SeriesSelectDialog(self,
                variable=self.selectedColumn,
                database=self.parent.db)
        #dlg.CenterOnParent()
        if dlg.ShowModal() == wx.ID_OK:
            dlg.selectedResult.variableName = self.selectedColumn
            #print dlg.selectedResult.variableNameCV
            #import pprint
            
            # Instead of adding immediately to mappings
            # add it to a list to be added when finish button
            # is clicked.
            self.newMappings.append({str(self.selectedColumn):{\
                'ResultID':int(dlg.selectedResult.resultID),
                'LastByteRead':0,
                'CalculateAggInterval':'false'}})
            
            #pprint.pprint(self.inputDict)
            for m in self.m_listCtrl3.GetObjects():
                if m.variableName == dlg.selectedResult.variableName:
                    self.m_listCtrl3.RemoveObjects([m])
                    break

            self.m_listCtrl3.AddObject(dlg.selectedResult)
            dlg.Destroy()
            return True
        dlg.Destroy()
        return False


