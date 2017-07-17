import sys
import wx
#import wx.lib.agw.ultimatelistctrl as ULC
from ObjectListView import ObjectListView, ColumnDefn
import wx.lib.mixins.gridlabelrenderer as glr
from src.wizard.controller.frmVirtualList import VirtualList
from src.wizard.controller.frmVirtualGrid import VirtualGrid, GridBase
#from lib.ObjectListView.ObjectListView import VirtualObjectListView


class MyGrid(VirtualGrid, glr.GridWithLabelRenderersMixin):
    def __init__(self, *args, **kw):
        VirtualGrid.__init__(self, *args, **kw)
        glr.GridWithLabelRenderersMixin.__init__(self)

class MyColLabelRenderer(glr.GridLabelRenderer):
    def __init__(self, bgcolor):
        self._bgcolor = bgcolor
        
    def Draw(self, grid, dc, rect, col):
        dc.SetBrush(wx.Brush(self._bgcolor))
        dc.SetPen(wx.TRANSPARENT_PEN)
        dc.DrawRectangleRect(rect)
        hAlign, vAlign = grid.GetColLabelAlignment()
        text = grid.GetColLabelValue(col)
        self.DrawBorder(grid, dc, rect)
        self.DrawText(grid, dc, rect, text, hAlign, vAlign)

