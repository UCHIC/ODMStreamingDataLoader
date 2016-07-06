import wx

from datetime import datetime
import dateutil.parser as dparser


#TODO get rid of *


from src.wizard.controller.frmAddSpatialReference \
    import NewSpatialReferenceController
from src.wizard.view.clsCustomDialog import CustomDialog

from src.wizard.view.clsResultPage import ResultPageView
from odm2api.ODM2.models import TimeSeriesResults, Results, FeatureActions
import uuid


class ResultSummaryPanel(ResultPageView):
    def __init__( self, parent):
        super(ResultSummaryPanel, self).__init__(parent)
        self.Bind(wx.EVT_SHOW, self.onShow)
        self.parent = parent
        self.btnNewSR.Bind(wx.EVT_BUTTON, self.onCreateSpatialReference)
 
        self.fontColor = wx.Colour(67, 79, 112)
        self.populateFields()

    def getSeriesData(self):
        read = self.parent.database.getReadSession()
        return read.getResults()
    
    def onButtonAdd(self, event):
        event.Skip()
    
    def createResult(self):
        
        if not self.Validate():
            self.Refresh()
            return

        selections = self.parent.getSelections()
        
        samplingFeatureID = selections[0].SamplingFeatureID
        actionID = selections[4].ActionID

        write = self.parent.database.getWriteSession()
        fa =FeatureActions(SamplingFeatureID=samplingFeatureID, ActionID=actionID)
        featureAction = write.createFeatureAction(fa)

        featureActionID = featureAction.FeatureActionID

        variableID = selections[1].VariableID
        unitID = selections[2].UnitsID

        processingLevelID = selections[3].ProcessingLevelID

        valueCount = 1 # ???

        sampledMedium = str(self.comboSamp.GetStringSelection())
        
        resultTypeCV = "Time series coverage"

        statusCV = None
        if str(self.comboStatus.GetStringSelection()) != "":
            statusCV = str(self.comboStatus.GetStringSelection())

        validUTCOffset = None
        if self.spinUTCValid.GetValue() != 0:
            validUTCOffset = self.spinUTCValid.GetValue()

        validDT = None
        if self.dateValidDT.GetValue().IsValid():
            validDT = self._getTime(self.dateValidDT, self.timeValid)
        
        resultDT = None
        if self.datePickerResult.GetValue().IsValid():
            validDT = self._getTime(self.datePickerResult,
                self.timeResult)
        
        # TODO -- taxonomicclass
        keys = [y for x in [i.keys() for i in self.tax] for y in x]
        vals = [y for x in [i.values() for i in self.tax] for y in x]
        d = dict(zip(keys, vals))

        tax = None
        if str(self.comboTax.GetStringSelection()) != "":
            tax = d[self.comboTax.GetStringSelection()]
        print tax

        aggStat = str(self.comboAgg.GetStringSelection())

        x = None
        if float(self.txtX.GetValue()) != 0.0:
            x = float(self.txtX.GetValue())
        y = None
        if float(self.txtY.GetValue()) != 0.0:
            y = float(self.txtY.GetValue())
        z = None
        if float(self.txtZ.GetValue()) != 0.0:
            z = float(self.txtZ.GetValue())


        xUnit = None
        if str(self.comboXUnits.GetStringSelection()) != "":
            xUnit = str(self.comboXUnits.GetStringSelection())
        yUnit = None
        if str(self.comboYUnits.GetStringSelection()) != "":
            yUnit = str(self.comboYUnits.GetStringSelection())
        zUnit = None
        if str(self.comboZUnits.GetStringSelection()) != "":
            zUnit = str(self.comboZUnits.GetStringSelection())


        keys = [yy for xx in [i.keys() for i in self.sp_ref] for yy in xx]
        vals = [yy for xx in [i.values() for i in self.sp_ref] for yy in xx]
        d = dict(zip(keys, vals))

        sr = None
        if str(self.comboSR.GetStringSelection()) != "":
            sr = d[self.comboSR.GetStringSelection()]

        timeSpacing = None
        if str(self.txtIntended.GetValue()) != "":
            timeSpacing = float(self.txtIntended.GetValue())
        timeUnit = None
        if str(self.comboIntendedUnits.GetStringSelection()) != "":
            timeUnit = str(self.comboIntendedUnits.GetStringSelection())

        print "X", x
        print "Y", y
        print "Z", z
        tsr= TimeSeriesResults(ResultUUID = str(uuid.uuid4()),
                    FeatureActionID=featureActionID,
                   VariableID=variableID,
                   UnitsID=unitID,
                   ProcessingLevelID=processingLevelID,
                   ValueCount=valueCount,
                   SampledMediumCV=sampledMedium,
                   ResultTypeCV=resultTypeCV,
                   TaxonomicClassifierID=tax,
                   ResultDateTime=resultDT,
                   ResultDateTimeUTCOffset=validUTCOffset,
                   ValidDateTime=validDT,
                   ValidDateTimeUTCOffset=validUTCOffset,
                   StatusCV=statusCV,
                    AggregationStatisticCV=aggStat,
                    XLocation=x,
                    XLocationUnitsID=xUnit,
                    YLocation=y,
                    YLocationUnitsID=yUnit,
                    ZLocation=z,
                    ZLocationUnitsID=zUnit,
                    SpatialReferenceID=sr,
                    IntendedTimeSpacing=timeSpacing,
                    IntendedTimeSpacingUnitsID=timeUnit)
        result =  write.createResult(tsr)
        



        print result
        return result


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

    def onShow(self, event):
        if event.GetShow() is True:
            selections = self.parent.getSelections()
            
            self.getSamplingFeatureSummary(\
                selections[0])
            self.getVariablesSummary(\
                selections[1])
            self.getUnitsSummary(\
                selections[2])
            self.getProcessingLevelSummary(\
                selections[3])
            self.getActionsSummary(\
                selections[4])

        event.Skip()

    def populateFields(self):
        read = self.parent.database.getReadSession()

        self.mediums = {} #read.getCVMediumTypes()
        [self.mediums.update({obj.Name:obj}) \
            #for obj in read.getCVMediumTypes()]
            for obj in read.getCVs(type="Medium")]

        self.comboSamp.AppendItems(self.mediums.keys())

        self.aggStat = {} #read.getCVAggregationStatistics()
        [self.aggStat.update({obj.Name:obj}) \
         #   for obj in read.getCVAggregationStatistics()]
            for obj in read.getCVs(type="aggregationstatistic")]
        self.comboAgg.AppendItems(self.aggStat.keys())
        
        #status = read.getCVStatus();
        status = read.getCVs(type="Status")
        statusTerms = [obj.Term for obj in status]
        self.comboStatus.AppendItems(statusTerms)

        #timeUnits = read.getUnitsByTypeCV("length")
        timeUnits = read.getUnits(type="length")

        timeUnitsName = [obj.UnitsName for obj in timeUnits]
        self.comboXUnits.AppendItems(timeUnitsName)
        self.comboYUnits.AppendItems(timeUnitsName)
        self.comboZUnits.AppendItems(timeUnitsName)
        self.comboIntendedUnits.AppendItems(timeUnitsName)
        
        self.tax = [{i.TaxonomicClassifierName:i.TaxonomicClassifierID}\
            for i in read.getTaxonomicClassifiers()]
        self.comboTax.AppendItems(\
            [y for x in [i.keys() for i in self.tax] for y in x]
            )
        
        self.sp_ref = [{i.SRSName:i.SpatialReferenceID}\
            #for i in read.getCVSpacialReferenceTypes()]
            for i in read.getSpatialReferences()]
        self.comboSR.AppendItems(\
            [y for x in [i.keys() for i in self.sp_ref] for y in x]
            )

    def onCreateSpatialReference(self, event):
        dlg = CustomDialog(self, "New Spatial Reference")
        dlg.addPanel(NewSpatialReferenceController(dlg, self.parent.database))
        if dlg.ShowModal() == wx.ID_OK:
            read = self.parent.database.getReadSession()
            self.sp_ref = [{i.SRSName:i.SpatialReferenceID}\
                #for i in read.getCVSpacialReferenceTypes()]
                for i in read.getSpatialReferences()]
            self.comboSR.Clear()
            self.comboSR.AppendItems(\
                [y for x in [i.keys() for i in self.sp_ref] for y in x]
                )
        event.Skip()


    def getSamplingFeatureSummary(self, obj):
        self.txtSum.Freeze()
        
        self.txtSum.BeginBold()
        self.txtSum.BeginUnderline()
        self.txtSum.WriteText("Sampling Feature")
        self.txtSum.EndBold()
        self.txtSum.EndUnderline()
        self.txtSum.Newline()
       
        self.txtSum.WriteText("Code: ")
        self.txtSum.BeginItalic()
        self.txtSum.BeginTextColour(self.fontColor)
        self.txtSum.WriteText(str(obj.SamplingFeatureCode))
        self.txtSum.EndTextColour()
        self.txtSum.EndItalic()
        self.txtSum.Newline()

        self.txtSum.WriteText("Name: ")
        self.txtSum.BeginTextColour(self.fontColor)
        self.txtSum.BeginItalic()
        if not obj.SamplingFeatureName:
            self.txtSum.WriteText("--")
        else:
            self.txtSum.WriteText(str(obj.SamplingFeatureName))
        self.txtSum.EndTextColour()
        self.txtSum.EndItalic()
        self.txtSum.Newline()
        
        self.txtSum.WriteText("Type: ")
        self.txtSum.BeginItalic()
        self.txtSum.BeginTextColour(self.fontColor)
        if not obj.SamplingFeatureTypeCV:
            self.txtSum.WriteText("--")
        else:
            self.txtSum.WriteText(str(obj.SamplingFeatureTypeCV))
        self.txtSum.EndTextColour()
        self.txtSum.EndItalic()
        self.txtSum.Newline()
        
        self.txtSum.WriteText("Description: ")
        self.txtSum.BeginTextColour(self.fontColor)
        self.txtSum.BeginItalic()
        if not obj.SamplingFeatureDescription:
            self.txtSum.WriteText("--")
        else:
            self.txtSum.WriteText(str(obj.SamplingFeatureDescription))
        self.txtSum.EndItalic()
        self.txtSum.EndTextColour()
        self.txtSum.Newline()
        
        self.txtSum.WriteText("Geotype: ")
        self.txtSum.BeginTextColour(self.fontColor)
        self.txtSum.BeginItalic()
        if not obj.SamplingFeatureGeotypeCV:
            self.txtSum.WriteText("--")
        else:
            self.txtSum.WriteText(str(obj.SamplingFeatureGeotypeCV))
        self.txtSum.EndTextColour()
        self.txtSum.EndItalic()
        self.txtSum.Newline()
        
        self.txtSum.WriteText("Elevation: ")
        self.txtSum.BeginItalic()
        self.txtSum.BeginTextColour(self.fontColor)
        if not obj.Elevation_m:
            self.txtSum.WriteText("--")
        else:
            self.txtSum.WriteText(str(obj.Elevation_m) + " meters")
        self.txtSum.EndItalic()
        self.txtSum.EndTextColour()
        self.txtSum.Newline()
        
        self.txtSum.Thaw()
    
    def getVariablesSummary(self, obj):
        self.txtSum.Freeze()
        
        self.txtSum.BeginBold()
        self.txtSum.BeginUnderline()
        self.txtSum.WriteText("Variable")
        self.txtSum.EndBold()
        self.txtSum.EndUnderline()
        self.txtSum.Newline()
       
        self.txtSum.WriteText("Code: ")
        self.txtSum.BeginItalic()
        self.txtSum.BeginTextColour(self.fontColor)
        self.txtSum.WriteText(str(obj.VariableCode))
        self.txtSum.EndTextColour()
        self.txtSum.EndItalic()
        self.txtSum.Newline()

        self.txtSum.WriteText("Name: ")
        self.txtSum.BeginTextColour(self.fontColor)
        self.txtSum.BeginItalic()
        if not obj.VariableNameCV:
            self.txtSum.WriteText("--")
        else:
            self.txtSum.WriteText(str(obj.VariableNameCV))
        self.txtSum.EndTextColour()
        self.txtSum.EndItalic()
        self.txtSum.Newline()
        
        self.txtSum.WriteText("Type: ")
        self.txtSum.BeginItalic()
        self.txtSum.BeginTextColour(self.fontColor)
        if not obj.VariableTypeCV:
            self.txtSum.WriteText("--")
        else:
            self.txtSum.WriteText(str(obj.VariableTypeCV))
        self.txtSum.EndTextColour()
        self.txtSum.EndItalic()
        self.txtSum.Newline()
        
        self.txtSum.WriteText("Definition: ")
        self.txtSum.BeginTextColour(self.fontColor)
        self.txtSum.BeginItalic()
        if not obj.VariableDefinition:
            self.txtSum.WriteText("--")
        else:
            self.txtSum.WriteText(str(obj.VariableDefinition))
        self.txtSum.EndItalic()
        self.txtSum.EndTextColour()
        self.txtSum.Newline()
        
        self.txtSum.Thaw()
        
    def getUnitsSummary(self, obj):
        self.txtSum.Freeze()
        
        self.txtSum.BeginBold()
        self.txtSum.BeginUnderline()
        self.txtSum.WriteText("Unit")
        self.txtSum.EndBold()
        self.txtSum.EndUnderline()
        self.txtSum.Newline()
       
        self.txtSum.WriteText("Abbreviation: ")
        self.txtSum.BeginItalic()
        self.txtSum.BeginTextColour(self.fontColor)
        self.txtSum.WriteText(str(obj.UnitsAbbreviation))
        self.txtSum.EndTextColour()
        self.txtSum.EndItalic()
        self.txtSum.Newline()

        self.txtSum.WriteText("Name: ")
        self.txtSum.BeginTextColour(self.fontColor)
        self.txtSum.BeginItalic()
        if not obj.UnitsName:
            self.txtSum.WriteText("--")
        else:
            self.txtSum.WriteText(str(obj.UnitsName))
        self.txtSum.EndTextColour()
        self.txtSum.EndItalic()
        self.txtSum.Newline()
        
        self.txtSum.WriteText("Type: ")
        self.txtSum.BeginItalic()
        self.txtSum.BeginTextColour(self.fontColor)
        if not obj.UnitsTypeCV:
            self.txtSum.WriteText("--")
        else:
            self.txtSum.WriteText(str(obj.UnitsTypeCV))
        self.txtSum.EndTextColour()
        self.txtSum.EndItalic()
        self.txtSum.Newline()
        
        self.txtSum.WriteText("Link: ")
        self.txtSum.BeginTextColour(self.fontColor)
        self.txtSum.BeginItalic()
        if not obj.UnitsLink:
            self.txtSum.WriteText("--")
        else:
            self.txtSum.BeginURL(obj.UnitsLink)
            self.txtSum.WriteText(str(obj.UnitsLink))
            self.txtSum.EndURL()
        self.txtSum.EndItalic()
        self.txtSum.EndTextColour()
        self.txtSum.Newline()
        
        self.txtSum.Thaw()
    
    def getProcessingLevelSummary(self, obj):
        self.txtSum.Freeze()
        
        self.txtSum.BeginBold()
        self.txtSum.BeginUnderline()
        self.txtSum.WriteText("Processing Level")
        self.txtSum.EndBold()
        self.txtSum.EndUnderline()
        self.txtSum.Newline()
       
        self.txtSum.WriteText("Code: ")
        self.txtSum.BeginItalic()
        self.txtSum.BeginTextColour(self.fontColor)
        self.txtSum.WriteText(str(obj.ProcessingLevelCode))
        self.txtSum.EndTextColour()
        self.txtSum.EndItalic()
        self.txtSum.Newline()

        self.txtSum.WriteText("Definition: ")
        self.txtSum.BeginTextColour(self.fontColor)
        self.txtSum.BeginItalic()
        if not obj.Definition:
            self.txtSum.WriteText("--")
        else:
            self.txtSum.WriteText(str(obj.Definition))
        self.txtSum.EndTextColour()
        self.txtSum.EndItalic()
        self.txtSum.Newline()
        
        self.txtSum.WriteText("Explanation: ")
        self.txtSum.BeginItalic()
        self.txtSum.BeginTextColour(self.fontColor)
        if not obj.Explanation:
            self.txtSum.WriteText("--")
        else:
            self.txtSum.WriteText(str(obj.Explanation))
        self.txtSum.EndTextColour()
        self.txtSum.EndItalic()
        self.txtSum.Newline()
        
        self.txtSum.Thaw()
    
    def getActionsSummary(self, obj):
        self.txtSum.Freeze()
        
        self.txtSum.BeginBold()
        self.txtSum.BeginUnderline()
        self.txtSum.WriteText("Action")
        self.txtSum.EndBold()
        self.txtSum.EndUnderline()
        self.txtSum.Newline()
       
        self.txtSum.WriteText("ID: ")
        self.txtSum.BeginItalic()
        self.txtSum.BeginTextColour(self.fontColor)
        self.txtSum.WriteText(str(obj.ActionID))
        self.txtSum.EndTextColour()
        self.txtSum.EndItalic()
        self.txtSum.Newline()

        self.txtSum.WriteText("Type: ")
        self.txtSum.BeginTextColour(self.fontColor)
        self.txtSum.BeginItalic()
        if not obj.ActionTypeCV:
            self.txtSum.WriteText("--")
        else:
            self.txtSum.WriteText(str(obj.ActionTypeCV))
        self.txtSum.EndTextColour()
        self.txtSum.EndItalic()
        self.txtSum.Newline()
        
        self.txtSum.WriteText("Description: ")
        self.txtSum.BeginItalic()
        self.txtSum.BeginTextColour(self.fontColor)
        if not obj.ActionDescription:
            self.txtSum.WriteText("--")
        else:
            self.txtSum.WriteText(str(obj.ActionDescription))
        self.txtSum.EndTextColour()
        self.txtSum.EndItalic()
        self.txtSum.Newline()
        
        self.txtSum.WriteText("Method ID: ")
        self.txtSum.BeginTextColour(self.fontColor)
        self.txtSum.BeginItalic()
        if not obj.MethodID:
            self.txtSum.WriteText("--")
        else:
            self.txtSum.WriteText(str(obj.MethodID))
        self.txtSum.EndItalic()
        self.txtSum.EndTextColour()
        self.txtSum.Newline()
        
        self.txtSum.WriteText("Begin Time: ")
        self.txtSum.BeginTextColour(self.fontColor)
        self.txtSum.BeginItalic()
        if not obj.BeginDateTime:
            self.txtSum.WriteText("--")
        else:
            self.txtSum.WriteText(str(obj.BeginDateTime) + " (UTC Offset " + str(obj.BeginDateTimeUTCOffset) + ")")
        self.txtSum.EndTextColour()
        self.txtSum.EndItalic()
        self.txtSum.Newline()
        
        self.txtSum.WriteText("End Time: ")
        self.txtSum.BeginItalic()
        self.txtSum.BeginTextColour(self.fontColor)
        if not obj.EndDateTime:
            self.txtSum.WriteText("--")
        else:
            self.txtSum.WriteText(str(obj.EndDateTime) + " (UTC Offset " + str(obj.EndDateTimeUTCOffset) + ")")
        self.txtSum.EndItalic()
        self.txtSum.EndTextColour()
        self.txtSum.Newline()
        
        self.txtSum.Thaw()
