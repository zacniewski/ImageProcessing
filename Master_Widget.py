# -*- coding: utf-8 -*-

import sys
import os
import platform
import cStringIO
from PIL import Image, ImageFilter, ImageDraw
from PyQt4 import QtGui, QtCore
#import numpy as np
#nr wersji programu :)
__version__ = "1.1"
class SuperProgram(QtGui.QWidget):
    css="""
    QtGui.QHBoxLayout{
    color:white;
    border-style:solid;
    border-width:5px;
    }
    """
    def __init__(self):
        super(SuperProgram, self).__init__()
        
        #inicjalizacja nazwy pliku - ważne !!!
        self.filename = None       
        
        #inicjalizacja obrazków - ważne !!!
        self.image = QtGui.QImage()
        self.PIL2qpixmap_image = QtGui.QImage()

        #menu
        toolbar_menu = QtGui.QHBoxLayout()
        toolBar = QtGui.QToolBar()
        
        #menu Plik->Otwórz plik
        openFileAction = QtGui.QAction(QtGui.QIcon('Program_Images/fileopen.png'), u'Otwórz plik', self)
        openFileAction.setShortcut('Ctrl+O')
        openFileAction.setToolTip(u'Otwórz nowy plik')
        openFileAction.triggered.connect(self.showDialog)   
        
        #menu Plik->Zamknij
        exitAction = QtGui.QAction(QtGui.QIcon('Program_Images/filequit.png'), 'Zamknij', self)        
        exitAction.setShortcut('Ctrl+Q')
        exitAction.setStatusTip('Zamknij program')
        exitAction.triggered.connect(QtGui.qApp.quit)   
                  
        #przycisk Plik
        fileButton = QtGui.QToolButton()
        fileButton.setText('Plik')
        
        #dodanie akcji do przycisku 'Plik'
        fileButton.addAction(openFileAction)
        fileButton.addAction(exitAction)
        fileButton.setPopupMode(QtGui.QToolButton.MenuButtonPopup)
        fileButton.setToolTip(u'Menu główne')

        # dodanie menu 'Plik' do paska
        toolBar.addWidget(fileButton)
        
        #przycisk Edycja
        editButton = QtGui.QToolButton()
        editButton.setText('Edycja obrazu')
        editButton.setPopupMode(QtGui.QToolButton.MenuButtonPopup) 
        
        # dodanie menu 'Edycja' do paska
        toolBar.addWidget(editButton)      
                  
        #menu Edycja->Zamień kolory
        invertAction = QtGui.QAction(QtGui.QIcon('Program_Images/editinvert.png'), u'Odwróć piksele', self)        
        invertAction.setShortcut('Ctrl+I')
        invertAction.setToolTip(u'Zamiana kolorów w obrazie')
        invertAction.triggered.connect(self.editInvert)   
        
        #dodanie akcji do przycisku 'Edycja'
        editButton.addAction(invertAction)
        editButton.addAction(invertAction)
        
        #przycisk Filtry
        filterButton = QtGui.QToolButton()
        filterButton.setText('Filtry dla obrazu')
        filterButton.setPopupMode(QtGui.QToolButton.MenuButtonPopup) 
                
        #menu Filtry->Filtr nr 1
        filter1Action=QtGui.QAction(QtGui.QIcon('Program_Images/editinvert.png'), u'Filtr medianowy',self)
        filter1Action.triggered.connect(self.image2PIL)
       
        #menu Filtry->Filtr nr 2
        filter2Action=QtGui.QAction(QtGui.QIcon('Program_Images/editswap.png'), u'Filtr nr 2',self)
        filter2Action.triggered.connect(self.helpFeatures) #zmienić !!
                
        #dodanie akcji do przycisku 'Filtry'
        filterButton.addAction(filter1Action)
        filterButton.addAction(filter2Action)
        filterButton.setToolTip("Wybierz filtr")
        
        # dodanie menu 'Filtry' do paska
        toolBar.addWidget(filterButton)   
        
        #Zoom dla obrazka
        self.zoomSpinBox = QtGui.QSpinBox()
        self.zoomSpinBox.setRange(1, 400)
        self.zoomSpinBox.setSuffix(" %")
        self.zoomSpinBox.setValue(100)
        self.zoomSpinBox.setToolTip("Zoom dla obrazu")
        self.zoomSpinBox.setStatusTip(self.zoomSpinBox.toolTip())
        self.zoomSpinBox.setFocusPolicy(QtCore.Qt.NoFocus)
        self.connect(self.zoomSpinBox,QtCore.SIGNAL("valueChanged(int)"), self.showImage)
        toolBar.addWidget(self.zoomSpinBox)
        
        #przycisk Pomoc
        helpButton = QtGui.QToolButton()
        helpButton.setText('Pomoc')
        helpButton.setPopupMode(QtGui.QToolButton.MenuButtonPopup) 
                
        #menu Pomoc->O programie
        helpAction=QtGui.QAction(QtGui.QIcon('Program_Images/icon.png'), u'O programie',self)
        helpAction.triggered.connect(self.helpAbout)
       
        #menu Pomoc->Opis możliwości
        featuresAction=QtGui.QAction(QtGui.QIcon('Program_Images/filenew.png'), u'Możliwości programu',self)
        featuresAction.triggered.connect(self.helpFeatures)
                
        #dodanie akcji do przycisku 'Pomoc'
        helpButton.addAction(helpAction)
        helpButton.addAction(featuresAction)
        helpButton.setToolTip('Info o programie')
        
        # dodanie menu 'Pomoc' do paska
        toolBar.addWidget(helpButton)     
        
        # dodanie paska menu do layoutu
        toolbar_menu.addWidget(toolBar)
               
        #napisy wejściowe
        label_up_box = QtGui.QHBoxLayout()
        self.napis1=QtGui.QLabel(u"\nOBRAZ WEJŚCIOWY")
        self.napis1.setStyleSheet("font: 14pt \"MS Shell Dlg 2\";")
        self.napis1.setAlignment(QtCore.Qt.AlignCenter)

        self.napis2=QtGui.QLabel(u"\nOBRAZ WYJŚCIOWY")
        self.napis2.setStyleSheet("font: 14pt \"MS Shell Dlg 2\";")
        self.napis2.setAlignment(QtCore.Qt.AlignCenter)
        
        label_up_box.addWidget(self.napis1)
        label_up_box.addWidget(self.napis2)
        #label_up_box.insertStretch(1,500)
        
        #dwa górne okna
        hbox = QtGui.QHBoxLayout()
        self.up_left = QtGui.QLabel(self)
        self.up_left.setAlignment(QtCore.Qt.AlignCenter)
        self.up_right = QtGui.QLabel(self)
        self.up_right.setAlignment(QtCore.Qt.AlignCenter)
        hbox.addWidget(self.up_left)
        hbox.addWidget(self.up_right)
        
        #napisy do slidera
        self.label_slider = QtGui.QVBoxLayout()
        self.napis5=QtGui.QLabel(u"\nREGULACJA JASNOŚCI")
        self.napis5.setStyleSheet("font: 14pt \"MS Shell Dlg 2\";")
        self.napis5.setAlignment(QtCore.Qt.AlignCenter)
        self.label_slider.addWidget(self.napis5)

        #slider i licznik
        hbox2 = QtGui.QHBoxLayout()
        self.sld = QtGui.QSlider(QtCore.Qt.Horizontal, self)
        self.sld.setMinimum(-255)
        self.sld.setMaximum(255)
        lcd = QtGui.QLCDNumber(self)
        lcd.setSegmentStyle(QtGui.QLCDNumber.Flat)
        lcd.setStyleSheet("font: 14pt \"MS Shell Dlg 2\";color : blue")

        hbox2.addWidget(self.sld)
        hbox2.addWidget(lcd)
        self.sld.valueChanged.connect(lcd.display)
        
        #napisy do histogramów
        label_down_box = QtGui.QHBoxLayout()
        self.napis3=QtGui.QLabel(u"\nHISTOGRAM WEJŚCIOWY")
        self.napis3.setStyleSheet("font: 14pt \"MS Shell Dlg 2\";")
        self.napis3.setAlignment(QtCore.Qt.AlignCenter)

        self.napis4=QtGui.QLabel(u"\nHISTOGRAM WYJŚCIOWY")
        self.napis4.setStyleSheet("font: 14pt \"MS Shell Dlg 2\";")
        self.napis4.setAlignment(QtCore.Qt.AlignCenter)
        label_down_box.addWidget(self.napis3)
        label_down_box.addWidget(self.napis4)
               
        #dwa dolne okna
        hbox3 = QtGui.QHBoxLayout()
        self.down_left = QtGui.QLabel(self)
        self.down_left.setAlignment(QtCore.Qt.AlignCenter)
        self.down_right = QtGui.QLabel(self)
        self.down_right.setAlignment(QtCore.Qt.AlignCenter)

        hbox3.addWidget(self.down_left)
        hbox3.addWidget(self.down_right)
        
        #Status na dole
        self.stat=QtGui.QStatusBar(self)
        self.stat.showMessage("Gotowy - wczytaj obraz !!!")
        self.sizeLabel = QtGui.QLabel()
        self.sizeLabel.setFrameStyle(QtGui.QFrame.StyledPanel|QtGui.QFrame.Sunken)
        self.stat.addPermanentWidget(self.sizeLabel)

        #layout całości
        vbox = QtGui.QVBoxLayout()
        vbox.addLayout(toolbar_menu)
        vbox.addLayout(label_up_box)
        vbox.addLayout(hbox)
        vbox.addLayout(self.label_slider)
        vbox.addLayout(hbox2)
        vbox.addLayout(label_down_box)
        vbox.addLayout(hbox3)
        vbox.addWidget(self.stat)
        #ustawienie layoutu dla całości
        self.setLayout(vbox)
        vbox.setSizeConstraint(QtGui.QLayout.SetFixedSize)
        #element odpowiedzialny za wyświetlanie grafiki
        #self.scene = QtGui.QGraphicsScene()  
        #self.scene2 = QtGui.QLabel()

        #ładowanie startowego obrazka do wszystkich czterech okienek graficznych
        self.up_left.setPixmap(QtGui.QPixmap('Program_Images/no-photo.jpg'))
        self.up_right.setPixmap(QtGui.QPixmap('Program_Images/no-photo.jpg'))
        self.down_left.setPixmap(QtGui.QPixmap('Program_Images/no-photo.jpg'))
        self.down_right.setPixmap(QtGui.QPixmap('Program_Images/no-photo.jpg'))
        
        #wymiary oraz tytuł
        self.setGeometry(100, 100, 300, 300)
        self.setWindowTitle(u'System analizy rozkładu jasności obrazu')    
        self.show()
        
    #funkcja od menu 'Pomoc->O programie'
    def helpAbout(self):
        QtGui.QMessageBox.about(self, u"O programie",
                u"""<b>System analizy rozkładu jasności obrazu</b> v %s
                <p>Agnieszka Szypuła</p> 
                <p>E-mail: aga.szypula@gmail.com</p>
                <p>Python %s - Qt %s - PyQt %s on %s</p>""" % (
                platform.__version__, platform.python_version(),
                QtCore.QT_VERSION_STR, QtCore.PYQT_VERSION_STR, platform.system()))                       

    #funkcja od menu 'Pomoc->Możliwości programu'
    def helpFeatures(self):
        QtGui.QMessageBox.about(self, u"Możliwości programu",
                u"""<b>Program pozwala na:</b>
                <p>- wczytywanie obrazów i iich przetwarzanie</p> 
                <p>- otrzymywanie histogramów</p>
                <p>- stosowanie wybranych filtrów na obrazach""")                       

    #funkcja od otwierania pliku Plik->Otwórz plik   
    def showDialog(self):
        dir1 = os.path.dirname(self.filename) \
                if self.filename is not None else "."
        formats = ["*.%s" % unicode(format1).lower() \
                   for format1 in QtGui.QImageReader.supportedImageFormats()]
        self.fname = unicode(QtGui.QFileDialog.getOpenFileName(self,
                            u"System analizy obrazów - Wybierz obraz", dir1,
                            u"Pliki obrazów (%s)" % " ".join(formats)))
        if self.fname:
            self.loadFile(self.fname)

    #funkcja od ładowania plików z obrazkami         
    def loadFile(self, fname=None):
        if self.fname is None:
            action = self.sender()
            if isinstance(action, QtGui.QAction):
                self.fname = unicode(action.data().toString())
                if not self.okToContinue():
                    return
                else:
                    return
        if self.fname:
            self.filename = None
            image = QtGui.QImage(self.fname)
        if image.isNull():
            message = u"Błąd odczytu %s" % self.fname
        else:
            #self.addRecentFile(self.fname)
            self.image = QtGui.QImage()
            #for action, check in self.resetableActions:
            #    action.setChecked(check)
            self.image = image
            self.filename = self.fname

            self.showImage()#OK

            #self.dirty = False
            self.sizeLabel.setText("%d x %d" % (image.width(), image.height()))
            message = u"Załadowano %s" % os.path.basename(self.fname)
        self.updateStatus(message)
            
        self.filename = None
        image = QtGui.QImage(self.fname)
        if image.isNull():
            message = u"Błąd odczytu %s" % self.fname
    
    #funkcja od pokazywania obrazków
    def showImage(self, percent=None):
        if self.image.isNull():
            return
        #if self.PIL2qpixmap_image.isNull():
        #    return
        if percent is None:
            percent = self.zoomSpinBox.value() #zoom - dorobić
        #percent=100
        factor = percent / 100.0
        width = self.image.width() * factor
        height = self.image.height() * factor
        image = self.image.scaled(width, height, QtCore.Qt.KeepAspectRatio)
        #PIL2qpixmap_image = self.PIL2qpixmap_image.scaled(width, height, QtCore.Qt.KeepAspectRatio)
        self.up_left.setPixmap(QtGui.QPixmap.fromImage(image)) 
        
        #zamień wczytany obraz na format PIL
        self.image2PIL() #OK
      
        # oblicz histogram wczytanego pliku
        self.plotHistogram(self.pil_image)#OK
        # wyświetl histogram
        self.PIL2qpixmap(self.histogram_image)#OK
        self.down_left.setPixmap(QtGui.QPixmap.fromImage(self.PIL2qpixmap_image)) 

        # zmień wartości pikseli, realizowane na obrazie w formacie PIL
        self.transformImage(self.pil_image)
        #self.PIL2qpixmap(self.PIL2qpixmap_transformed_image)#BAD dla bmp????
        # wyświetl obraz po zmianie wartości pikseli
        #self.PIL2qpixmap(self.histogram_image)#OK
        #self.update()
        
        # wyświetl obraz po transformacji
        self.up_right.setPixmap(QtGui.QPixmap.fromImage(self.PIL2qpixmap_transformed_image))
        
        # oblicz histogram pliku po transformacji
        self.plotHistogram(self.transformed_image)#OK 
        self.PIL2qpixmap(self.histogram_image)#OK
        self.down_right.setPixmap(QtGui.QPixmap.fromImage(self.PIL2qpixmap_image)) 
               
    # funkcja od  pokazywania statusu - na razie nie zdefiniowana                            
    def updateStatus(self, message):
        self.stat.showMessage(message, 5000)   
    
    #funkcja do odwracania pikseli j=255-i
    def editInvert(self):
        if self.image.isNull():
            return
        self.image.invertPixels() #wbudowana funkcja
        self.showImage()
        #self.dirty = True
        #self.updateStatus(u"Odwrócony" if on else u"Odwrócony(z powrotem)")

    #funkcja do filtru medianowego
    def image2PIL(self):
        if self.image.isNull():
            return
        self.bufor=QtCore.QBuffer()
        self.bufor.open(QtCore.QIODevice.ReadWrite)
        self.image.save(self.bufor, "PNG")
        strio = cStringIO.StringIO()
        strio.write(self.bufor.data())
        self.bufor.close()
        strio.seek(0)
        self.pil_image = Image.open(strio) #obraz w formacie PIL
        self.pil_image.save('pil_image.png', 'PNG')
        #test
        #self.pil_image.show() 
        
        
    def plotHistogram(self, pil_image):

        histHeight = 120            # Height of the histogram
        histWidth = 256 
        multiplerValue = 1.0        # The multiplier value basically increases

        #showFstopLines = False       # True/False to hide outline
        #fStopLines = 5
        # kolry do użycia
        #backgroundColor = (51,51,51)    # kolor tła
        #lineColor = (102,102,102)       # kolor linii
        #red = (255,60,60)               # czerwone linie
        #green = (51,204,51)             # zielone linie
        #blue = (0,102,255)              # niebieskie linie
        
        ##################################################################################
        self.hist = pil_image.histogram()
        print self.hist
        histMax = max(self.hist)                                     #comon color
        xScale = float(histWidth)/len(self.hist)                     # xScaling
        yScale = float((histHeight)*multiplerValue)/histMax            # yScaling 
        
        self.histogram_image = Image.new("L", (histWidth, histHeight), 255)   #255 - biały
        draw = ImageDraw.Draw(self.histogram_image)
        # Draw Outline is required
        """if showFstopLines:    
            xmarker = histWidth/fStopLines
            x =0
            for i in range(1,fStopLines+1):
                draw.line((x, 0, x, histHeight), fill=lineColor)
                x+=xmarker
            draw.line((histWidth-1, 0, histWidth-1, 200), fill=lineColor)
            draw.line((0, 0, 0, histHeight), fill=lineColor)
        
       """ 
        # Rysuj histogram
        x=0; c=0;
        for i in self.hist:
            if int(i)==0: pass
            else:
                #color = red
                #if c>255: color = green
                #if c>511: color = blue
                draw.line((x, histHeight, x, histHeight-(i*yScale)), 88)    #0 - czarny    
            if x>255: x=0
            else: x+=1
            c+=1
        
        # Zapisz histogram  
        self.histogram_image.save('histogram.png', 'PNG')

    def transformImage(self, pil_image):
        #self.pil_image.show()
        self.transformed_image = self.pil_image.point(lambda i: i + self.sld.value())
        data_transformed = self.transformed_image.tostring()
        self.PIL2qpixmap_transformed_image = QtGui.QImage(data_transformed, pil_image.size[0],pil_image.size[1],QtGui.QImage.Format_Indexed8)
        self.PIL2qpixmap_transformed_image.save('zmiana_pikseli.png', 'PNG')
        #self.up_right.setPixmap(QtGui.QPixmap.fromImage(self.PIL2qpixmap_transformed_image)) 

    def PIL2qpixmap(self, pil_image):
        #w, h = pil_image.size
        data = pil_image.tostring()
        self.PIL2qpixmap_image = QtGui.QImage(data, pil_image.size[0],pil_image.size[1],QtGui.QImage.Format_Indexed8)
        self.PIL2qpixmap_image.save('PIL2qpixmap.png', 'PNG')
           
def main():
    
    app = QtGui.QApplication([])
    app.setWindowIcon(QtGui.QIcon('Program_Images/icon.png'))

    #mm = MainWindow()
    #mm.show()
    #wywołanie klasy
    sp=SuperProgram()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()    