class DataConfigPanelView(wx.Panel):
    def __init__( self, parent ):
        wx.Panel.__init__ ( self, parent, id = wx.ID_ANY, pos = wx.DefaultPosition, size = wx.Size( 972,569 ), style = wx.TAB_TRAVERSAL )
        
        bSizerMain = wx.BoxSizer( wx.VERTICAL )
        
        bSizerTop = wx.BoxSizer( wx.HORIZONTAL )
        bSizerTopLeft = wx.BoxSizer( wx.VERTICAL )
        
        sbSizerTime = wx.StaticBoxSizer( wx.StaticBox( self, wx.ID_ANY, u"Date Time Column:" ), wx.VERTICAL )
        
        choiceTimeColChoices = []
        self.choiceTimeCol = wx.Choice( sbSizerTime.GetStaticBox(), wx.ID_ANY, wx.DefaultPosition, wx.Size( 160,-1 ), choiceTimeColChoices, 0 )
        self.choiceTimeCol.SetSelection( 0 )
        sbSizerTime.Add( self.choiceTimeCol, 0, wx.ALL, 10 )
       
        bSizerUTC = wx.BoxSizer(wx.HORIZONTAL)

        lblUTC = wx.StaticText(sbSizerTime.GetStaticBox(), wx.ID_ANY,u"UTC Offset", wx.DefaultPosition, wx.DefaultSize, 0)
        
        bSizerUTC.Add(lblUTC, 0, wx.ALL, 10)
        bSizerUTC.AddSpacer((0, 0), 1, wx.EXPAND)

        self.spinUTCOffset = wx.SpinCtrl( sbSizerTime.GetStaticBox(), wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, wx.SP_ARROW_KEYS, 0, 10, 0 )
        self.spinUTCOffset.SetMinSize( wx.Size( 50,-1 ) )
        self.spinUTCOffset.SetRange(-12,14) 
        
        bSizerUTC.Add(self.spinUTCOffset, 0, wx.ALL, 10)

        sbSizerTime.Add(bSizerUTC, 0, wx.EXPAND)
        
        
        bSizerTopLeft.Add( sbSizerTime, 0, wx.EXPAND, 10 )
        
        
        
        #sbSizerSpacing = wx.StaticBoxSizer( wx.StaticBox( self, wx.ID_ANY, u"Intended Time Spacing:" ), wx.VERTICAL )
        
        # self.spinTimeSpacing = wx.SpinCtrl( sbSizerSpacing.GetStaticBox(), wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, wx.SP_ARROW_KEYS, 0, 10, 0 )
        # self.spinTimeSpacing.SetMinSize( wx.Size( 160,-1 ) )
        # self.spinTimeSpacing.SetRange(0,100)
        # sbSizerSpacing.Add( self.spinTimeSpacing, 0, wx.ALL, 10 )
        #
        # bSizerUnit = wx.BoxSizer(wx.HORIZONTAL)
        #
        # lblUnitID = wx.StaticText(sbSizerSpacing.GetStaticBox(), wx.ID_ANY,u"Unit", wx.DefaultPosition, wx.DefaultSize, 0)
        #
        # bSizerUnit.Add(lblUnitID, 0, wx.ALL, 10)
        # bSizerUnit.AddSpacer((0, 0), 1, wx.EXPAND)
        #
        # self.choiceUnitID = wx.Choice( sbSizerSpacing.GetStaticBox(), wx.ID_ANY, wx.DefaultPosition, wx.Size( 120,-1 ), choiceTimeColChoices, 0)
        # self.choiceUnitID.SetSelection(0)
        # bSizerUnit.Add(self.choiceUnitID, 0, wx.ALL, 10)
        #
        # sbSizerSpacing.Add(bSizerUnit, 0, wx.EXPAND)
        #
        # bSizerTopLeft.Add(sbSizerSpacing, 0, wx.EXPAND, 10)

        bSizerTop.Add(bSizerTopLeft, 0, wx.EXPAND)

        
        
        sbSizerData = wx.StaticBoxSizer( wx.StaticBox( self, wx.ID_ANY, u"Data Columns:" ), wx.VERTICAL )
        
        #self.m_listCtrl1 = VirtualGrid(self, id=wx.ID_ANY,
        #    pos=wx.DefaultPosition, size=wx.Size(-1, 250))
        if sys.platform == 'darwin':
            self.m_listCtrl1 = MyGrid(self, id=wx.ID_ANY,
                pos=wx.DefaultPosition, size=wx.Size(820, 250))
        else:
            self.m_listCtrl1 = MyGrid(self, id=wx.ID_ANY,
                pos=wx.DefaultPosition, size=wx.Size(-1, 250))
            
        sbSizerData.Add(self.m_listCtrl1, 0, wx.ALL, 10)
        
        bSizerTop.Add( sbSizerData, 1, wx.EXPAND, 10 )
        
        
        bSizerMain.Add( bSizerTop, 0, wx.EXPAND|wx.ALL, 10 )
        
        bSizerBottom = wx.BoxSizer( wx.VERTICAL )
        
        sbSizerMappings = wx.StaticBoxSizer( wx.StaticBox( self, wx.ID_ANY, u"Mappings:" ), wx.VERTICAL )
        
        # ObjectListView table.
        self.lstMappings = \
                ObjectListView(sbSizerMappings.GetStaticBox(),
                           id=wx.ID_ANY,
                           pos=wx.DefaultPosition,
                           size=wx.Size(-1,200),
                           style=wx.LC_REPORT|wx.SUNKEN_BORDER)
        # Customize the list control's message
        # when it is empty.
        self.lstMappings.oddRowsBackColor = wx.Colour(255, 248, 229)
        self.lstMappings.evenRowsBackColor = wx.Colour(204, 229, 255)
        self.lstMappings.SetEmptyListMsg(\
            "No columns mapped")
        self.lstMappings.SetObjects(None)
        self.lstMappings.SetColumns([
            ColumnDefn('Data Column','left',150,'variableName'),
            ColumnDefn('Result ID','left',70,'resultID'),
            ColumnDefn('Samp. Feat. Code','left',110,'samplingFeatureCode'),
            ColumnDefn('Samp. Feat. Name','left',110,'samplingFeatureName'),
            ColumnDefn('Variable Code','left',100,'variableCode'),
            ColumnDefn('Variable Name','left',100,'variableNameCV'),
            ColumnDefn('Units Name','left',80,'unitsName'),
            ColumnDefn('Method Code','left',100,'methodCode'),
            ColumnDefn('Method Name','left',100,'methodName'),
            ColumnDefn('Proc. Level Code','left',110,'processingLevelCode'),])  
        
        sbSizerMappings.Add(self.lstMappings, 1, wx.EXPAND | wx.ALL)
        
        bSizerBottom.Add( sbSizerMappings, 0, wx.EXPAND|wx.ALL)
        
        
        bSizerMain.Add( bSizerBottom, 1, wx.EXPAND|wx.ALL, 10 )
        
        self.SetSizer( bSizerMain )
        self.Layout()
        
        self.Bind(wx.grid.EVT_GRID_LABEL_LEFT_CLICK, self.onColClick, self.m_listCtrl1)
        self.Bind(wx.grid.EVT_GRID_CELL_LEFT_CLICK, self.onCellClick, self.m_listCtrl1)
        self.Bind(wx.grid.EVT_GRID_CELL_RIGHT_CLICK, self.onCellClick, self.m_listCtrl1)
        self.Bind(wx.grid.EVT_GRID_LABEL_LEFT_DCLICK, self.onColDoubleClick, self.m_listCtrl1)
        self.Bind(wx.EVT_CHOICE, self.onTimeChoice, self.choiceTimeCol)
    
    def onAddNew(self, event):
        event.Skip()

    def onColClick(self, event):
        event.Skip()
    
    def onCellClick(self, event):
        event.Skip()
    
    def onTimeSelect(self, event):
        event.Skip()
    
    def onTimeChoice(self, event):
        event.Skip()
    
    def onColDoubleClick(self, event):
        event.Skip()
