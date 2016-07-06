
import wx

from src.wizard.controller.frmFileConfigPanel import FileConfigPanelController
from src.wizard.controller.frmDataConfigPanel import DataConfigPanelController
from src.wizard.controller.frmDatabaseConfigPanel import DatabaseConfigPanel

class ChainedDialog(wx.Dialog):
    def __init__(self, data={}, *args, **kwargs):
        super(ChainedDialog, self).__init__(*args, **kwargs)
        # Set this extra style for validation to work.
        self.SetExtraStyle(wx.WS_EX_VALIDATE_RECURSIVELY)
        # Declare the sizers.
        self.mainSizer = wx.BoxSizer(wx.VERTICAL)
        self.panelSizer = wx.BoxSizer(wx.VERTICAL)
        self.buttonSizer = wx.BoxSizer(wx.HORIZONTAL)
        # panelList holds all of the panels for this
        # custom wizard.
        self.panelList = []
        # currentPanel defines which panel that the
        # user is currently on.
        self.currentPanel = 0
        # data is a dictionary of attributes
        # which are passed from one panel to
        # another in order to create a mapping.
        # The default value is an empty dictionary.
        self.data = data
        # Add the buttons.
        self.addButtons()
        # Define and add the panels.
        self.setPanels()
        # Display the current panel.
        self.panelList[self.currentPanel].Show()
        # Resize the page to fit the contents.
        self.mainSizer.Fit(self)
        # Pass any incoming data to the first panel.
        # E.g. if this custom wizard is being used
        # to edit a mapping that already exists.
        self.panelList[self.currentPanel].setInput(data=self.data)

    def addButtons(self):
        # Add the buttons, which will appear on each page.
        self.cancelButton = wx.Button(self, label="Cancel")
        self.cancelButton.Bind(wx.EVT_BUTTON, self.onClose)
        self.buttonSizer.Add(self.cancelButton, 0,
            wx.ALL| wx.EXPAND | wx.ALIGN_RIGHT, 10)
        self.prevButton = wx.Button(self, label="< Back")
        self.prevButton.Bind(wx.EVT_BUTTON, self.onPrev)
        self.buttonSizer.Add(self.prevButton, 0,
            wx.ALL| wx.EXPAND | wx.ALIGN_RIGHT, 10)
        self.nextButton = wx.Button(self, label="Next >")
        self.nextButton.Bind(wx.EVT_BUTTON, self.onNext)
        self.buttonSizer.Add(self.nextButton, 0,
            wx.ALL| wx.EXPAND | wx.ALIGN_RIGHT, 10)
        # Add the buttons and sizers to the main sizer.
        self.mainSizer.Add(self.panelSizer, 1, wx.EXPAND, 10)
        self.mainSizer.Add(self.buttonSizer, 0, wx.ALIGN_RIGHT, 10)
        self.SetSizer(self.mainSizer)
        # Disable the 'back' button.
        self.prevButton.Enable(False)
    
    def setPanels(self):
        # Declare each panel to be added to this custom
        # wizard.
        filePanel = FileConfigPanelController(self)
        dataPanel = DataConfigPanelController(self)
        #dbPanel = pnlDBConfig(self, None)
        dbPanel = DatabaseConfigPanel(self)
        # Add each of them to the appropriate sizer.
        self.panelSizer.Add(filePanel)
        self.panelSizer.Add(dataPanel)
        self.panelSizer.Add(dbPanel)
        # Hide them all for now.
        filePanel.Hide()
        dataPanel.Hide()
        dbPanel.Hide()
        # Add each one to the internal list of panels
        # in order to keep track of which one the user
        # is currently on.
        self.panelList.append(dbPanel)
        self.panelList.append(filePanel)
        self.panelList.append(dataPanel)


    def run(self):
        '''
            This is where the modal dialog will sit
            until the call to EndModal() is made.
        '''
        returnValue = self.ShowModal()
        if returnValue == wx.ID_OK:
            # Completed successfully, return the data.
            return self.data
        # User quit early, return None.
        return None

    def buttonCheck(self):
        if self.currentPanel == len(self.panelList)-1:
            self.nextButton.SetLabel("Finish")
        else:
            self.panelList[self.currentPanel+1]
            self.nextButton.SetLabel("Next >")

        if self.currentPanel == 0:
            self.prevButton.Enable(False)
        else: 
            self.prevButton.Enable(True)
            
    def onClose(self, event):
        self.EndModal(-1)

    def onPrev(self, event):
        if self.currentPanel-1 >= 0:
            self.panelList[self.currentPanel].Hide()
            self.panelList[self.currentPanel-1].Show()
            self.currentPanel -= 1
            self.mainSizer.Fit(self)
            self.buttonCheck()
        event.Skip()

    def onNext(self, event):
        # OK to move to the next panel.
        if self.currentPanel+1 <= len(self.panelList)-1:
            if not self.panelList[self.currentPanel].Validate():
                event.Skip()
                return
            try:
                self.panelList[self.currentPanel+1].setInput(data=self.panelList[self.currentPanel].getInput())
            except TypeError as e:
                event.Skip()
                print ( "error going to next page %s"% e)
                return#
                #error_dlg = wx.MessageBox('This data does not look valid. Check to see if the configuration options match the data file.\n\nDo you want to continue anyway?', 'Data Load Error', wx.YES_NO | wx.NO_DEFAULT | wx.ICON_QUESTION)
                #if error_dlg == wx.NO:
                #    print "no"
                #    event.Skip()
                #    return

            self.panelList[self.currentPanel].Hide()
            self.panelList[self.currentPanel+1].Show()
            #self.panelList[self.currentPanel+1].setInput(\
            #    self.panelList[self.currentPanel].getInput())
            self.currentPanel += 1
            self.mainSizer.Fit(self)
            self.buttonCheck()
        else: 
            for panel in self.panelList:
                self.data.update(panel.getInput())
                panel.Destroy()
            self.EndModal(wx.ID_OK)

        event.Skip()

if __name__ == '__main__':
    app = wx.App(False)
    myWizard = ChainedDialog(parent=None, title="Wizard",
                             size=wx.DefaultSize,
                             style=wx.DEFAULT_DIALOG_STYLE)
    myWizard.Show()
    app.MainLoop()
