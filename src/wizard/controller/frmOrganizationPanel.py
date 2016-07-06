import wx

from src.wizard.view.clsOrganizationPanel\
    import OrganizationPanelView

from src.wizard.controller.frmRequiredValidator \
    import RequiredValidator
from src.wizard.controller.frmRequiredComboValidator \
    import RequiredComboValidator
from odm2api.ODM2.models import Organizations


class OrganizationPanel(OrganizationPanelView):
    def __init__(self, parent):
        super(OrganizationPanel, self).__init__(parent)
        self.parent = parent
        self.Bind(wx.EVT_SHOW, self.onShow)
        self.checkIgnore.Bind(wx.EVT_CHECKBOX, self.onCheck)

        self.m_comboBox131.Bind(wx.EVT_COMBOBOX, self.onPreOrg)

        read = self.parent.database.getReadSession()

        orgs = read.getOrganizations()
        self.org = {}
        [self.org.update({o.OrganizationName:o.OrganizationID}) \
            for o in orgs]
    
        if not self.org:
            self.m_comboBox131.Enable(False)
        else:
            self.m_comboBox131.AppendItems(self.org.keys())
    
        # orgTypes = [org.Name for org in read.getCVOrganizationTypes()]
        orgTypes = [org.Name for org in read.getCVs(type="Organization Type")]
        self.orgTypeCombo.AppendItems(orgTypes)

        self.comboParent.AppendItems(self.org.keys())
   
    def onCheck(self, event):
        if event.IsChecked():
            for child in self.sbSizer221.GetStaticBox().GetChildren():
                try:
                    if not isinstance(child, wx.StaticText):
                        child.Enable(False)
                except Exception as e:
                    pass
            self.orgID = None
            self.orgName = ""
            self.orgTypeCombo.SetValidator(wx.DefaultValidator)
            self.textCode.SetValidator(wx.DefaultValidator)
            self.textName.SetValidator(wx.DefaultValidator)
        else:
            self.orgTypeCombo.SetValidator(RequiredComboValidator())
            self.textCode.SetValidator(RequiredValidator())
            self.textName.SetValidator(RequiredValidator())
            for widget in self.sbSizer221.GetStaticBox().GetChildren():
                try:
                    widget.Enable(True)
                except Exception:
                    pass
        event.Skip()

    def getData(self):
        if not self.checkIgnore.GetValue():
            if str(self.m_comboBox131.GetStringSelection()) == "":
                
                orgType = str(self.orgTypeCombo.GetStringSelection())
                orgCode = str(self.textCode.GetValue())
                orgName = str(self.textName.GetValue())
                orgDesc = None
                if str(self.textDesc.GetValue()) != "":
                    orgDesc = str(self.textDesc.GetValue())
                orgLink = None
                if str(self.textLink.GetValue()) != "":
                    orgLink = str(self.textLink.GetValue())
                orgParent = None
                if str(self.comboParent.GetStringSelection()) != "":
                    orgParent = self.org[self.comboParent.GetStringSelection()]


                write = self.parent.database.getWriteSession()
                org= Organizations(OrganizationTypeCV=orgType,
                    OrganizationCode=orgCode,
                    OrganizationName=orgName,
                    OrganizationDescription=orgDesc,
                    OrganizationLink=orgLink,
                    ParentOrganizationID=orgParent)
                org = write.createOrganization(org)

                self.orgID = org.OrganizationID
                self.orgName = orgName

        return dict({"Organization":{"Name":self.orgName, "ID":self.orgID}})
    
    def onPreOrg(self, event):
        self.orgTypeCombo.SetValidator(wx.DefaultValidator)
        self.textCode.SetValidator(wx.DefaultValidator)
        self.textName.SetValidator(wx.DefaultValidator)
        self.orgID = self.org[self.m_comboBox131.GetStringSelection()]
        self.orgName = str(self.m_comboBox131.GetStringSelection())
        event.Skip()

    def onShow(self, event):
        self.parent.btnNext.Enable(True)
        event.Skip()
  
    def enable(self, event):
        self.parent.btnNext.Enable(True)
        event.Skip()
    
    def disable(self, event):
        self.parent.btnNext.Enable(False)
        event.Skip()

