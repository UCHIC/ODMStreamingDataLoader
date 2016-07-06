
import wx
from datetime import datetime
import dateutil.parser as dparser

from collections import namedtuple
from src.controllers.Database import Database
from src.common.functions import wxdate2pydate

from src.wizard.view.clsAddNewActionsPanel import AddNewActionsPanelView
#from src.wizard.view.clsAddAffiliationPanel import NewAffiliationView
#from src.wizard.controller.frmAffiliationDialog import AffiliationDialog
from src.wizard.controller.frmPersonPanel import PersonPanel
from src.wizard.controller.frmOrganizationPanel import OrganizationPanel
from src.wizard.controller.frmAffiliationPanel import AffiliationPanel
from src.wizard.controller.AffiliationWizard \
    import AffiliationWizard
from src.wizard.view.clsCustomDialog \
    import CustomDialog
from src.wizard.controller.frmAddNewMethodPanel \
    import AddNewMethodPanelController

from odm2api.ODM2.models import Actions, ActionBy

class Test:
    def __init__(self, name, org):
        self.name = name
        self.org = org

class AddNewActionsPanelController(AddNewActionsPanelView):
    def __init__(self, daddy, db, **kwargs):
        super(AddNewActionsPanelController, self).__init__(daddy,
            **kwargs)
        self.parent = daddy
        self.db = db
        
        self.m_comboBox13.Bind(wx.EVT_COMBOBOX, self.onActionTypeSelect)
        self.m_b.Bind(wx.EVT_BUTTON, self.onNewAffiliation)
        self.btnNewMethod.Bind(wx.EVT_BUTTON, self.onNewMethod)
        self.btnNewMethod.Enable(False)
        #self.affList.Bind(wx.EVT_LEFT_DOWN, self.onAffListClick)    
        #self.affList.Bind(wx.EVT_LIST_INSERT_ITEM, self.onAffInsert)    
        #self.affList.Bind(wx.EVT_LIST_ITEM_SELECTED, self.onAffSelect)    
        self.read = self.db.getReadSession()
        
        self.populateFields()

    def populateFields(self):
        #read = self.db.getReadSession()

        actionTypes = [i.Name for i in self.read.getCVs(type = "actiontype")]
        self.m_comboBox13.AppendItems(actionTypes)

        #self.affList.SetObjects(self.read.getDetailedAffiliationInfo())
        self.affList.AddObjects(self.read.getDetailedAffiliationInfo())

    def onActionTypeSelect(self, event):
        # self.sp_ref = [{i.SRSName:i.SpatialReferenceID}\
        #       for i in read.getCVSpacialReferenceTypes()]
        self.btnNewMethod.Enable(True)
        self.m_comboBox134.Clear()
        self.m_comboBox134.SetValue("Select Method")
        self.methods = [{i.MethodName:i.MethodID} for i in self.read.getMethods(type=event.GetString())]
        self.m_comboBox134.SetItems(\
            [y for x in [i.keys() for i in self.methods] for y in x]
            )
        #self.m_comboBox134.SetItems(methodTypes)
    
    def onNewMethod(self, event):
        dlg = CustomDialog(self, u'Create New Method')
        newMethodPanel = AddNewMethodPanelController(dlg, self.db)
        dlg.addPanel(newMethodPanel)
        newMethodPanel.setTypeFilter(str(self.m_comboBox13.GetStringSelection()))
        if dlg.ShowModal() == wx.ID_OK:
            newMethod = newMethodPanel.method
            self.methods = [{i.MethodName:i.MethodID}\
                for i in [newMethod]]
            self.m_comboBox134.AppendItems([y for x in [i.keys() for i in self.methods] for y in x])
            #self.m_comboBox134.SetValue(newMethod.MethodName)
        dlg.Destroy()
        event.Skip()

    def onNewAffiliation(self, event):
        wiz = AffiliationWizard(self,
            database=self.db,
            title="Create New Affiliation")
        wiz.addPage(PersonPanel)
        wiz.addPage(OrganizationPanel)
        wiz.addPage(AffiliationPanel)
        if wiz.ShowModal() == wx.ID_OK:
            read = self.db.getReadSession()
            newAffiliations = read.getDetailedAffiliationInfo()
            self.affList.SetObjects(newAffiliations)
        event.Skip()

    def onOK(self, event):
        # Try to validate the form.
        if not self.Validate():
            self.Refresh()
            return
        elif not self.affList.GetSelectedObjects():
            wx.MessageBox('Select at least one affiliation.', 'Error')
            self.Refresh()
            return
        else:
            # Move the data into the value dictionaries.
            # All data should be valid at this point.
            self.getFieldValues() 
            try:
                write = self.db.getWriteSession()
                action= Actions(ActionTypeCV=self.actionType,
                    MethodID=self.methodID,
                    BeginDateTime=self.beginDT,
                    BeginDateTimeUTCOffset=self.beginDTUTC,
                    EndDateTime=self.endDT,
                    EndDateTimeUTCOffset=self.endDTUTC,
                    ActionDescription=self.actionDesc,
                    ActionFileLink=self.actionLink)
                action = write.createAction(action)

                self.actionID = action.ActionID
                
                for affID in self.affiliationList:
                    actionby=ActionBy(\
                        ActionID=self.actionID,
                        AffiliationID=affID,
                        IsActionLead=(affID == self.actionLead))
                    write.createActionby(actionby)
                
            except Exception as e:
                print e
                #todo Catch error and display message
        event.Skip()

    def getFieldValues(self):

        keys = [y for x in [i.keys() for i in self.methods] for y in x]
        vals = [y for x in [i.values() for i in self.methods] for y in x]
        d = dict(zip(keys, vals))

        self.actionType = str(self.m_comboBox13.GetStringSelection())
        self.methodID = d[str(self.m_comboBox134.GetStringSelection())]
        self.beginDT = self._getTime(self.m_datePicker5, self.m_timePicker1)
        self.beginDTUTC = self.spinUTCBegin.GetValue()
        self.affiliationList = [i.affiliationID for i in self.affList.GetSelectedObjects()]
        for i in self.affList.GetSelectedObjects():
            if self.affList.IsChecked(i):
                self.actionLead = i.affiliationID
                break
        if self.m_datePicker51.GetValue().IsValid():
            self.endDT = self._getTime(self.m_datePicker51, self.m_timePicker2)
        else:
            self.endDT = None
        self.endDTUTC = self.beginDTUTC
        if str(self.m_textCtrl232.GetValue()) == '':
            self.actionDesc = None
        else:
            self.actionDesc = str(self.m_textCtrl232.GetValue())
        if str(self.m_textCtrl234.GetValue()) == '':
            self.actionLink = None
        else:
            self.actionLink = str(self.m_textCtrl234.GetValue())

    def _getTime(self, d, t):
        date = d.GetValue()
        time = t.GetValue()
        begin = ''
        try:
            begin = datetime.strptime(str(date), '%c').strftime('%Y-%m-%d')
            begin = begin + ' ' + str(time)
        except ValueError:
            date = str(date)
            date = date.replace("'PMt'", '')
            date = date.replace("'AMt'", '') 
            begin = datetime.strptime(date, '%A, %B %d, %Y %X %p').strftime('%Y-%m-%d')
            begin = begin + ' ' + str(time)
        return dparser.parse(begin)




if __name__ == '__main__':
    db = Database()
    Credentials = namedtuple('Credentials', 'engine, host, db_name, uid, pwd')
    db.createConnection(Credentials(\
        'mysql',
        'rambo.bluezone.usu.edu',
        'odm2',
        'odm',
        'odm'))
    app = wx.App()
    frame = wx.Frame(None)
    frame.SetSizer(wx.BoxSizer(wx.VERTICAL))
    pnl = AddNewActionsPanelController(frame, db)
    frame.CenterOnScreen()
    frame.Show()
    app.MainLoop()
 
