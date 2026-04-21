import Metashape
import os
from PySide2 import QtWidgets

app = Metashape.app

QUALITY_MAP = {
    "Very High": 1,
    "High": 2,
    "Medium": 4,
    "Low": 8,
    "Lowest": 16
}


class ProcessingDialog(QtWidgets.QDialog):

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Wizard")
        self.setMinimumWidth(520)

        layout = QtWidgets.QVBoxLayout(self)


        cam_group = QtWidgets.QGroupBox("Kamery")
        cam_layout = QtWidgets.QVBoxLayout(cam_group)

        self.photos_btn = QtWidgets.QPushButton("Wybierz folder ze zdjęciami")
        self.photos_lbl = QtWidgets.QLabel("-")

        self.cam_crs_btn = QtWidgets.QPushButton("Wybierz CRS kamer")
        self.cam_crs_lbl = QtWidgets.QLabel("-")

        cam_layout.addWidget(self.photos_btn)
        cam_layout.addWidget(self.photos_lbl)
        cam_layout.addWidget(self.cam_crs_btn)
        cam_layout.addWidget(self.cam_crs_lbl)

        layout.addWidget(cam_group)


        osn_group = QtWidgets.QGroupBox("Osnowa")
        osn_layout = QtWidgets.QVBoxLayout(osn_group)

        self.osn_btn = QtWidgets.QPushButton("Wybierz plik osnowy (.txt)")
        self.osn_lbl = QtWidgets.QLabel("-")

        self.osn_crs_btn = QtWidgets.QPushButton("Wybierz CRS")
        self.osn_crs_lbl = QtWidgets.QLabel("-")

        osn_layout.addWidget(self.osn_btn)
        osn_layout.addWidget(self.osn_lbl)
        osn_layout.addWidget(self.osn_crs_btn)
        osn_layout.addWidget(self.osn_crs_lbl)

        layout.addWidget(osn_group)


        final_group = QtWidgets.QGroupBox("CRS wynikowy")
        final_layout = QtWidgets.QVBoxLayout(final_group)

        self.final_crs_btn = QtWidgets.QPushButton("Wybierz CRS wynikowy")
        self.final_crs_lbl = QtWidgets.QLabel("-")

        final_layout.addWidget(self.final_crs_btn)
        final_layout.addWidget(self.final_crs_lbl)

        layout.addWidget(final_group)


        proc_group = QtWidgets.QGroupBox("Przetwarzanie")
        proc_layout = QtWidgets.QVBoxLayout(proc_group)

        self.quality_combo = QtWidgets.QComboBox()
        self.quality_combo.addItems(QUALITY_MAP.keys())

        self.chk_align = QtWidgets.QCheckBox("Orientacja zdjęć (SfM)")
        self.chk_dense = QtWidgets.QCheckBox("Chmura punktów")
        self.chk_model = QtWidgets.QCheckBox("Model 3D + tekstura")

        self.chk_align.setChecked(True)
        self.chk_dense.setChecked(True)
        self.chk_model.setChecked(True)

        proc_layout.addWidget(QtWidgets.QLabel("Jakość:"))
        proc_layout.addWidget(self.quality_combo)
        proc_layout.addWidget(self.chk_align)
        proc_layout.addWidget(self.chk_dense)
        proc_layout.addWidget(self.chk_model)

        layout.addWidget(proc_group)


        btn_layout = QtWidgets.QHBoxLayout()
        self.run_btn = QtWidgets.QPushButton("START")
        self.cancel_btn = QtWidgets.QPushButton("ANULUJ")

        btn_layout.addWidget(self.run_btn)
        btn_layout.addWidget(self.cancel_btn)
        layout.addLayout(btn_layout)


        self.photos_dir = None
        self.osn_file = None
        self.camera_crs = None
        self.osn_input_crs = None
        self.final_crs = None


        self.photos_btn.clicked.connect(self.select_photos)
        self.osn_btn.clicked.connect(self.select_osn)
        self.cam_crs_btn.clicked.connect(self.select_cam_crs)
        self.osn_crs_btn.clicked.connect(self.select_osn_crs)
        self.final_crs_btn.clicked.connect(self.select_final_crs)

        self.run_btn.clicked.connect(self.accept)
        self.cancel_btn.clicked.connect(self.reject)

    def select_photos(self):
        self.photos_dir = app.getExistingDirectory("Folder ze zdjęciami")
        self.photos_lbl.setText(self.photos_dir or "-")

    def select_osn(self):
        self.osn_file = app.getOpenFileName("Plik Osnowy", filter="*.txt")
        self.osn_lbl.setText(self.osn_file or "-")

    def select_cam_crs(self):
        self.camera_crs = app.getCoordinateSystem("CRS kamer")
        if self.camera_crs:
            self.cam_crs_lbl.setText(self.camera_crs.name)

    def select_osn_crs(self):
        self.osn_input_crs = app.getCoordinateSystem("CRS Osnowy")
        if self.osn_input_crs:
            self.osn_crs_lbl.setText(self.osn_input_crs.name)

    def select_final_crs(self):
        self.final_crs = app.getCoordinateSystem("CRS wynikowy")
        if self.final_crs:
            self.final_crs_lbl.setText(self.final_crs.name)

    def get_params(self):
        return {
            "photos_dir": self.photos_dir,
            "osn_file": self.osn_file,
            "camera_crs": self.camera_crs,
            "osn_input_crs": self.osn_input_crs,
            "final_crs": self.final_crs,
            "downscale": QUALITY_MAP[self.quality_combo.currentText()],
            "do_align": self.chk_align.isChecked(),
            "do_dense": self.chk_dense.isChecked(),
            "do_model": self.chk_model.isChecked()
        }


