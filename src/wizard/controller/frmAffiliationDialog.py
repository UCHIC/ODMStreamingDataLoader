import wx

from src.wizard.view.clsCustomDialog \
    import CustomDialog
from odm2api.ODM2.models import People

class AffiliationDialog(CustomDialog):
    def __init__(self, parent, title):
        super(AffiliationDialog, self).__init__(\
            title=title,
            parent=parent)
        
        self.parent = parent

    def initControls(self):
        self.view.m_sdbSizer10OK.Bind(wx.EVT_BUTTON, self.onOK)

        read = self.parent.db.getReadSession()
        
        people = read.getPeople()
        self.people = {}
        [self.people.update({p.PersonFirstName + " " + p.PersonLastName:p.PersonID})\
            for p in people]
        
        if not self.people:
            self.view.m_comboBox13.Enable(False)
        else:
            self.view.m_comboBox13.AppendItems(self.people.keys())

        orgs = read.getOrganizations()
        self.org = {}
        [self.org.update({o.OrganizationName:o.OrganizationID}) \
            for o in orgs]
        
        if not self.org:
            self.view.m_comboBox131.Enable(False)
        else:
            self.view.m_comboBox131.AppendItems(self.org.keys())
        
        orgTypes = [org.Name for org in read.getCVs(type="Organization Type")]
        self.view.orgTypeCombo.AppendItems(orgTypes)

        self.view.comboParent.AppendItems(self.org.keys())

    def onOK(self, event):
        # Try to validate the form.
        if not self.Validate():
            print "not valid"
            self.Refresh()
            return
 
        write = self.parent.db.getWriteSession()

        if self.view.m_comboBox13.GetStringSelection() == "":
            firstName = None
            lastName = None
            middleName = None

            ppl=People(PersonFirstName=firstName,
                PersonLastName=lastName,
                PersonMiddleName=middleName)
            person = write.createPerson(ppl)
        else:
            personID = self.people[self.view.m_comboBox13.GetStringSelection()]
            print personID

        if self.view.m_comboBox131.GetStringSelection() == "":
            pass
        else:
            organizationID = self.org[self.view.m_comboBox131.GetStringSelection()]
            print organizationID

        event.Skip()
