import os
import sys
import shlex
import queue
import threading
import subprocess
from pathlib import Path

from PyQt5.QtCore import Qt, QProcess, QTimer
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QLabel, QLineEdit, QPushButton,
    QFileDialog, QRadioButton, QCheckBox, QTextEdit, QProgressBar,
    QVBoxLayout, QHBoxLayout, QGridLayout, QGroupBox, QMessageBox, QFrame,
    QScrollArea
)


APP_STYLE = """
QWidget {
    background: #0b1020;
    color: #e5e7eb;
    font-family: 'Segoe UI';
    font-size: 10pt;
}
QMainWindow { background: #0b1020; }
QLabel#Title { font-size: 25pt; font-weight: 700; color: #f8fafc; }
QLabel#Subtitle { color: #94a3b8; font-size: 10pt; }
QGroupBox {
    background: #131b2e;
    border: 1px solid #26334c;
    border-radius: 12px;
    margin-top: 14px;
    padding: 15px 12px 12px 12px;
    font-weight: 700;
    color: #93c5fd;
}
QGroupBox::title { subcontrol-origin: margin; left: 14px; padding: 0 6px; }
QLineEdit, QComboBox {
    background: #0f172a;
    border: 1px solid #334155;
    border-radius: 7px;
    min-height: 22px;
    padding: 6px 9px;
    selection-background-color: #6366f1;
    color: #f8fafc;
}
QLineEdit:focus, QComboBox:focus { border: 1px solid #818cf8; }
QComboBox QAbstractItemView {
    background: #111827;
    color: #f8fafc;
    selection-background-color: #4f46e5;
}
QPushButton {
    background: #243047;
    border: 1px solid #334155;
    border-radius: 8px;
    min-height: 20px;
    padding: 8px 13px;
    color: #e5e7eb;
    font-weight: 600;
}
QPushButton:hover { background: #334155; }
QPushButton:pressed { background: #1e293b; }
QPushButton#Primary {
    background: #6366f1;
    border: 1px solid #818cf8;
    color: white;
    padding: 11px 17px;
}
QPushButton#Primary:hover { background: #4f46e5; }
QPushButton:disabled { background: #293246; color: #8290a5; }
QCheckBox, QRadioButton { spacing: 8px; color: #dbeafe; }
QCheckBox::indicator, QRadioButton::indicator { width: 16px; height: 16px; }
QTextEdit {
    background: #080d18;
    border: 1px solid #26334c;
    border-radius: 9px;
    padding: 9px;
    color: #d1d5db;
    selection-background-color: #4f46e5;
    font-family: Consolas, monospace;
    font-size: 9pt;
}
QProgressBar {
    background: #1e293b;
    border: none;
    border-radius: 5px;
    height: 9px;
    text-align: center;
}
QProgressBar::chunk { background: #6366f1; border-radius: 5px; }
"""


