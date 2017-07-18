
import wx

from src.wizard.view.clsAddNewMethodPanel import AddNewMethodPanelView
from odm2api.ODM2.models import Methods

class AddNewMethodPanelController(AddNewMethodPanelView):
    def __init__(self, daddy, db, **kwargs):
        super(AddNewMethodPanelController, self).__init__(daddy,
            **kwargs)
        self.parent = daddy
        self.db = db
        self.method = None# This is our method return value
        self.methodCode = None
        self.methodName = None
        self.desc = None
        self.populateFields()
    
    def setTypeFilter(self, t):
        self.m_comboBox14.AppendItems([t])

    def populateFields(self):
        read = self.db.getReadSession()

        #methodTypes = [i.Name for i in read.getCVMethodTypes()]
        #self.m_comboBox14.AppendItems(methodTypes)

        self.orgs = [{i.OrganizationName: i.OrganizationID}\
            for i in read.getOrganizations()]
        self.m_comboBox141.AppendItems(\
            [y for x in [i.keys() for i in self.orgs] for y in x])

    def onOK(self, event):
        if not self.Validate():
            self.Refresh()
            return
        else:
            self.getFieldValues()
            try:
                write = self.db.getWriteSession()
                meth = Methods(\
                    MethodCode=self.methodCode,
                    MethodName=self.methodName,
                    MethodTypeCV=self.methodType,
                    OrganizationID=self.orgId,
                    MethodDescription=self.desc)
                self.method = write.createMethod(meth)
            except Exception as e:
                wx.MessageBox(e, 'Error saving method to database.')
        event.Skip()
    
    def getFieldValues(self):
        self.methodCode = str(self.m_textCtrl33.GetValue())
        self.methodName = str(self.m_textCtrl331.GetValue())
        self.desc = str(self.m_textCtrl38.GetValue())

        if str(self.m_comboBox14.GetStringSelection()) != '':
            self.methodType = str(self.m_comboBox14.GetStringSelection())
        else:
            self.methodType = None

        keys = [y for x in [i.keys() for i in self.orgs] for y in x]
        vals = [y for x in [i.values() for i in self.orgs] for y in x]

        d = dict(zip(keys, vals))

        if str(self.m_comboBox141.GetStringSelection()) != '':
            self.orgId = d[self.m_comboBox141.GetStringSelection()]
        else:
            self.orgId = None
