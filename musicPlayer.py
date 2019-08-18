import os
import wx
import wx.media
import wx.lib.buttons as buttons

dirName = os.path.dirname(os.path.abspath(__file__))
bitmapDir = os.path.join(dirName, 'bitmaps')

#################################################

class MediaPanel(wx.Panel):

#-----------------------------------------------

    def __init__(self, parent):
        wx.Panel.__init__(self, parent = parent)

        self.frame = parent
        self.currentVolume = 50
        self.createMenu()
        self.layoutControls()

        sp = wx.StandardPaths.Get()
        self.currentFolder = sp.GetDocumentsDir()

        self.timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.onTimer)
        self.timer.Start(100)

#-----------------------------------------------

    def layoutControls(self):

        try:
            self.mediaPlayer = wx.media.MediaCtrl(self, style = wx.SIMPLE_BORDER)
        except NotImplementedError:
            self.Destroy()
            raise

        #create a playback slider
        self.playbackSlider = wx.Slider(self, size = wx.DefaultSize)

        self.Bind(wx.EVT_SLIDER, self.onSeek, self.playbackSlider)

        self.volumeCtrl = wx.Slider(self, style = wx.SL_VERTICAL | wx.SL_INVERSE)
        self.volumeCtrl = wx.SetRange(0, 100)
        self.volumeCtrl.SetValue(self.currentVolume)
        self.Bind(wx.EVT_SLIDER, self.onSetVolume)

        #create sizers
        mainSizer = wx.BoxSizer(wx.VERTICAL)
        hSizer = wx.BoxSizer(wx.HORIZONTAL)
        audioSizer = self.buildAudioBar()

        #layout widgets
        mainSizer.Add(self.playbackSlider, 1, wx.ALL | wx.EXPAND, 5)
        hSizer.Add(audioSizer, 0, wx.ALL | wx.CENTER, 5)
        mainSizer.Add(hSizer)

        self.hSizer(mainSizer)
        self.Layout()

#------------------------------------------------

        def buildAudioBar(self):
            """Building the audio bar control"""
            audioBarSizer = wx.BoxSizer(wx.HORIZONTAL)
            self.buildBtn({'bitmap':"player_prev.png", 'handler':self.onPrev, 'name':'prev'}, audioBarSizer)
            #self.buildBtn({'bitmap': 'player_prev.png', 'handler': self.onPrev, 'name': 'prev'}, audioBarSizer)
            #create play/pause toggle button
            img = wx.Bitmap(os.path.join(bitmapDir, "player_play.png"))
            self.playPauseBtn = buttons.GenBitmapToggleButton(self, bitmap = img, name = "play")
            self.playPauseBtn.Enable(False)

            img = wx.Bitmap(os.path.join(bitmapDir, "player_pause.png"))
            self.playPauseBtn.SetBitmapSelected(img)
            self.playPauseBtn.SetInitialSize()

            self.playPauseBtn.Bind(wx.EVT_BUTTON, self.onPlay)
            audioBarSizer.Add(self.playPauseBtn, 0, wx.LEFT, 3)

            btnData = [{'bitmap': 'player_stop.png',
                        'handler': self.onStop,
                        'name': 'stop'},
                       {'bitmap': 'player_next.png',
                        'handler': self.onNext,
                        'name': 'next'}]
            for btn in btnData:
                self.buildBtn(btn, audioBarSizer)
            return audioBarSizer

#--------------------------------------------------------------------

        def buildBtn(self, btnDict, sizer):
            bmp = btnDict['bitmap']
            handler = btnDict['handler']

            img = wx.Bitmap(os.path.join(bitmapDir, bmp))
            btn = buttons.GenBitmaoButton(self, bitmap = img, name = btnDict['name'])
            btn.SetInitialSize()
            btn.Bind(wx.EVT_BUTTON, handler)
            sizer.Add(btn, 0, wx.LEFT, 3)

#---------------------------------------------------------------------

        def createMenu(self):
            """creates a menu"""
            menubar = wx.MenuBar()

            fileMenu = wx.Menu()
            open_file_menu_item = fileMenu.Append(wx.NewId(), "&Open", "Open a File")
            menubar.Append(fileMenu, '&File')
            self.frame.SetMenuBar(menubar)
            self.frame.Bind(wx.EVT_MENU, self.onBrowsw, open_file_menu_item)

#----------------------------------------------------------------------

        def loadMusic(self, musicFile):
            """
            load the music in the MediaCtrl od display an error dialog
            if the user tries to load an unsupported file type
            """
            if not self.mediaPlayer.Load(musicFile):
                wx.MessageBox("Unable to load %s: Unsupported format" %musicFile,
                              "ERROR", wx.ICON_ERROR | wx.OK)
            else:
                self.mediaPlayer.SetInitialSize()
                self.GetSizer().Layout()
                self.playbackSlider.SetRange(0, self.mediaPlayer.Length())
                self.playPauseBtn.Enable(True)

#------------------------------------------------------------------

        def onBrowse(self, event):
            """
            Opens a file dialog to browse for music
            """
            wildcard = "MP3 (*.mp3)|*.mp3|"\
                       "WAV (*.wav)|*.wav"
            dlg = wx.FileDialog(
                self, message = "Choose a File",
                defaultDir=self.currentFolder,
                defaultFile="",
                wildcard=wildcard,
                style = wx.OPEN | wx.CHANGE_DIR
                )
            if dlg.ShowModal() == wx.ID_OK:

