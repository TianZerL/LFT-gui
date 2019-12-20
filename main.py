#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
from PyQt5.QtWidgets import QApplication
from widget import LFTWidget

if __name__ == "__main__":
    app = QApplication(sys.argv)
    mainWidget = LFTWidget()
    mainWidget.show()
    sys.exit(app.exec())
