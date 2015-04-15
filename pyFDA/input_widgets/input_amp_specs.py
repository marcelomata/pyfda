# -*- coding: utf-8 -*-
"""
Created on Mon Nov 18 13:36:39 2013

@author: Julia Beike, Christian Münker
"""

# TODO: Check specs IIR / FIR A_PB <-> delta_PB
# TODO: Rounding errors during muliple to-and-fro changes
from __future__ import print_function, division, unicode_literals
from numpy import log10
import sys, os
from PyQt4 import QtGui, QtCore

# import filterbroker from one level above if this file is run as __main__
# for test purposes
if __name__ == "__main__":
    __cwd__ = os.path.dirname(os.path.abspath(__file__))
    sys.path.append(os.path.dirname(__cwd__))


class InputAmpSpecs(QtGui.QWidget): #QtGui.QWidget,
    """
    Build and update widget for entering the amplitude
    specifications like A_sb, A_pb etc.
    """
    def __init__(self, specs, DEBUG = True):

        """
        Initialize; specs is a dictionary containing _all_ the filter specs
        """
        super(InputAmpSpecs, self).__init__()
        self.DEBUG = DEBUG
        self.specs = specs  # dictionary containing _all_ specifications of the
                            # currently selected filter

#        self.labels = labels # list with labels for combobox

        self.qlabels = [] # list with references to QLabel widgets
        self.qlineedit = [] # list with references to QLineEdit widgets

        self.initUI()

    def initUI(self):
        self.layVMain = QtGui.QVBoxLayout() # Widget vertical layout

        title = "Amplitude Specifications"
        units = ["dB", "V", "W"]
        self.idxOld = -1 # index of comboUnits before last change

        bfont = QtGui.QFont()
        bfont.setBold(True)
#            bfont.setWeight(75)
        self.lblTitle = QtGui.QLabel(self) # field for widget title
        self.lblTitle.setText(str(title))
        self.lblTitle.setFont(bfont)
        self.lblTitle.setWordWrap(True)
        self.layVMain.addWidget(self.lblTitle)

        self.lblUnits = QtGui.QLabel(self)
        self.lblUnits.setText("Unit:")

        self.cmbUnitsA = QtGui.QComboBox(self)
        self.cmbUnitsA.addItems(units)
        self.cmbUnitsA.setObjectName("cmbUnitsA")
        self.cmbUnitsA.setToolTip("Set unit for amplitude specifications:\n"
        "dB is attenuation (positive values)\nV and W are less than 1.")
        
        """Edit WincMIC"""
        #Die ComboBox passt Ihre größe dynamisch dem längsten element an.
        self.cmbUnitsA.setSizeAdjustPolicy(QtGui.QComboBox.AdjustToContents)
        """END"""

        self.cmbUnitsA.setCurrentIndex(0)

        self.layGSpecs = QtGui.QGridLayout() # sublayout for spec fields
        self.layGSpecs.addWidget(self.lblUnits,0,0)
        self.layGSpecs.addWidget(self.cmbUnitsA,0,1, QtCore.Qt.AlignLeft)

        #self.layGSpecs.addWidget(self.lblTitle, 0, 0, 2, 1) # span two columns

        # - Build a list from all entries in the specs dictionary starting
        #   with "A" (= amplitude specifications of the current filter)
        # - Pass the list to setEntries which recreates the widget
        newLabels = [l for l in self.specs if l[0] == 'A']
        self.setEntries(newLabels = newLabels)

        frmMain = QtGui.QFrame()
        frmMain.setFrameStyle(QtGui.QFrame.StyledPanel|QtGui.QFrame.Sunken)
        frmMain.setLayout(self.layGSpecs)

        self.layVMain.addWidget(frmMain)
        self.layVMain.setContentsMargins(1,1,1,1)

        self.setLayout(self.layVMain)
#
#        mainLayout = QtGui.QHBoxLayout()
#        mainLayout.addWidget(frmMain)
#        self.setLayout(mainLayout)

        # SIGNALS & SLOTS
        # Every time a field is edited, call self.freqUnits - the signal is
        #   constructed in _addEntry
        self.cmbUnitsA.currentIndexChanged.connect(self.ampUnits)

        self.ampUnits()

    def ampUnits(self):
        """
        Transform the amplitude spec input fields according to the Units
        setting. Spec entries are always stored in dB, only the displayed
        values are adapted to the amplitude unit, not the dictionary!
        """
        idx = self.cmbUnitsA.currentIndex()  # read index of units combobox

        if self.sender(): # origin of signal that triggered the slot
            senderName = self.sender().objectName()
            print(senderName + ' was triggered\n================')
        else: # no sender, ampUnits has been called from initUI
            senderName = "cmbUnitsA"

        if senderName == "cmbUnitsA" and idx != self.idxOld:
            # combo unit has changed -> change display of amplitude entries
            self.loadEntries()

        else: # amplitude spec textfield has been changed
            self.storeEntries()
        self.idxOld = idx

    def rtLabel(self, label):
        """
        Rich text label: Format label with HTML tags, replacing '_' by
        HTML subscript tags
        """
        #"<b><i>{0}</i></b>".format(newLabels[i])) # update label
        if "_" in label:
            label = label.replace('_', '<sub>')
            label += "</sub>"
        htmlLabel = "<b><i>"+label+"</i></b>"
        return htmlLabel
