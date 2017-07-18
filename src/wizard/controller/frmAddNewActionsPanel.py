import wx
from datetime import datetime
import dateutil.parser as dparser
from collections import namedtuple
from src.controllers.Database import Database
from src.wizard.view.clsAddNewActionsPanel import AddNewActionsPanelView
from src.wizard.controller.frmPersonPanel import PersonPanel
from src.wizard.controller.frmOrganizationPanel import OrganizationPanel
from src.wizard.controller.frmAffiliationPanel import AffiliationPanel
from src.wizard.controller.AffiliationWizard import AffiliationWizard
from src.wizard.view.clsCustomDialog import CustomDialog
from src.wizard.controller.frmAddNewMethodPanel import AddNewMethodPanelController
from odm2api.ODM2.models import Actions, ActionBy


class AddNewActionsPanelController(AddNewActionsPanelView):
    def __init__(self, daddy, db):
        super(AddNewActionsPanelController, self).__init__(daddy)
        self.parent = daddy
        self.db = db
        self.action = None

        self.action_type_combo.Bind(wx.EVT_COMBOBOX, self.onActionTypeSelect)
        self.m_b.Bind(wx.EVT_BUTTON, self.onNewAffiliation)
        self.btnNewMethod.Bind(wx.EVT_BUTTON, self.onNewMethod)
        self.btnNewMethod.Enable(False)
        self.read = self.db.getReadSession()

        self.populateFields()

    def populateFields(self):
        action_controlled_vocabulary = self.read.getCVs(type='actiontype')
        action_types = [vocab.Name for vocab in action_controlled_vocabulary]

        self.action_type_combo.AppendItems(action_types)

        self.affList.SetObjects(self.read.getDetailedAffiliationInfo())

    def onActionTypeSelect(self, event):
        self.btnNewMethod.Enable(True)
        self.method_combo.Clear()
        self.method_combo.SetValue("Select Method")
        self.methods = [{i.MethodName:i.MethodID} for i in self.read.getMethods(type=event.GetString())]
        self.method_combo.SetItems([y for x in [i.keys() for i in self.methods] for y in x])
        #self.m_comboBox134.SetItems(methodTypes)
    
    def onNewMethod(self, event):
        dlg = CustomDialog(self, u'Create New Method')
        newMethodPanel = AddNewMethodPanelController(dlg, self.db)
        dlg.addPanel(newMethodPanel)
        newMethodPanel.setTypeFilter(str(self.action_type_combo.GetStringSelection()))
        if dlg.ShowModal() == wx.ID_OK:
            newMethod = newMethodPanel.method
            self.methods = [{i.MethodName: i.MethodID} for i in [newMethod]]
            self.method_combo.AppendItems([y for x in [i.keys() for i in self.methods] for y in x])
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
                action = Actions(
                    ActionTypeCV=self.actionType,
                    MethodID=self.methodID,
                    BeginDateTime=self.beginDT,
                    BeginDateTimeUTCOffset=self.beginDTUTC,
                )
                try:
                    action.EndDateTime = self.endDT,
                    action.EndDateTimeUTCOffset = self.endDTUTC,
                    action.ActionDescription = self.actionDesc,
                    action.ActionFileLink = self.actionLink
                except Exception as error:
                    print error

                action = write.createAction(action)

                self.actionID = action.ActionID
                
                for affID in self.affiliationList:
                    actionby = ActionBy(
                        ActionID=self.actionID,
                        AffiliationID=affID,
                        IsActionLead=(affID == self.actionLead)
                    )
                    write.createActionby(actionby)

                    self.parent.parent.list_ctrl.SetObjects(self.parent.parent.getSeriesData())
                    length = self.parent.parent.list_ctrl.GetItemCount.im_self.ItemCount
                    length = length - 1
                    self.parent.parent.list_ctrl.Focus(length)
                    self.parent.parent.list_ctrl.Select(length, 1)
                
            except Exception as error:
                print error

        event.Skip()

    def getFieldValues(self):

        keys = [y for x in [aff.keys() for aff in self.methods] for y in x]
        vals = [y for x in [aff.values() for aff in self.methods] for y in x]
        d = dict(zip(keys, vals))

#         self.ActionType = str(self.action_type_combo.GetStringSelection())
#         self.MethodID = d[str(self.method_combo.GetStringSelection())]
#         self.BeginDT = self._getTime(self.m_datePicker5, self.m_timePicker1)
#         self.BeginDTUTC = self.spinUTCBegin.GetValue()
#         self.AffiliationList = [i.affiliationID for i in self.affList.GetSelectedObjects()]
#
#         for i in self.affList.selected():
#             if self.affList.IsChecked(i):
#                 self.actionLead = i.affiliationID
# # =======
        self.actionType = str(self.action_type_combo.GetStringSelection())
        self.methodID = d[str(self.method_combo.GetStringSelection())]
        self.beginDT = self._getTime(self.dateBegin, self.m_timePicker1)
        self.beginDTUTC = self.spinUTCBegin.GetValue()
        self.affiliationList = [aff.AffiliationID for aff in self.affList.GetSelectedObjects()]

        for aff in self.affList.GetSelectedObjects():
            if self.affList.IsChecked(aff):
                self.actionLead = aff.AffiliationID
# >>>>>>> 302544e2537a81675971d89e1be2a758c65becd8
                break
        if self.m_datePicker51.GetValue().IsValid():
            self.endDT = self._getTime(self.m_datePicker51, self.m_timePicker2)
        else:
            self.EndDT = None
        self.EndDTUTC = self.beginDTUTC
        if str(self.m_textCtrl232.GetValue()) == '':
            self.actionDesc = None
        else:
            self.ActionDesc = str(self.m_textCtrl232.GetValue())
        if str(self.m_textCtrl234.GetValue()) == '':
            self.ActionLink = None
        else:
            self.ActionLink = str(self.m_textCtrl234.GetValue())

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
