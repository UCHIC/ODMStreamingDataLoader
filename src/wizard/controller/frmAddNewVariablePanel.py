
import wx

from src.wizard.view.clsAddNewVariablePanel import AddNewVariablePanelView
from odm2api.ODM2.models import Variables

class AddNewVariablePanelController(AddNewVariablePanelView):
    def __init__(self, daddy, db, **kwargs):
        super(AddNewVariablePanelController, self).__init__(daddy,
            **kwargs)
        self.parent = daddy
        self.db = db

        self.populateFields()

    def populateFields(self):
        '''
        '''
        read = self.db.getReadSession()

        # names = [i.Name for i in read.getCVVariableNames()]
        names = [i.Name for i in read.getCVs(type="Variable Name")]
        self.m_comboBox4.AppendItems(names)

        
        # types = [i.Name for i in read.getCVVariableTypes()]
        types = [i.Name for i in read.getCVs(type="Variable Type")]
        self.m_comboBox12.AppendItems(types)
        
        # speciations = [i.Name for i in read.getCVSpeciations()]
        speciations = [i.Name for i in read.getCVs(type="Speciation")]
        self.m_comboBox2.AppendItems(speciations)

    def onOK(self, event):
        if not self.Validate():
            self.Refresh()
            return
        self.getFieldValues()
        try:
            write = self.db.getWriteSession()
            var = Variables(\
                VariableCode=self.variableCode,
                VariableNameCV=self.variableName,
                VariableTypeCV=self.variableType,
                NoDataValue=self.ndv,
                SpeciationCV=self.speciation,
                VariableDefinition=self.definition)
            write.createVariable(var)

        except Exception as e:
            print e

        event.Skip()

    def getFieldValues(self):
        self.variableCode = str(self.m_textCtrl23.GetValue())
        self.variableName = str(self.m_comboBox4.GetStringSelection())
        self.variableType = str(self.m_comboBox12.GetStringSelection())
        self.ndv = float(self.m_textCtrl15.GetValue())
        
        if str(self.m_comboBox2.GetStringSelection()) != '':
            self.speciation = str(self.m_comboBox2.GetStringSelection())
        else:
            self.speciation = None
        if str(self.m_textCtrl24.GetValue()) != '':
            self.definition = str(self.m_textCtrl24.GetValue())
        else:
            self.definition = None
        
