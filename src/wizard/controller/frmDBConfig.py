"""Subclass of clsDBConfiguration, which is generated by wxFormBuilder."""

import wx
from sqlalchemy.exc import DBAPIError

from src.wizard.view.clsDBConfig import clsDBConfiguration
from api.ODMconnection import dbconnection
from src.common.functions import searchDict


class frmDBConfig(wx.Dialog):
    def __init__(self, parent, service_manager, is_main=False):
        wx.Dialog.__init__(self, parent, title=u'Database Configuration',
                           style=wx.DEFAULT_DIALOG_STYLE, size=wx.Size(500, 315))
        self.panel = pnlDBConfig(self, None, is_main)
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.sizer.AddWindow(self.panel, 1, border=1, flag=wx.EXPAND | wx.GROW | wx.ALL)
        self.SetSizer(self.sizer)
        self.sizer.Fit(self.panel)

# Implementing clsDBConfiguration
class pnlDBConfig(clsDBConfiguration):
    def __init__(self, parent,  is_main=False):
        clsDBConfiguration.__init__(self, parent)

        self.choices = {"Microsoft SQL Server": 'mssql', "MySQL": 'mysql', "PostgreSQL":"postgresql", "SQLite":"sqlite"}
        self.cbDatabaseType.AppendItems(self.choices.keys())

        self.parent = parent
        self.is_main = is_main

        self.inputDict = {}
        
    def getInput(self):
        self.inputDict.update(self.getFieldValues())
        return self.inputDict

    def populate(self, data={}):
        print "data.... ", data
        if data:
            choices = {'mssql': 2, "mysql": 3, "postgresql": 1, "sqlite": 0}
            self.cbDatabaseType.SetSelection(choices[searchDict(data, 'Engine')])
            self.txtUser.SetValue(searchDict(data, 'UserName'))
            self.txtPass.SetValue(searchDict(data, 'Password'))
            self.txtServer.SetValue(searchDict(data, 'Address'))
            self.txtDBName.SetValue(searchDict(data, 'DatabaseName'))
            self.inputDict = data        

    def OnValueChanged(self, event):
        """

        :param event:
        :return:
        """

        self.btnSave.Enable(False)

        try:
            curr_dict = self.getFieldValues()
            if self.conn_dict == curr_dict:
                self.btnSave.Enable(True)
        except:
            pass

    # Handlers for clsDBConfiguration events.
    def OnBtnTest(self, event):
        conn_dict = self.getFieldValues()
        if self.validateInput(conn_dict['Database']):
            self.btnSave.Enable(True)
            self.conn_dict = conn_dict

    def OnBtnSave(self, event):
        self.parent.EndModal(wx.ID_OK)

    def OnBtnCancel(self, event):
        self.parent.SetReturnCode(wx.ID_CANCEL)
        self.parent.EndModal(wx.ID_CANCEL)

    def validateInput(self, conn_dict):
        message = ""

        '''Check that everything has been filled out'''
        if not all(x for x in conn_dict.values()):
            message = "Please complete every field in order to proceed"
            wx.MessageBox(message, 'Database Connection', wx.OK | wx.ICON_EXCLAMATION)
            return False

        try:
            conn = dbconnection.createConnection(conn_dict['Engine'], conn_dict['Address'], conn_dict["DatabaseName"], conn_dict['UserName'], conn_dict["Password"], 2.0)
            if conn:
                message = "This connection is valid"
                wx.MessageBox(message, 'Test Connection', wx.OK)
            else:
                #TODO add error message if user cannont connect to the database ( not using VPN) but the db is still 1.1.1)

                message = "This connection is not valid Database"

                wx.MessageBox(message, 'Error Occurred', wx.OK | wx.ICON_ERROR)
                return False
        except Exception as e:
            print (e)
            wx.MessageBox("This connection is invalid", 'Error Occurred', wx.ICON_ERROR | wx.OK)
            return False
            # wx.MessageBox(e.message, 'Error Occurred', wx.ICON_ERROR | wx.OK)

        return True

    # Returns a dictionary of the database values entered in the form
    def getFieldValues(self):
        conn_dict = {}

        conn_dict['Engine'] = self.choices[self.cbDatabaseType.GetValue()] if self.cbDatabaseType.GetValue() != ''  else ''
        conn_dict['UserName'] = self.txtUser.GetValue()
        conn_dict['Password'] = self.txtPass.GetValue()
        conn_dict['Address'] = self.txtServer.GetValue()
        conn_dict['DatabaseName'] = self.txtDBName.GetValue()

        return {'Database': conn_dict}