def get_or_create_chunk():
    doc = Metashape.app.document

    if doc.chunk and len(doc.chunk.cameras) > 0:
        reply = QtWidgets.QMessageBox.question(
            None,
            "Zdjęcia już istnieją",
            "W projekcie są już wczytane zdjęcia.\nCzy chcesz pracować na nich?",
            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No
        )
        if reply == QtWidgets.QMessageBox.Yes:
            return doc.chunk
        else:
            return doc.addChunk()
    else:
        return doc.addChunk()



def run_processing(p):

    doc = Metashape.app.document
    chunk = get_or_create_chunk()

    chunk.crs = p["final_crs"]
    chunk.camera_crs = p["camera_crs"]


    if len(chunk.cameras) == 0:
        photos = [
            os.path.join(p["photos_dir"], f)
            for f in os.listdir(p["photos_dir"])
            if f.lower().endswith((".jpg", ".jpeg", ".tif", ".tiff"))
        ]
        chunk.addPhotos(photos)


    if p["do_align"]:
        chunk.matchPhotos(
            downscale=p["downscale"],
            generic_preselection=True,
            reference_preselection=False
        )
        chunk.alignCameras()


    imported_markers = []
    if p["osn_file"]:
        with open(p["osn_file"], "r") as f:
            for line in f:
                parts = line.split()
                if len(parts) < 4:
                    continue

                name = parts[0]
                x, y, z = map(float, parts[1:4])


                loc = Metashape.Vector([y, x, z])

                if p["osn_input_crs"] != p["final_crs"]:
                    loc = Metashape.CoordinateSystem.transform(
                        loc, p["osn_input_crs"], p["final_crs"]
                    )

                m = chunk.addMarker()
                m.label = name
                m.reference.location = loc
                m.reference.enabled = True
                imported_markers.append(m)

    chunk.detectMarkers(
        target_type=Metashape.TargetType.CrossTarget,
        tolerance=10,
        merge_markers=False
    )

    
    if imported_markers and chunk.transform.matrix and chunk.crs:
        
        detected_markers = [m for m in chunk.markers if m not in imported_markers and m.position is not None]
        matched_detected = set()

        for m_import in imported_markers:
            loc = m_import.reference.location
            best_dist = float('inf')
            best_m = None

            for m_det in detected_markers:
                if m_det in matched_detected:
                    continue
                
                
                pos_crs = chunk.crs.project(chunk.transform.matrix.mulp(m_det.position))
                
                
                dist_3d = (pos_crs - loc).norm()
                
                if dist_3d < best_dist:
                    best_dist = dist_3d
                    best_m = m_det

            
            if best_m and best_dist < 30.0:
               
                best_m.label = m_import.label
                best_m.reference.location = m_import.reference.location
                best_m.reference.enabled = True
                matched_detected.add(best_m)
                
                
                chunk.remove(m_import) 
            

        to_remove = [m for m in detected_markers if m not in matched_detected]
        for m_det in to_remove:
            chunk.remove(m_det)
       

    chunk.updateTransform()

    chunk.optimizeCameras(
        fit_f=True,
        fit_cx=True,
        fit_cy=True,
        fit_k1=True,
        fit_k2=True,
        fit_k3=True,
        fit_p1=True,
        fit_p2=True,
        adaptive_fitting=True
    )


    if p["do_dense"]:
        chunk.buildDepthMaps(
            downscale=p["downscale"],
            filter_mode=Metashape.MildFiltering
        )
        chunk.buildPointCloud(
            source_data=Metashape.DepthMapsData,
            point_colors=True,
            point_confidence=True
        )


    if p["do_model"]:
        chunk.buildModel(
            source_data=Metashape.DepthMapsData,
            surface_type=Metashape.Arbitrary,
            interpolation=Metashape.EnabledInterpolation,
            face_count=Metashape.MediumFaceCount,
            build_texture=True
        )


    eo_txt = "Label X Y Z Omega Phi Kappa\n"
    for cam in chunk.cameras:
        if not cam.transform:
            continue

        c = cam.center

        R_w2c = cam.transform.rotation()
        R_c2w = R_w2c.t()
        opk = Metashape.utils.mat2opk(R_c2w)

        eo_txt += (
            f"{cam.label} "
            f"{c.x:.3f} {c.y:.3f} {c.z:.3f} "
            f"{opk.x:.6f} {opk.y:.6f} {opk.z:.6f}\n"
        )

    eo_path = os.path.join(p["photos_dir"], "EO.txt")
    with open(eo_path, "w") as f:
        f.write(eo_txt)


    doc.save(os.path.join(p["photos_dir"], "projekt.psx"))



def start_gui():
    dlg = ProcessingDialog()
    if dlg.exec_():
        run_processing(dlg.get_params())

try:
    app.removeMenuItem("Wizard/Wizard")
except:
    pass

app.addMenuItem("Wizard/Wizard", start_gui)