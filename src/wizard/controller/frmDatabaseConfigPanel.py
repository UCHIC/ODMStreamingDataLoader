import wx
from sqlalchemy.exc import DBAPIError
from collections import namedtuple

from src.wizard.view.clsDBConfig import clsDBConfiguration
from odm2api.ODMconnection import dbconnection
from src.common.functions import searchDict

from src.wizard.controller.frmChainedDialogPage import ChainedDialogPage
from src.controllers.Database import Database

class DatabaseConfigPanel(ChainedDialogPage,
    clsDBConfiguration):
    
    def __init__(self, parent):
        # First call each parent class's constructor.
        clsDBConfiguration.__init__(self, parent)
        ChainedDialogPage.__init__(self)
        self.parent = parent
        self.parent.nextButton.Enable(False)
    
    def getInput(self):
        # Implementing getInput from ChainedDialogPage.
        self.inputDict.update(self.getFieldValues())
        return self.inputDict

    def setInput(self, data):
        # Implementing setInput from ChainedDialogPage.
        self.choices = {"Microsoft SQL Server": 'mssql', "MySQL": 'mysql', "PostgreSQL":"postgresql", "SQLite":"sqlite"}
        self.cbDatabaseType.AppendItems(self.choices.keys())
        if data:
            choices = {'mssql': 2, "mysql": 3, "postgresql": 1, "sqlite": 0}
            self.cbDatabaseType.SetSelection(choices[searchDict(data, 'Engine')])
            self.txtUser.SetValue(searchDict(data, 'UserName'))
            self.txtPass.SetValue(searchDict(data, 'Password'))
            self.txtServer.SetValue(searchDict(data, 'Address'))
            self.txtDBName.SetValue(searchDict(data, 'DatabaseName'))
            self.inputDict = data        

    def onTestConnection(self, event):
        conn_dict = self.getFieldValues()
        if self.validateInput(conn_dict['Database']):
            self.conn_dict = conn_dict
            self.parent.nextButton.Enable(True) 
        else:
            self.parent.nextButton.Enable(False)

    def sanitizeFieldValues(self, value):
        value = value.replace(';','')
        return value

    def getFieldValues(self):
        conn_dict = {}
        conn_dict['Engine'] = self.choices[self.cbDatabaseType.GetValue()] if self.cbDatabaseType.GetValue() != ''  else ''
        conn_dict['UserName'] = self.sanitizeFieldValues(str(self.txtUser.GetValue()))
        conn_dict['Password'] = self.sanitizeFieldValues(str(self.txtPass.GetValue()))
        conn_dict['Address'] = self.sanitizeFieldValues(str(self.txtServer.GetValue()))
        conn_dict['DatabaseName'] = self.sanitizeFieldValues(str(self.txtDBName.GetValue()))
        return {'Database': conn_dict}

    def validateInput(self, conn_dict):
        message = "Invalid connection!"
        title = "Connection Error"
        ico = wx.ICON_EXCLAMATION
        connected = False
        # First check if all of the fields are completed.
        if not all(x for x in conn_dict.values()):
            message = "Please complete every field in order to proceed."
            wx.MessageBox(message=message,
                caption=title,
                style=wx.OK|ico)
            return False
        
        Credentials = namedtuple('Credentials',
            'engine host db_name uid pwd')

        cred = Credentials(conn_dict['Engine'],
            conn_dict['Address'],
            conn_dict['DatabaseName'],
            conn_dict['UserName'],
            conn_dict['Password'])
        
        self.dbConnection = Database()
        
        if self.dbConnection.createConnection(cred):
            message = "This connection is valid."
            ico = wx.OK|wx.ICON_INFORMATION
            title = "Connection Successfull"
            connected = True
            self.parent.db = self.dbConnection
            self.parent.nextButton.SetFocus()
        else:
            connected = False

        wx.MessageBox(message=message,
            caption=title,
            style=ico)
        return connected


