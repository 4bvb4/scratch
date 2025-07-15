import sys
import os
import numpy as np
import nibabel as nib
import nrrd
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QPushButton,
    QFileDialog, QLabel, QMessageBox, QHBoxLayout,
    QSplitter
)
from PyQt5.QtCore import Qt
import pyqtgraph as pg


class NiftiToNrrdConverter(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("NIfTI to NRRD Converter")
        self.setMinimumSize(1200, 800)

        # File data
        self.nrrd_file = None
        self.nifti_file = None
        self.roi_file = None
        self.header = None

        self.nrrd_data = None
        self.nifti_data = None
        self.roi_data = None

        self.transpose_state = 0  # (0, 1, 2)

        # To hold overlay items
        self.nrrd_overlay = None
        self.nifti_overlay = None

        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout(self)

        # --- Control Panel ---
        control_layout = QHBoxLayout()
        self.nrrd_label = QLabel("No NRRD file")
        self.nifti_label = QLabel("No NIfTI file")
        self.roi_label = QLabel("No ROI file")

        self.nrrd_button = QPushButton("Select NRRD Header")
        self.nifti_button = QPushButton("Select NIfTI File")
        self.roi_button = QPushButton("Select ROI NRRD")
        self.clear_roi_button = QPushButton("Clear ROI")
        self.transpose_button = QPushButton("Transpose View")
        self.convert_button = QPushButton("Convert and Save")

        self.nrrd_button.clicked.connect(self.select_nrrd_file)
        self.nifti_button.clicked.connect(self.select_nifti_file)
        self.roi_button.clicked.connect(self.select_roi_file)
        self.clear_roi_button.clicke
