
import wx
import uuid
# TODO 
# Clean these up.
from odm2api.ODM2.services.createService import *
from odm2api.ODM2.models import SamplingFeatures, Sites

from src.wizard.view.clsAddNewSampFeatPanel import AddNewSampFeatPanelView
#from src.wizard.view.clsAddSpatialReferences import NewSpatialReferenceView
from src.wizard.controller.frmAddSpatialReference import NewSpatialReferenceController
from src.wizard.view.clsCustomDialog import CustomDialog

class AddNewSampFeatPanelController(AddNewSampFeatPanelView):
    def __init__(self, daddy, db, **kwargs):
        super(AddNewSampFeatPanelController, self).__init__(daddy,
            **kwargs)
        self.parent = daddy
        self.db = db
        
        self.m_button411.Bind(wx.EVT_BUTTON, self.onCreateSpatialReference)

        self.populateFields()
        

    def populateFields(self):
        read = self.db.getReadSession()
        
        self._uuid = uuid.uuid4()
        self.m_textCtrl30.SetValue(unicode(self._uuid))
        
        #cv_names = [i.Name for i in read.getCVSamplingFeatureTypes()]
        self.m_textCtrl30.SetValue('Site')
        
        # self.sites = [i.Name for i in read.getCVSiteTypes()]
        self.sites = [i.Name for i in read.getCVs(type='Site Type')]
        self.m_comboBox8.AppendItems(self.sites)
        
        self.sp_ref = [{i.SRSName:i.SpatialReferenceID}\
            # for i in read.getCVSpacialReferenceTypes()]
            for i in read.getSpatialReferences()]
        self.m_comboBox822.AppendItems(\
            [y for x in [i.keys() for i in self.sp_ref] for y in x]
            )
        
        #geo = [i.Name for i in read.getCVSamplingFeatureGeoTypes()]
        self.m_geotypeTxt.SetValue('Point')
        
        # self.datum = [i.Name for i in read.getCVElevationDatums()]
        self.datum = [i.Name for i in read.getCVs(type="Elevation Datum")]
        self.m_comboBox8211.AppendItems(self.datum)

    def onCreateSpatialReference(self, event):
        dlg = CustomDialog(self, "New Spatial Reference")
        dlg.addPanel(NewSpatialReferenceController(dlg, self.db))
        if dlg.ShowModal() == wx.ID_OK:
            read = self.db.getReadSession()
            self.sp_ref = [{i.SRSName:i.SpatialReferenceID}\
                # for i in read.getCVSpacialReferenceTypes()]
                for i in read.getSpatialReferences()]
            self.m_comboBox822.Clear()
            self.m_comboBox822.AppendItems(\
                [y for x in [i.keys() for i in self.sp_ref] for y in x]
                )
        event.Skip()
        

    def onOK(self, event):
        # Event handler for when the user clicks OK.
        
        # Try to validate the form.
        if not self.Validate():
            self.Refresh()
            return
        else:
            # Move the data into the value dictionaries.
            # All data should be valid at this point.
            self.getFieldValues() 
            try:
                # Create the variable in the database.
                write = self.db.getWriteSession()
                # sf= SamplingFeatures(\


                site = Sites(SamplingFeatureUUID=str(self._uuid),
                            SamplingFeatureCode=self.requiredValues['code'],
                            SamplingFeatureTypeCV=self.requiredValues['vType'],
                            SamplingFeatureName=self.optionalValues['name'],
                            SamplingFeatureDescription=self.optionalValues['desc'],
                            SamplingFeatureGeotypeCV=self.optionalValues['geoType'],
                            Elevation_m=self.optionalValues['elevation'],
                            ElevationDatumCV=self.optionalValues['elevationDatum'],
                            FeatureGeometry=self.optionalValues['featureGeo'],
                            SpatialReferenceID=self.requiredValues['spatialRef'],
                            SiteTypeCV=self.requiredValues['siteType'],
                            Latitude=self.requiredValues['lat'],
                            Longitude=self.requiredValues['long'])
                # site = write.createSite(site)
                self.sf = write.createSamplingFeature(site)


            except Exception as e:
                print e
        event.Skip()

    def getFieldValues(self):
        # Stores all of the required field values.
        # Default is None.
        self.requiredValues = {'uuid':'', # Required
                  'code':None, # Required
                  'vType':'Site',# Required
                  'spatialRef':None,# Required
                  'lat':None, # Required
                  'long':None,# Required
                  'siteType':None
                  }
        self.optionalValues = {
                  'name':None, 
                  'desc':None,
                  'geoType':'POINT',
                  'elevation':None,
                  'elevationDatum':None,
                  'featureGeo':None,
                  }
        
        self.requiredValues['uuid'] = str(uuid.uuid4())
        self.requiredValues['code'] = str(self.m_textCtrl301.GetValue())
        
        keys = [y for x in [i.keys() for i in self.sp_ref] for y in x]
        vals = [y for x in [i.values() for i in self.sp_ref] for y in x]
        d = dict(zip(keys, vals))

        self.requiredValues['spatialRef'] = \
            d[self.m_comboBox822.GetStringSelection()]
        self.requiredValues['lat'] = float(self.m_textCtrl35.GetValue())
        self.requiredValues['long'] = float(self.m_textCtrl36.GetValue())
        if self.m_comboBox8211.GetStringSelection() != '':
            self.optionalValues['elevationDatum'] = \
                str(self.datum[self.m_comboBox8211.GetSelection()])
        
        self.requiredValues['siteType'] = \
            str(self.m_comboBox8.GetStringSelection())
        
        if str(self.m_textCtrl302.GetValue()) != '':
            self.optionalValues['name'] = str(self.m_textCtrl302.GetValue())
        if str(self.m_textCtrl3022.GetValue()) != '':
            self.optionalValues['elevation'] = str(self.m_textCtrl3022.GetValue())
       
        if str(self.m_comboBox8211.GetStringSelection()) != '':
            self.optionalValues['elevationDatum'] = str(self.m_comboBox8211.GetStringSelection())
        if str(self.m_textCtrl303.GetValue()) != '':
            self.optionalValues['desc'] = str(self.m_textCtrl303.GetValue())
