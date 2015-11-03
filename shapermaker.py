#-------------------------------------------------------------------------------
# Name:        shapermaker
# Purpose:     Graphical User Interface (GUI) that uses the inputshaping module
#              to design one-mode input shapers based on parameters specified by
#              the user.  Impulse amplitudes and times can be copied to the
#              clipboard using commands in the "Copy" menu of the toolbar.
#
# Author:      James Jackson Potter
# Email:       jjpotterkowski@gmail.com
#
# Created:     25/04/2014 (dd/mm/yyyy)
# Copyright:   (c) 2014 James Jackson Potter
# License:     This program is free software; you can redistribute it and/or
#              modify it under the terms of the GNU General Public License
#              as published by the Free Software Foundation; either version 2
#              of the License, or (at your option) any later version.
#
#              This program is distributed in the hope that it will be useful,
#              but WITHOUT ANY WARRANTY; without even the implied warranty of
#              MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#              GNU General Public License for more details.
#
#              You should have received a copy of the GNU General Public License
#              along with this program; if not, write to the Free Software
#              Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA
#              02110-1301, USA.
#-------------------------------------------------------------------------------
import inputshaping
import wx

__version__ = "1.0"


class ShaperMakerGUI(wx.Frame):
    """
    Step 1: Enter details of oscillatory mode to suppress.  Specifically, the
        natural frequency in rad/s, the damping ratio, the sampling rate in
        frames per second, the input shaper type, the input shaper strength
        between 0 (unshaped) and 1 (full, original input shaper), and an
        additional parameter that only applies for EI and SNA shapers.

    Step 2: Click "Design Input Shaper" button.  The impulse amplitudes and
        times, in both continuous and digital forms, are displayed below the
        "Design Input Shaper" button.

    Step 3: Impulse amplitudes and times can be copied to the clipboard using
        commands in the "Copy" menu of the toolbar.  In the "Tools" menu, the
        "Sensitivity" option generates the input shaper's sensitivity curve.
    """


    def __init__(self, parent, title):
        wx.Frame.__init__(self, parent, title=title)

        # Variable initialization
        self.wn = 1.25
        self.zeta = 0.05
        self.fps = 25
        self.shaperChoices = ['OFF', 'ZV', 'SNA', 'UMZV', 'UMZVD', 'ZVD', 'EI', 'RM3', 'RM4', 'RM5']
        self.shaperType = 'OFF'
        self.shaperSelection = 0
        self.strength = 1.0
        self.parameter = 0.0

        # GUI settings
        self.SetBackgroundColour('lightgrey')
        self.borderWidth = 5

        # Widgets
        self.stt1 = wx.StaticText(self, label="Natural frequency (rad/s):", style=wx.ALIGN_LEFT)
        self.stt2 = wx.StaticText(self, label="Damping ratio:", style=wx.ALIGN_LEFT)
        self.stt3 = wx.StaticText(self, label="Sampling rate (frames/s):", style=wx.ALIGN_LEFT)
        self.stt4 = wx.StaticText(self, label="Input shaper type:", style=wx.ALIGN_LEFT)
        self.stt5 = wx.StaticText(self, label="Input shaper strength:", style=wx.ALIGN_LEFT)
        self.stt6 = wx.StaticText(self, label="Additional parameter:", style=wx.ALIGN_LEFT)

        self.tec1 = wx.TextCtrl(self, value=str(self.wn))
        self.tec2 = wx.TextCtrl(self, value=str(self.zeta))
        self.tec3 = wx.TextCtrl(self, value=str(self.fps))
        self.cob4 = wx.ComboBox(self, choices=self.shaperChoices, style=wx.CB_READONLY)
        self.cob4.SetSelection(self.shaperSelection)
        self.tec5 = wx.TextCtrl(self, value=str(self.strength))
        self.tec6 = wx.TextCtrl(self, value=str(self.parameter))
        self.tec5.Disable()
        self.tec6.Disable()

        self.but7 = wx.Button(self, label="Design Input Shaper")

        self.stb8 = wx.StaticBox(self, label="Continuous", style=wx.ALIGN_CENTER)
        self.stt81 = wx.StaticText(self, label="Amplitudes:", style=wx.ALIGN_LEFT)
        self.stt82 = wx.StaticText(self, label="Times (s):", style=wx.ALIGN_LEFT)

        self.stb9 = wx.StaticBox(self, label="Digital", style=wx.ALIGN_CENTER)
        self.stt91 = wx.StaticText(self, label="Amplitudes:", style=wx.ALIGN_LEFT)
        self.stt92 = wx.StaticText(self, label="Times (s):", style=wx.ALIGN_LEFT)
        self.stt93 = wx.StaticText(self, label="Frames:", style=wx.ALIGN_LEFT)

        # Modify StaticBox font
        sbFont = wx.Font(7, wx.DEFAULT, wx.NORMAL, wx.BOLD)
        self.stb8.SetFont(sbFont)
        self.stb9.SetFont(sbFont)

        # Status bar
        self.CreateStatusBar()
        self.SetStatusText(" Specify settings, then click 'Design Input Shaper' button") # text in status bar before it gets replaced

        # Menu bar
        self.ID_COPYCONAMPS = 100
        self.ID_COPYCONTIMES = 101
        self.ID_COPYDIGAMPS = 102
        self.ID_COPYDIGTIMES = 103
        self.ID_COPYDIGSTEPS = 104
        self.ID_SENSITIVITY = 105

        copy_menu = wx.Menu()
        copy_menu.Append(self.ID_COPYCONAMPS, 'Continuous amplitudes', ' Copy continuous impulse amplitudes to clipboard')
        copy_menu.Append(self.ID_COPYCONTIMES, 'Continuous times', ' Copy continuous impulse times to clipboard')
        copy_menu.AppendSeparator()
        copy_menu.Append(self.ID_COPYDIGAMPS, 'Digital amplitudes', ' Copy digital impulse amplitudes to clipboard')
        copy_menu.Append(self.ID_COPYDIGTIMES, 'Digital times', ' Copy digital impulse times to clipboard')
        copy_menu.Append(self.ID_COPYDIGSTEPS, 'Digital frames', ' Copy digital impulse frames to clipboard')

        tools_menu = wx.Menu()
        tools_menu.Append(self.ID_SENSITIVITY, 'Sensitivity curve', ' Plot sensitivity curve of input shaper')

        menu_bar = wx.MenuBar()
        menu_bar.Append(copy_menu, '&Copy')
        menu_bar.Append(tools_menu, '&Tools')
        self.SetMenuBar(menu_bar)

        # Widget layout and such
        self.conSizer = wx.StaticBoxSizer(self.stb8, wx.VERTICAL)
        self.conSizer.AddMany([(self.stt81, -1, wx.TOP|wx.LEFT|wx.RIGHT, self.borderWidth),
            (self.stt82, 0, wx.ALL, self.borderWidth)])

        self.digSizer = wx.StaticBoxSizer(self.stb9, wx.VERTICAL)
        self.digSizer.AddMany([(self.stt91, -1, wx.TOP|wx.LEFT|wx.RIGHT, self.borderWidth),
            (self.stt92, 0, wx.TOP|wx.LEFT|wx.RIGHT, self.borderWidth),
            (self.stt93, 0, wx.ALL, self.borderWidth)])

        mainSizer = wx.BoxSizer(wx.VERTICAL)
        mainSizer.AddMany([(self.stt1, 0, wx.TOP|wx.LEFT|wx.RIGHT, self.borderWidth), # 3 numbers are proportion, flag, border
            (self.tec1, 0, wx.TOP|wx.LEFT|wx.RIGHT, self.borderWidth),
            (self.stt2, 0, wx.TOP|wx.LEFT|wx.RIGHT, self.borderWidth),
            (self.tec2, 0, wx.TOP|wx.LEFT|wx.RIGHT, self.borderWidth),
            (self.stt3, 0, wx.TOP|wx.LEFT|wx.RIGHT, self.borderWidth),
            (self.tec3, 0, wx.TOP|wx.LEFT|wx.RIGHT, self.borderWidth),
            (self.stt4, 0, wx.TOP|wx.LEFT|wx.RIGHT, self.borderWidth),
            (self.cob4, 0, wx.TOP|wx.LEFT|wx.RIGHT, self.borderWidth),
            (self.stt5, 0, wx.TOP|wx.LEFT|wx.RIGHT, self.borderWidth),
            (self.tec5, 0, wx.TOP|wx.LEFT|wx.RIGHT, self.borderWidth),
            (self.stt6, 0, wx.TOP|wx.LEFT|wx.RIGHT, self.borderWidth),
            (self.tec6, 0, wx.TOP|wx.LEFT|wx.RIGHT, self.borderWidth),
            (self.but7, 0, wx.TOP|wx.LEFT|wx.RIGHT|wx.EXPAND, self.borderWidth),
            (self.conSizer, 0, wx.TOP|wx.LEFT|wx.RIGHT, self.borderWidth),
            (self.digSizer, 0, wx.ALL, self.borderWidth)])
        mainSizer.SetSizeHints(self)
        self.SetSizer(mainSizer)

        self._layout_main_frame()
        self.Show()

        # Make bindings
        self.Bind(wx.EVT_BUTTON, self._on_button, self.but7)
        self.Bind(wx.EVT_MENU, lambda event: self.to_clipboard(event, 1), id=self.ID_COPYCONAMPS)
        self.Bind(wx.EVT_MENU, lambda event: self.to_clipboard(event, 2), id=self.ID_COPYCONTIMES)
        self.Bind(wx.EVT_MENU, lambda event: self.to_clipboard(event, 3), id=self.ID_COPYDIGAMPS)
        self.Bind(wx.EVT_MENU, lambda event: self.to_clipboard(event, 4), id=self.ID_COPYDIGTIMES)
        self.Bind(wx.EVT_MENU, lambda event: self.to_clipboard(event, 5), id=self.ID_COPYDIGSTEPS)
        self.Bind(wx.EVT_MENU, self._on_sensitivity, id=self.ID_SENSITIVITY)
        self.Bind(wx.EVT_COMBOBOX, self._on_combobox, self.cob4)

        # Get the ball rolling by initializing shaper to OFF
        self.shaperObject = inputshaping.InputShaper(self.wn, self.zeta, self.fps)
        self._on_button(wx.ID_MORE) # using wx.ID_MORE as an arbitrary event ID ...


    def _on_combobox(self, event):
        self.shaperSelection = self.cob4.GetSelection()
        self.shaperType = self.shaperChoices[self.shaperSelection]

        if self.shaperType == 'SNA':
            self.tec5.Enable()
            self.tec5.SetValue('1.0')
            self.stt6.SetLabel("Negative impulse:")
            self.tec6.Enable()
            self.tec6.SetValue('0.5')

        elif self.shaperType == 'EI':
            self.tec5.Enable()
            self.tec5.SetValue('1.0')
            self.stt6.SetLabel("Tolerable vibration:")
            self.tec6.Enable()
            self.tec6.SetValue('0.05')

        elif (self.shaperType == 'OFF') or (self.shaperType == 'UMZV') or (self.shaperType == 'UMZVD'):
            self.tec5.Disable()
            self.tec5.SetValue('1.0')
            self.stt6.SetLabel("Additional parameter:")
            self.tec6.Disable()
            self.tec6.SetValue('0.0')

        else:
            self.tec5.Enable()
            self.tec5.SetValue('1.0')
            self.stt6.SetLabel("Additional parameter:")
            self.tec6.Disable()
            self.tec6.SetValue('0.0')


    def _on_sensitivity(self, event):
        self.shaperObject.sensitivity_curve()


    def to_clipboard(self, event, flag):
        clipdata = wx.TextDataObject()
        if flag == 1:
            clipdata.SetText(self.conAmps)
        elif flag == 2:
            clipdata.SetText(self.conTimes)
        elif flag == 3:
            clipdata.SetText(self.digAmps)
        elif flag == 4:
            clipdata.SetText(self.digTimes)
        else:
            clipdata.SetText(self.digFrames)

        wx.TheClipboard.Open()
        wx.TheClipboard.SetData(clipdata)
        wx.TheClipboard.Close()


    def _on_button(self, event):
        self.SetStatusText("Use 'Copy' menu to send vectors to clipboard")

        # Read parameters from GUI
        self.wn = float(self.tec1.Value)
        self.zeta = float(self.tec2.Value)
        self.fps = float(self.tec3.Value)
        self.shaperSelection = self.cob4.GetSelection()
        self.shaperType = self.shaperChoices[self.shaperSelection]
        self.strength = float(self.tec5.Value)
        self.parameter = float(self.tec6.Value)

        # Design input shaper with inputshaper module
        ins = inputshaping.InputShaper(self.wn, self.zeta, self.fps)
        if (self.shaperType == 'SNA') or (self.shaperType == 'EI'):
            execString = 'ins.' + self.shaperType + '(' + str(self.parameter) + ', ' + str(self.strength) + ')'
        elif (self.shaperType == 'OFF') or (self.shaperType == 'UMZV') or (self.shaperType == 'UMZVD'):
            execString = 'ins.' + self.shaperType + '()'
        else:
            execString = 'ins.' + self.shaperType + '(' + str(self.strength) + ')'
        exec(execString)

        # Extract information from InputShaper object
        self.shaperObject = ins
        self.conAmps = self._format_impulse_vector(ins.conAmps)
        self.conTimes = self._format_impulse_vector(ins.conTimes)
        self.digAmps =self._format_impulse_vector(ins.digAmps)
        self.digTimes = self._format_impulse_vector(ins.digTimes)
        self.digFrames =str(ins.digFrames)

        # Display information in labels and update GUI
        self.stt81.SetLabel("Amplitudes: " + self.conAmps)
        self.stt82.SetLabel("Times (s):   " + self.conTimes)
        self.stt91.SetLabel("Amplitudes: " + self.digAmps)
        self.stt92.SetLabel("Times (s):   " + self.digTimes)
        self.stt93.SetLabel("Frames:      " + self.digFrames)
        self._layout_main_frame()


    def _layout_main_frame(self):
        # Note that we're talking to the sizer, not the frame itself
        self.GetSizer().SetSizeHints(self) # IMPORTANT to get window to resize
        self.Refresh()


    def _format_impulse_vector(self, vectorIn):
        return "["+", ".join(["%.3f" % x for x in vectorIn])+"]"


def run_gui():
    app = wx.App() # create an application class instance
    frm = ShaperMakerGUI(None, 'ShaperMaker')
    app.MainLoop() # enter the application main loop


if __name__ == '__main__':
    app = wx.App() # create an application class instance
    frm = ShaperMakerGUI(None, 'ShaperMaker')
    app.MainLoop() # enter the application main loop
