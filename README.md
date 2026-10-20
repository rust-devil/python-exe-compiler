# 🐍 Python EXE Compiler

**A modern Python-to-EXE build tool powered by PyQt5, PyInstaller, and Nuitka.**

Python EXE Compiler is a desktop application designed to simplify the process of packaging Python scripts into executable applications. Its graphical interface helps developers configure builds, select compilation engines, preview commands, and monitor build logs without manually entering complex terminal commands.

## ✨ Features

- 🎨 **Modern GUI:** Dark-themed desktop interface built with PyQt5.
- ⚙️ **Multiple Build Engines:** Choose between PyInstaller and Nuitka.
- 📂 **Source Selection:** Browse and select your Python source file.
- 📦 **Flexible Output:** Configure single-file or standalone directory builds where supported.
- 🖼️ **Custom Icons:** Set an application icon for supported builds.
- 🪟 **Console Options:** Configure console visibility for GUI applications.
- 🧹 **Clean Builds:** Remove previous build artifacts where supported.
- 👀 **Command Preview:** Review the generated build command before execution.
- 📋 **Live Build Logs:** Monitor compilation output and error messages.
- ⏹️ **Stop Build:** Stop a running build from the interface.
- 📁 **Output Management:** Open the output directory after compilation.

## 🛠️ Technologies Used

| Technology | Purpose |
|---|---|
| Python | Application logic |
| PyQt5 | Desktop GUI |
| PyInstaller | Package Python applications into executables |
| Nuitka | Compile and package Python applications |
| Git & GitHub | Version control and collaboration |

## 📋 Requirements

- Windows 10 or Windows 11
- Python 3.9 or newer recommended
- pip package manager
- PyQt5
- PyInstaller and/or Nuitka
- A compatible C/C++ compiler for Nuitka configurations that require one

## 🚀 Installation

### 1. Clone the repository

```powershell
git clone https://github.com/rust-devil/python-exe-compiler.git
cd python-exe-compiler
```

Alternatively, download the repository as a ZIP file and extract it.

### 2. Create a virtual environment

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 3. Install dependencies

Install PyQt5:

```powershell
python -m pip install PyQt5
```

Install both build engines:

```powershell
python -m pip install pyinstaller nuitka
```

You can install only the build engine you intend to use.

### 4. Launch the application

If the main application file is named `compiler.py`, execute:

```powershell
python compiler.py
```

If the `python` command is unavailable, try:

```powershell
py compiler.py
```

## 📖 How to Use

1. Launch Python EXE Compiler.
2. Select the Python script you want to package.
3. Choose an output directory and executable name.
4. Select PyInstaller or Nuitka.
5. Configure the available build options.
6. Review the generated command.
7. Start the build and monitor the logs.
8. Open the output folder to locate the generated executable or standalone distribution.

## 🔨 Build Engines

### PyInstaller

PyInstaller bundles a Python application and its dependencies into a distributable package.

Build a single executable:

```powershell
python -m PyInstaller --onefile your_script.py
```

Build a GUI application without a console window:

```powershell
python -m PyInstaller --onefile --windowed your_script.py
```

Official documentation: https://pyinstaller.org/en/stable/

### Nuitka

Nuitka compiles Python modules and can package applications in standalone or one-file mode.

Build a one-file application:

```powershell
python -m nuitka --mode=onefile your_script.py
```

Build a standalone distribution:

```powershell
python -m nuitka --mode=standalone your_script.py
```

Nuitka may require a compatible C/C++ compiler and additional setup depending on your environment.

Official documentation: https://nuitka.net/doc/user-manual.html

## 🐞 Troubleshooting

### PyQt5 is not installed

```powershell
python -m pip install PyQt5
```

### PyInstaller is not installed

```powershell
python -m pip install pyinstaller
```

### Nuitka is not installed

```powershell
python -m pip install nuitka
```

### The executable closes immediately

Try building with the console enabled and launch the resulting executable from PowerShell to inspect error messages.

### Missing files or dependencies

Some projects require additional configuration for data files, images, dynamically imported modules, environment variables, or native libraries. Consult the documentation for the selected build engine.

## 📁 Project Structure

```text
python-exe-compiler/
├── compiler.py
├── README.md
└── LICENSE
```

This is a basic representation. Additional files may be present in the repository.

## 🔐 Security Notes

- Never commit API keys, passwords, access tokens, or other secrets.
- Use environment variables for sensitive configuration.
- Review dependencies before packaging or distributing an application.
- Test generated executables before sharing them with others.

## 🤝 Contributing

Contributions, bug reports, and feature suggestions are welcome.

1. Fork this repository.
2. Create a feature branch.
3. Implement your changes.
4. Test the application and relevant build options.
5. Submit a pull request describing your changes.

## 📄 License

See the [`LICENSE`](LICENSE) file in this repository for the applicable license terms.

## 🔗 Useful Links

- **GitHub Repository:** https://github.com/rust-devil/python-exe-compiler
- **PyInstaller:** https://pyinstaller.org/en/stable/
- **Nuitka:** https://nuitka.net/doc/user-manual.html
- **PyQt:** https://www.riverbankcomputing.com/software/pyqt/

---

**Built for Python developers who want a simpler way to package their applications.** 🚀
