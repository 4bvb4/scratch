import sys
import os
import numpy as np
import nibabel as nib
import nrrd
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QPushButton,
    QFileDialog, QLabel, QMessageBox, QHBoxLayout
)
import pyqtgraph as pg

class NiftiToNrrdConverter(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("NIfTI to NRRD Converter")

        self.nrrd_file = None
        self.nifti_file = None
        self.header = None

        self.nrrd_data = None
        self.nifti_data = None

        # UI Elements
        layout = QVBoxLayout()
        self.nrrd_label = QLabel("No NRRD file selected")
        self.nifti_label = QLabel("No NIfTI file selected")

        self.nrrd_button = QPushButton("Select NRRD Header File")
        self.nrrd_button.clicked.connect(self.select_nrrd_file)

        self.nifti_button = QPushButton("Select NIfTI File")
        self.nifti_button.clicked.connect(self.select_nifti_file)

        self.convert_button = QPushButton("Convert and Save as NRRD")
        self.convert_button.clicked.connect(self.convert_and_save)

        # Image viewers
        self.viewer_layout = QHBoxLayout()
        self.nrrd_viewer = pg.ImageView()
        self.nifti_viewer = pg.ImageView()

        self.viewer_layout.addWidget(self.nrrd_viewer)
        self.viewer_layout.addWidget(self.nifti_viewer)

        layout.addWidget(self.nrrd_label)
        layout.addWidget(self.nrrd_button)
        layout.addWidget(self.nifti_label)
        layout.addWidget(self.nifti_button)
        layout.addWidget(self.convert_button)
        layout.addLayout(self.viewer_layout)

        self.setLayout(layout)

    def select_nrrd_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select NRRD File", "", "NRRD files (*.nrrd)")
        if file_path:
            self.nrrd_file = file_path
            self.nrrd_label.setText(f"NRRD: {file_path}")
            try:
                self.nrrd_data, self.header = nrrd.read(file_path)
                middle_slice = self.nr_
