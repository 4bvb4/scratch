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
        self.clear_roi_button.clicked.connect(self.clear_roi)
        self.transpose_button.clicked.connect(self.transpose_data)
        self.convert_button.clicked.connect(self.convert_and_save)

        control_layout.addWidget(self.nrrd_label)
        control_layout.addWidget(self.nrrd_button)
        control_layout.addWidget(self.nifti_label)
        control_layout.addWidget(self.nifti_button)
        control_layout.addWidget(self.roi_label)
        control_layout.addWidget(self.roi_button)
        control_layout.addWidget(self.clear_roi_button)
        control_layout.addWidget(self.transpose_button)
        control_layout.addWidget(self.convert_button)

        main_layout.addLayout(control_layout)

        # --- Viewers and Plots ---
        self.splitter_main = QSplitter(Qt.Vertical)
        self.splitter_top = QSplitter(Qt.Horizontal)
        self.splitter_bottom = QSplitter(Qt.Horizontal)

        self.nrrd_viewer = pg.ImageView()
        self.nifti_viewer = pg.ImageView()
        self.nrrd_plot = pg.PlotWidget(title="NRRD Central Line")
        self.nifti_plot = pg.PlotWidget(title="NIfTI Central Line")

        self.splitter_top.addWidget(self.nrrd_viewer)
        self.splitter_top.addWidget(self.nifti_viewer)
        self.splitter_bottom.addWidget(self.nrrd_plot)
        self.splitter_bottom.addWidget(self.nifti_plot)

        self.splitter_main.addWidget(self.splitter_top)
        self.splitter_main.addWidget(self.splitter_bottom)
        main_layout.addWidget(self.splitter_main)

        # Connect slice scroll events
        self.nrrd_viewer.timeLine.sigPositionChanged.connect(self.update_nrrd_overlay_slice)
        self.nifti_viewer.timeLine.sigPositionChanged.connect(self.update_nifti_overlay_slice)

    def select_nrrd_file(self):
        path, _ = QFileDialog.getOpenFileName(self, "Select NRRD File", "", "NRRD files (*.nrrd)")
        if path:
            self.nrrd_file = path
            self.nrrd_label.setText(f"NRRD: {os.path.basename(path)}")
            self.nrrd_data, self.header = nrrd.read(path)
            self.update_views()

    def select_nifti_file(self):
        path, _ = QFileDialog.getOpenFileName(self, "Select NIfTI File", "", "NIfTI files (*.nii *.nii.gz)")
        if path:
            self.nifti_file = path
            self.nifti_label.setText(f"NIfTI: {os.path.basename(path)}")
            g = nib.load(path).get_fdata()
            self.nifti_data = np.transpose(np.transpose(g, [2, 0, 1])[:, :, ::-1])
            self.update_views()

    def select_roi_file(self):
        path, _ = QFileDialog.getOpenFileName(self, "Select ROI NRRD File", "", "NRRD files (*.nrrd)")
        if path:
            self.roi_file = path
            self.roi_label.setText(f"ROI: {os.path.basename(path)}")
            try:
                roi_data, _ = nrrd.read(path)
                self.roi_data = roi_data.astype(np.uint8)
                self.update_views()
            except Exception as e:
                QMessageBox.critical(self, "Error reading ROI", str(e))

    def clear_roi(self):
        self.roi_data = None
        self.update_views()

    def transpose_data(self):
        self.transpose_state = (self.transpose_state + 1) % 3
        self.update_views()

    def apply_orientation(self, data):
        if self.transpose_state == 0:
            return data
        elif self.transpose_state == 1:
            return np.transpose(data, (1, 2, 0))
        elif self.transpose_state == 2:
            return np.transpose(data, (2, 0, 1))

    def get_overlay_image(self, roi_volume, index):
        overlay = np.zeros((*roi_volume.shape[1:], 4), dtype=np.uint8)
        if index >= roi_volume.shape[0]:
            return overlay
        slice_roi = roi_volume[index]
        overlay[..., 0] = 255       # Red
        overlay[..., 3] = slice_roi * 100
        return overlay

    def update_views(self):
        if self.nrrd_data is not None:
            vol = self.apply_orientation(self.nrrd_data)
            self.nrrd_viewer.setImage(vol, xvals=np.arange(vol.shape[0]))
            self.update_nrrd_overlay_slice()
            mid_idx = vol.shape[0] // 2
            slice_img = vol[mid_idx]
            central_line = slice_img[slice_img.shape[0] // 2, :]
            self.nrrd_plot.clear()
            self.nrrd_plot.plot(central_line, pen='b')

        if self.nifti_data is not None:
            vol = self.apply_orientation(self.nifti_data)
            self.nifti_viewer.setImage(vol, xvals=np.arange(vol.shape[0]))
            self.update_nifti_overlay_slice()
            mid_idx = vol.shape[0] // 2
            slice_img = vol[mid_idx]
            central_line = slice_img[slice_img.shape[0] // 2, :]
            self.nifti_plot.clear()
            self.nifti_plot.plot(central_line, pen='r')

    def update_nrrd_overlay_slice(self):
        if self.roi_data is None:
            return
        if self.nrrd_overlay:
            self.nrrd_viewer.view.removeItem(self.nrrd_overlay)
        roi_vol = self.apply_orientation(self.roi_data)
        slice_idx = int(round(self.nrrd_viewer.currentIndex))
        overlay_img = self.get_overlay_image(roi_vol, slice_idx)
        self.nrrd_overlay = pg.ImageItem(overlay_img)
        self.nrrd_viewer.view.addItem(self.nrrd_overlay)

    def update_nifti_overlay_slice(self):
        if self.roi_data is None:
            return
        if self.nifti_overlay:
            self.nifti_viewer.view.removeItem(self.nifti_overlay)
        roi_vol = self.apply_orientation(self.roi_data)
        slice_idx = int(round(self.nifti_viewer.currentIndex))
        overlay_img = self.get_overlay_image(roi_vol, slice_idx)
        self.nifti_overlay = pg.ImageItem(overlay_img)
        self.nifti_viewer.view.addItem(self.nifti_overlay)

    def convert_and_save(self):
        if self.header is None or self.nifti_data is None:
            QMessageBox.warning(self, "Missing Data", "Load both NRRD and NIfTI files first.")
            return
        try:
            base_dir = os.path.dirname(self.nrrd_file)
            suggested_path = os.path.join(base_dir, "newfile.nrrd")
            nrrd.write(suggested_path, self.nifti_data, self.header)
            QMessageBox.information(self, "Saved", f"Saved as:\n{suggested_path}")
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = NiftiToNrrdConverter()
    window.show()
    sys.exit(app.exec_())
