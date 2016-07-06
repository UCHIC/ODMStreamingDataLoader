# -*- coding: utf-8 -*- 

###########################################################################
## Python code generated with wxFormBuilder (version Jun  5 2014)
## http://www.wxformbuilder.org/
##
## PLEASE DO "NOT" EDIT THIS FILE!
###########################################################################

import wx
import wx.xrc

###########################################################################
## Class clsDBConfiguration
###########################################################################

class clsDBConfiguration ( wx.Panel ):
	
    def __init__( self, parent ):
        wx.Panel.__init__ ( self, parent, id = wx.ID_ANY, pos = wx.DefaultPosition, size = wx.DefaultSize, style = wx.TAB_TRAVERSAL )
        
        self.SetMinSize( wx.Size( 442,291 ) )
        self.SetMaxSize( wx.Size( 627,291 ) )
        
        formSizer = wx.BoxSizer( wx.VERTICAL )

        sbSizer = wx.StaticBoxSizer( wx.StaticBox( self, wx.ID_ANY, u"Database Connection:" ), wx.VERTICAL )
        
        connectionSizer = wx.FlexGridSizer( 0, 2, 0, 15 )
        connectionSizer.AddGrowableCol( 1 )
        connectionSizer.SetFlexibleDirection( wx.VERTICAL )
        connectionSizer.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_ALL )
        
        
        self.stConnType = wx.StaticText( self, wx.ID_ANY, u"Connection Type", wx.DefaultPosition, wx.DefaultSize, wx.ALIGN_RIGHT )
        self.stConnType.Wrap( -1 )
        connectionSizer.Add( self.stConnType, 0, wx.ALL|wx.EXPAND|wx.ALIGN_RIGHT, 5 )
        
        cbDatabaseTypeChoices = []
        self.cbDatabaseType = wx.ComboBox( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, cbDatabaseTypeChoices, wx.CB_READONLY )

        connectionSizer.Add( self.cbDatabaseType, 1, wx.ALL|wx.EXPAND, 5 )
        
        self.stServer = wx.StaticText( self, wx.ID_ANY, u"Server", wx.DefaultPosition, wx.DefaultSize, wx.ALIGN_RIGHT )
        self.stServer.Wrap( -1 )
        connectionSizer.Add( self.stServer, 0, wx.ALL|wx.EXPAND|wx.ALIGN_RIGHT, 5 )
        
        self.txtServer = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0|wx.FULL_REPAINT_ON_RESIZE|wx.SIMPLE_BORDER )
        connectionSizer.Add( self.txtServer, 1, wx.ALL|wx.EXPAND, 5 )
        
        self.stDBName = wx.StaticText( self, wx.ID_ANY, u"Database", wx.DefaultPosition, wx.DefaultSize, wx.ALIGN_RIGHT )
        self.stDBName.Wrap( -1 )
        self.stDBName.SetFont( wx.Font( wx.NORMAL_FONT.GetPointSize(), 70, 90, 90, False, wx.EmptyString ) )
        
        connectionSizer.Add( self.stDBName, 0, wx.ALL|wx.EXPAND|wx.ALIGN_RIGHT, 5 )
        
        self.txtDBName = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0|wx.SIMPLE_BORDER )
        connectionSizer.Add( self.txtDBName, 1, wx.ALL|wx.EXPAND, 5 )
        
        self.stUser = wx.StaticText( self, wx.ID_ANY, u"User", wx.DefaultPosition, wx.DefaultSize, wx.ALIGN_RIGHT )
        self.stUser.Wrap( -1 )
        self.stUser.SetFont( wx.Font( wx.NORMAL_FONT.GetPointSize(), 70, 90, 90, False, wx.EmptyString ) )
        
        connectionSizer.Add( self.stUser, 0, wx.ALL|wx.EXPAND|wx.ALIGN_RIGHT, 5 )
        
        self.txtUser = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0|wx.SIMPLE_BORDER )
        connectionSizer.Add( self.txtUser, 1, wx.ALL|wx.EXPAND, 5 )
        
        self.stPass = wx.StaticText( self, wx.ID_ANY, u"Password", wx.DefaultPosition, wx.DefaultSize, wx.ALIGN_RIGHT )
        self.stPass.Wrap( -1 )
        self.stPass.SetFont( wx.Font( wx.NORMAL_FONT.GetPointSize(), 70, 90, 90, False, wx.EmptyString ) )
        
        connectionSizer.Add( self.stPass, 0, wx.ALL|wx.EXPAND|wx.ALIGN_RIGHT, 5 )
        
        self.txtPass = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, wx.TE_PASSWORD|wx.SIMPLE_BORDER )
        connectionSizer.Add( self.txtPass, 1, wx.ALL|wx.EXPAND, 5 )

        self.btnTest = wx.Button(self, wx.ID_ANY | wx.RIGHT, u"Test Connection", wx.DefaultPosition, wx.DefaultSize, 0)
        sbSizer.Add( connectionSizer, 90, wx.EXPAND, 3 )
        
        
        formSizer.Add( sbSizer, 1, wx.ALL|wx.EXPAND, 7 )
        
        #btnSizer = wx.FlexGridSizer( 0, 2, 0, 0)
        #btnSizer.SetFlexibleDirection( wx.VERTICAL )
        

        connectionSizer.AddSpacer( ( 0, 0), 1, wx.EXPAND, 5 )
        connectionSizer.Add( self.btnTest, 0, wx.ALL|wx.RIGHT|wx.ALIGN_RIGHT, 0 )
        
        #formSizer.Add( btnSizer, 0, wx.EXPAND, 5 )
        
        
        self.SetSizer( formSizer )
        self.Layout()
        
        # Connect Events
        self.btnTest.Bind( wx.EVT_BUTTON, self.onTestConnection )
        self.btnTest.SetFocus()
    
    def __del__( self ):
            pass
    
    
    # Virtual event handlers, overide them in your derived class
    def onTestConnection( self, event ):
            event.Skip()
    
    def OnBtnSave( self, event ):
            event.Skip()
    
    

