"""
    This file is part of amc2moodle, a convertion tool to recast quiz written
    with the LaTeX format used by automuliplechoice 1.0.3 into the 
    moodle XML quiz format.
    Copyright (C) 2016  Benoit Nennig, benoit.nennig@supmeca.fr 

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

from amc2moodle import grading
import subprocess
import sys
import os
from importlib import util  # python 3.x
import shutil


def checkTools(show=True):
    """ Check if the required Tools are available.
    """
    # Wand Python module
    wand_loader = util.find_spec('wand') 
    wandOk = wand_loader is not None
    if not wandOk:
        print ("Please install Wand's Python module")
    # lxml Python Module
    lxml_loader = util.find_spec('lxml') 
    lxmlOk = lxml_loader is not None
    if not lxmlOk:
        print ("Please install lxml's Python module")
    # LaTeXML
    latexMLwhich = subprocess.run(['which', 'latexml'],
                                  stdout=subprocess.DEVNULL)
    latexmlOk = latexMLwhich.returncode == 0
    if not latexmlOk:
        print ("Please install LaTeXML software (see https://dlmf.nist.gov/LaTeXML/)")
    # xmlindent
    xmlindentwhich = subprocess.run(['which', 'xmlindent'],
                                    stdout=subprocess.DEVNULL)
    xmlindentOk = xmlindentwhich.returncode == 0
    # if not xmlindentOk:
    #     print ("Please install (optional) XML indent software (see http://xmlindent.sourceforge.net/)")
    #
    return wandOk and lxmlOk and latexmlOk


def getFilename(fileIn):
    """ Get the filename without path.
    """
    return os.path.basename(fileIn)


def getPathFile(fileIn):
    """ Get the path of a file without.
    """
    dirname = os.path.dirname(fileIn)
    if not dirname:
        dirname = '.'
    return dirname


class amc2moodle:
    def __init__(self, fileInput=None, fileOutput=None, keepFile=None,
                 catname=None):
        """ Initialized object
        """
        print('========================')
        print('========================')
        print('=== Start amc2moodle ===')
        print('========================')
        print('========================')
        # default value # TODO move elsewhere
        self.output = None
        self.tempxmlfiledef = 'tex2xml.xml'
        self.tempxmlfile = 'tex2xml.xml'
        self.keepFlag = False
        self.catname = None
        # check required tools
        if not checkTools(show=True):
            sys.exit()
        if fileInput is None:
            print('Input TeX file is missing')
            sys.exit()
        else:
            # load data
            self.input = fileInput
            if fileOutput is not None:
                self.output = fileOutput
            else:
                tmp = os.path.splitext(self.input)
                self.output = tmp[0] + '.xml'
            if keepFile is not None:
                self.keepFlag = keepFile
            if catname is not None:
                self.catname = catname
            else:
                self.catname = self.input
            # temporary file
            self.tempxmlfile = os.path.join(getPathFile(self.input),
                                            self.tempxmlfiledef)
            self.showData()
        #run the building of the xml file for Moodle
        self.runBuilding()

    def showData(self):
        """ Show loaded parameters.
        """
        print('====== Parameters ======')
        print(' > path input TeX: %s' % getPathFile(self.input))
        print(' > input TeX file: %s' % getFilename(self.input))
        print(' > path output TeX: %s' % getPathFile(self.output))
        print(' > output XML file: %s' % getFilename(self.output))
        print(' > temp XML file: %s' % self.tempxmlfile)
        print(' > keep temp files: %s' % self.keepFlag)
        print(' > categorie name: %s' % self.catname)

    def endMessage(self):
        print("""File converted. Check below for errors...

            For import into moodle :
            --------------------------------
            - Go to the course admistration\question bank\import
            - Choose 'moodle XML format'
            - In the option chose : 'choose the closest grade if not listed'
              in the 'General option' since Moodle used tabulated grades 
              like 1/2, 1/3 etc...
        """)

    def runLaTeXML(self):
        """ Run LaTeXML on the input TeX file.
        """
        # run LaTeXML
        print(' > Running LaTeXML conversion')
        subprocess.run([
            'latexml',
            '--noparse',
            '--nocomments',
            '--path=%s' % os.path.dirname(__file__),
            '--dest=%s' % self.tempxmlfile,
            self.input])

    def runXMLindent(self):
        """ Build the xml file for Moodle quizz.
        """
        # check for xmlindent
        xmlindentwhich = subprocess.run(['which', 'xmlindent'])
        xmlindentOk = xmlindentwhich.returncode == 0

        if xmlindentOk:
            subprocess.run(['xmlindent', self.output,'-o', self.output])

    def runBuilding(self):
        """ Build the xml file for Moodle quizz.
        """
        print('====== Build XML =======')
        self.runLaTeXML()
        # run script
        print(' > Running Python conversion')
        grading.grading(
            inputfile=getFilename(self.tempxmlfile),
            inputdir=getPathFile(self.input),
            outputfile=getFilename(self.output),
            outputdir=getPathFile(self.input),
            keepFlag=self.keepFlag,
            incatname=self.catname
        )
        # remove temporary file
        if not self.keepFlag:
            print(' > Remove temp file: %s' % self.tempxmlfile)
            os.remove(self.tempxmlfile)
        # run XMLindent
        # self.runXMLindent()
        # copy file from working dir to outputdir
        # TODO need to check
        if getPathFile(self.input) != '.':
            if os.path.join(getPathFile(self.input),
                            getFilename(self.output)) != self.output:
                shutil.copyfile(os.path.join(getPathFile(self.input), getFilename(self.output)),
                                self.output)
        self.endMessage()