#-------------------------------------------------------------
    def setEntries(self, newLabels = []):
        """
        Set labels and get corresponding values from filter dictionary.
        When number of elements changes, the layout of subwidget is rebuilt.
        """
        # Check whether the number of entries has changed
        for i in range(max(len(self.qlabels), len(newLabels))):
             # newLabels is shorter than qlabels -> delete the difference
            if (i > (len(newLabels)-1)):
                self._delEntry(len(newLabels))

            # newLabels is longer than existing qlabels -> create new ones!
            elif (i > (len(self.qlabels)-1)):
             self._addEntry(i,newLabels[i])

            else:
                # when entry has changed, update label and corresponding value
                if self.qlineedit[i].objectName() != newLabels[i]:
                    self.qlabels[i].setText(self.rtLabel(newLabels[i]))
                    self.qlineedit[i].setText(str(self.specs[newLabels[i]]))
                    self.qlineedit[i].setObjectName(newLabels[i])  # update ID

    def _delEntry(self,i):
        """
        Delete entry number i from subwidget (QLabel and QLineEdit)
        """
        self.layGSpecs.removeWidget(self.qlabels[i])
        self.layGSpecs.removeWidget(self.qlineedit[i])

        self.qlabels[i].deleteLater()
        del self.qlabels[i]
        self.qlineedit[i].deleteLater()
        del self.qlineedit[i]


    def _addEntry(self, i, newLabel):
        """
        Append entry number i to subwidget (QLabel und QLineEdit)
        """
        self.qlabels.append(QtGui.QLabel(self))
        self.qlabels[i].setText(self.rtLabel(newLabel))

        self.qlineedit.append(QtGui.QLineEdit(str(self.specs[newLabel])))
        self.qlineedit[i].editingFinished.connect(self.ampUnits)
        self.qlineedit[i].setObjectName(newLabel) # update ID

        self.layGSpecs.addWidget(self.qlabels[i],(i+2),0)
        self.layGSpecs.addWidget(self.qlineedit[i],(i+2),1)

    def loadEntries(self):
        """
        Reload textfields from filter dictionary to update changed settings
        """
        idx = self.cmbUnitsA.currentIndex()  # read index of units combobox

        if idx == 0: # Entry is in dBs, same as in dictionary
            for i in range(len(self.qlineedit)):
                self.qlineedit[i].setText(
                    str(self.specs[self.qlineedit[i].objectName()]))

        elif idx == 1:  # Entries are voltages, convert from dBs
            for i in range(len(self.qlineedit)):
                self.qlineedit[i].setText(
                    str(10.**(-self.specs[self.qlineedit[i].objectName()]/20.)))

        else:  # Entries are powers, convert from dBs
            for i in range(len(self.qlineedit)):
                self.qlineedit[i].setText(
                    str(10.**(-self.specs[self.qlineedit[i].objectName()]/10.)))

    def storeEntries(self):
        """
        Store specification entries in filter dictionary
        Entries are always stored in dB (20 log10) !
        """
        idx = self.cmbUnitsA.currentIndex()  # read index of units combobox

#        for i in range(len(self.qlineedit)):
#            self.specs.update(
#                {self.qlineedit[i].objectName():float(self.qlineedit[i].text())})

        if idx == 0: # Entry is in dBs, same as in dictionary
            for i in range(len(self.qlineedit)):
                self.specs.update(
                    {self.qlineedit[i].objectName():
                        float(self.qlineedit[i].text())})

        elif idx == 1:  # Entries are voltages, convert to dBs
            for i in range(len(self.qlineedit)):
                self.specs.update(
                    {self.qlineedit[i].objectName():
                       - 20. * log10 (float(self.qlineedit[i].text()))})
        else:  # Entries are powers, convert to dBs
            for i in range(len(self.qlineedit)):
                self.specs.update(
                    {self.qlineedit[i].objectName():
                       - 10. * log10 (float(self.qlineedit[i].text()))})


#------------------------------------------------------------------------------

if __name__ == '__main__':
    import filterbroker as fb

    app = QtGui.QApplication(sys.argv)
    form = InputAmpSpecs(specs = fb.fil[0])

    form.setEntries(newLabels = ['A_SB','A_SB2','A_PB','A_PB2'])
    form.setEntries(newLabels = ['A_PB','A_PB2'])

    form.show()

    app.exec_()