class PythonExeStudio(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Python EXE Studio")
        self.resize(1120, 820)
        self.setMinimumSize(940, 700)
        self.process = None
        self.process_phase = None
        self.current_command = []

        self.source_edit = QLineEdit()
        self.output_edit = QLineEdit(str(Path.cwd() / "dist"))
        self.icon_edit = QLineEdit()
        self.python_edit = QLineEdit(sys.executable)
        self.name_edit = QLineEdit()
        for line_edit in (
            self.source_edit, self.output_edit, self.icon_edit,
            self.python_edit, self.name_edit
        ):
            line_edit.setMinimumHeight(38)
        self.mode_one = QRadioButton("Single EXE")
        self.mode_folder = QRadioButton("Folder build")
        self.mode_one.setChecked(True)
        self.windowed_check = QCheckBox("Windowed application (hide console)")
        self.windowed_check.setChecked(True)
        self.clean_check = QCheckBox("Clean previous build files")
        self.clean_check.setChecked(True)
        self.preview = QTextEdit()
        self.preview.setReadOnly(True)
        self.preview.setMaximumHeight(105)
        self.log = QTextEdit()
        self.log.setReadOnly(True)
        self.status_label = QLabel("Ready to build")
        self.progress = QProgressBar()
        self.progress.setRange(0, 0)
        self.progress.hide()

        self._create_ui()
        self.setStyleSheet(APP_STYLE)
        self._connect_signals()
        self._update_preview()
        self._log("Welcome to Python EXE Studio.\n", "info")
        self._log("Select a .py file and click Build EXE. PyInstaller is set up automatically if needed.\n")

    def _create_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        root = QVBoxLayout(central)
        root.setContentsMargins(26, 22, 26, 18)
        root.setSpacing(13)

        title = QLabel("Python EXE Studio")
        title.setObjectName("Title")
        subtitle = QLabel("A desktop builder that packages Python scripts as Windows executables")
        subtitle.setObjectName("Subtitle")
        root.addWidget(title)
        root.addWidget(subtitle)

        columns = QHBoxLayout()
        columns.setSpacing(16)
        root.addLayout(columns, 1)

        config_box = QGroupBox("BUILD CONFIGURATION")
        config_grid = QGridLayout(config_box)
        config_grid.setHorizontalSpacing(9)
        config_grid.setVerticalSpacing(11)
        config_grid.addWidget(QLabel("Python source (.py)"), 0, 0, 1, 2)
        config_grid.addWidget(self.source_edit, 1, 0)
        config_grid.addWidget(self._button("Browse", self._browse_source), 1, 1)

        config_grid.addWidget(QLabel("Output folder"), 2, 0, 1, 2)
        config_grid.addWidget(self.output_edit, 3, 0)
        config_grid.addWidget(self._button("Browse", self._browse_output), 3, 1)

        config_grid.addWidget(QLabel("Application icon (.ico) — optional"), 4, 0, 1, 2)
        config_grid.addWidget(self.icon_edit, 5, 0)
        config_grid.addWidget(self._button("Browse", self._browse_icon), 5, 1)

        config_grid.addWidget(QLabel("Build engine: PyInstaller (installed automatically)"), 6, 0, 1, 2)

        config_grid.addWidget(QLabel("Executable name"), 7, 0, 1, 2)
        config_grid.addWidget(self.name_edit, 8, 0, 1, 2)

        mode_row = QHBoxLayout()
        mode_row.addWidget(self.mode_one)
        mode_row.addWidget(self.mode_folder)
        mode_row.addStretch()
        config_grid.addWidget(QLabel("Packaging mode"), 9, 0, 1, 2)
        config_grid.addLayout(mode_row, 10, 0, 1, 2)
        config_grid.addWidget(self.windowed_check, 11, 0, 1, 2)
        config_grid.addWidget(self.clean_check, 12, 0, 1, 2)

        config_grid.addWidget(QLabel("Python interpreter"), 13, 0, 1, 2)
        config_grid.addWidget(self.python_edit, 14, 0)
        config_grid.addWidget(self._button("Browse", self._browse_python), 14, 1)

        action_row = QHBoxLayout()
        self.build_button = self._button("▶  Build EXE", self._start_build, primary=True)
        self.stop_button = self._button("■  Stop", self._stop_build)
        self.stop_button.setEnabled(False)
        self.open_button = self._button("Open output", self._open_output)
        action_row.addWidget(self.build_button)
        action_row.addWidget(self.stop_button)
        action_row.addStretch()
        action_row.addWidget(self.open_button)
        config_grid.addLayout(action_row, 15, 0, 1, 2)

        config_scroll = QScrollArea()
        config_scroll.setWidgetResizable(True)
        config_scroll.setFrameShape(QFrame.NoFrame)
        config_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        config_scroll.setWidget(config_box)

        right_layout = QVBoxLayout()
        right_layout.setSpacing(12)
        preview_box = QGroupBox("COMMAND PREVIEW")
        pv = QVBoxLayout(preview_box)
        pv.addWidget(self.preview)
        log_box = QGroupBox("BUILD LOG")
        ll = QVBoxLayout(log_box)
        ll.addWidget(self.log)
        right_layout.addWidget(preview_box)
        right_layout.addWidget(log_box, 1)

        columns.addWidget(config_scroll, 5)
        columns.addLayout(right_layout, 5)

        root.addWidget(self.progress)
        root.addWidget(self.status_label)

    def _button(self, text, callback, primary=False):
        b = QPushButton(text)
        if primary:
            b.setObjectName("Primary")
        b.clicked.connect(callback)
        return b

    def _connect_signals(self):
        for widget in (self.source_edit, self.output_edit, self.icon_edit, self.python_edit, self.name_edit):
            widget.textChanged.connect(self._update_preview)
        self.mode_one.toggled.connect(self._update_preview)
        self.mode_folder.toggled.connect(self._update_preview)
        self.windowed_check.toggled.connect(self._update_preview)
        self.clean_check.toggled.connect(self._update_preview)

    def _browse_source(self):
        path, _ = QFileDialog.getOpenFileName(self, "Choose Python source", "", "Python files (*.py);;All files (*)")
        if path:
            self.source_edit.setText(path)
            if not self.name_edit.text().strip():
                self.name_edit.setText(Path(path).stem)

    def _browse_output(self):
        path = QFileDialog.getExistingDirectory(self, "Choose output folder", self.output_edit.text())
        if path:
            self.output_edit.setText(path)

    def _browse_icon(self):
        path, _ = QFileDialog.getOpenFileName(self, "Choose icon", "", "Icon files (*.ico)")
        if path:
            self.icon_edit.setText(path)

    def _browse_python(self):
        path, _ = QFileDialog.getOpenFileName(self, "Choose Python interpreter", "", "Python executable (python.exe);;Executables (*.exe)")
        if path:
            self.python_edit.setText(path)

    def _command(self):
        source = self.source_edit.text().strip().strip('"')
        output = self.output_edit.text().strip().strip('"') or str(Path.cwd() / "dist")
        icon = self.icon_edit.text().strip().strip('"')
        name = self.name_edit.text().strip() or (Path(source).stem if source else "application")
        python = self.python_edit.text().strip().strip('"') or sys.executable
        onefile = self.mode_one.isChecked()
        cmd = [python, "-m", "PyInstaller", "--noconfirm"]
        if self.clean_check.isChecked():
            cmd.append("--clean")
        cmd.append("--onefile" if onefile else "--onedir")
        if self.windowed_check.isChecked():
            cmd.append("--windowed")
        cmd += ["--name", name, "--distpath", output, "--workpath", str(Path(output) / "_build"), "--specpath", str(Path(output) / "_spec")]
        if icon:
            cmd += ["--icon", icon]
        if source:
            cmd.append(source)
        return cmd

    def _update_preview(self, *_):
        cmd = self._command()
        self.current_command = cmd
        self.preview.setPlainText(subprocess.list2cmdline(cmd) if os.name == "nt" else shlex.join(cmd))

    def _start_build(self):
        source = Path(self.source_edit.text().strip().strip('"'))
        python = Path(self.python_edit.text().strip().strip('"'))
        icon = self.icon_edit.text().strip().strip('"')
        if not self.source_edit.text().strip():
            QMessageBox.warning(self, "Source required", "Select the Python .py file you want to build.")
            return
        if not source.is_file():
            QMessageBox.critical(self, "Source not found", f"File not found:\n{source}")
            return
        if not python.is_file():
            QMessageBox.critical(self, "Python not found", f"Interpreter not found:\n{python}")
            return
        if icon and not Path(icon).is_file():
            QMessageBox.critical(self, "Icon not found", "The selected icon file does not exist.")
            return
        output = Path(self.output_edit.text().strip().strip('"') or (Path.cwd() / "dist"))
        try:
            output.mkdir(parents=True, exist_ok=True)
        except OSError as exc:
            QMessageBox.critical(self, "Output error", str(exc))
            return
        try:
            engine_check = subprocess.run(
                [
                    str(python), "-c",
                    "import importlib.util, sys; "
                    "sys.exit(importlib.util.find_spec(sys.argv[1]) is None)",
                    "PyInstaller",
                ],
                capture_output=True,
                text=True,
                timeout=10,
            )
        except (OSError, subprocess.TimeoutExpired) as exc:
            QMessageBox.critical(
                self,
                "Could not check build engine",
                f"Could not verify PyInstaller with the selected Python interpreter:\n{exc}",
            )
            return
        if engine_check.returncode not in (0, 1):
            details = engine_check.stderr.strip() or engine_check.stdout.strip()
            QMessageBox.critical(
                self,
                "Python interpreter error",
                "The selected Python could not check for PyInstaller."
                + (f"\n\n{details}" if details else ""),
            )
            return
        if engine_check.returncode != 0:
            self._log(
                f"\nPyInstaller is not installed in {python}.\n"
                "Installing it automatically; this requires an internet connection.\n\n",
                "info",
            )
            self.build_button.setEnabled(False)
            self.stop_button.setEnabled(True)
            self.progress.show()
            self.status_label.setText("Installing PyInstaller…")
            self.process = QProcess(self)
            self.process_phase = "install"
            self.process.setWorkingDirectory(str(source.parent))
            self.process.setProgram(str(python))
            self.process.setArguments([
                "-m", "pip", "install", "--disable-pip-version-check", "pyinstaller"
            ])
            self.process.setProcessChannelMode(QProcess.MergedChannels)
            self.process.readyReadStandardOutput.connect(self._read_output)
            self.process.finished.connect(self._build_finished)
            self.process.errorOccurred.connect(self._process_error)
            self.process.start()
            return

        self._launch_build(source)

    def _launch_build(self, source):
        self._log("\n" + "=" * 60 + "\n", "info")
        self._log("Starting build:\n" + self.preview.toPlainText() + "\n\n", "info")
        self.build_button.setEnabled(False)
        self.stop_button.setEnabled(True)
        self.progress.show()
        self.status_label.setText("Building…")
        self.process = QProcess(self)
        self.process_phase = "build"
        self.process.setWorkingDirectory(str(source.parent))
        self.process.setProgram(self.current_command[0])
        self.process.setArguments(self.current_command[1:])
        self.process.setProcessChannelMode(QProcess.MergedChannels)
        self.process.readyReadStandardOutput.connect(self._read_output)
        self.process.finished.connect(self._build_finished)
        self.process.errorOccurred.connect(self._process_error)
        self.process.start()

    def _read_output(self):
        if self.process:
            data = bytes(self.process.readAllStandardOutput()).decode("utf-8", errors="replace")
            self._log(data, "error" if "error" in data.lower() or "traceback" in data.lower() else None)

    def _build_finished(self, exit_code, exit_status):
        self._read_output()
        if self.process_phase == "install":
            self.process = None
            if exit_code == 0:
                self._log("\nPyInstaller installed successfully. Starting build…\n", "success")
                source = Path(self.source_edit.text().strip().strip('"'))
                self._launch_build(source)
                return
            self.progress.hide()
            self.build_button.setEnabled(True)
            self.stop_button.setEnabled(False)
            self.status_label.setText(f"PyInstaller installation failed (exit code {exit_code})")
            self._log(
                f"\nPyInstaller installation failed (exit code {exit_code}).\n"
                "Check your internet connection and ensure pip is available for the selected Python.\n",
                "error",
            )
            self.process_phase = None
            return
        self.progress.hide()
        self.build_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        if exit_code == 0:
            self.status_label.setText("Build completed successfully")
            self._log("\nBUILD SUCCESSFUL\n", "success")
        else:
            self.status_label.setText(f"Build failed (exit code {exit_code})")
            self._log(f"\nBUILD FAILED (exit code {exit_code})\n", "error")
        self.process = None
        self.process_phase = None

    def _process_error(self, error):
        if self.process and self.process.state() == QProcess.NotRunning:
            self.progress.hide()
            self.build_button.setEnabled(True)
            self.stop_button.setEnabled(False)
            phase = self.process_phase
            if phase == "install":
                self.status_label.setText("Could not install PyInstaller")
                self._log(
                    f"\nCould not start PyInstaller installation: {error}\n"
                    "Check that pip is available for the selected Python.\n",
                    "error",
                )
            else:
                self.status_label.setText("Could not start build process")
                self._log(f"\nCould not start build: {error}\n", "error")
            self.process = None
            self.process_phase = None

    def _stop_build(self):
        if self.process and self.process.state() != QProcess.NotRunning:
            self.process.terminate()
            if not self.process.waitForFinished(2500):
                self.process.kill()
            self.status_label.setText("Build stopped")
            self._log("\nStop requested.\n", "error")

    def _log(self, text, kind=None):
        color = {"error": "#fca5a5", "success": "#86efac", "info": "#93c5fd"}.get(kind, "#d1d5db")
        self.log.setTextColor(__import__("PyQt5.QtGui", fromlist=["QColor"]).QColor(color))
        self.log.moveCursor(self.log.textCursor().End)
        self.log.insertPlainText(text)
        self.log.ensureCursorVisible()

    def _open_output(self):
        folder = self.output_edit.text().strip().strip('"') or str(Path.cwd() / "dist")
        Path(folder).mkdir(parents=True, exist_ok=True)
        try:
            if os.name == "nt":
                os.startfile(folder)
            elif sys.platform == "darwin":
                subprocess.Popen(["open", folder])
            else:
                subprocess.Popen(["xdg-open", folder])
        except Exception as exc:
            QMessageBox.critical(self, "Could not open folder", str(exc))


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    app.setFont(QFont("Segoe UI", 10))
    window = PythonExeStudio()
    window.show()
    sys.exit(app.exec_())

