Name:           pix2tex
Version:        0.0.31
Release:        1%{?dist}
Summary:        GUI frontend for LaTeX-OCR (pix2tex)

License:        MIT
URL:            https://github.com/lukas-blecher/LaTeX-OCR
Source0:        %{url}/archive/refs/tags/%{version}.tar.gz

BuildArch:      noarch

%global _pyproject_ghost_dist true
BuildRequires:  python3-devel python3-pip python3-setuptools python3-wheel

Requires:       python3-pyqt6 python3-pyqt6-webengine

%description
A GUI application that allows users to convert images of math equations into LaTeX using deep learning.

%prep
%autosetup -n LaTeX-OCR-%{version}

%build
# Nothing to build

%install
mkdir -p %{buildroot}%{_bindir}
mkdir -p %{buildroot}%{python3_sitelib}/pix2tex
install -m 644 pix2tex/gui.py %{buildroot}%{python3_sitelib}/pix2tex/gui.py

# Install pynput using pip into the buildroot
pip3 install --no-deps --target %{buildroot}%{python3_sitelib} pynput screeninfo

# Create a launcher script
cat > %{buildroot}%{_bindir}/pix2tex << 'EOF'
#!/bin/bash
PYVER=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
export PYTHONPATH=/usr/lib/python${PYVER}/site-packages:$PYTHONPATH
exec python3 -m pix2tex.gui "$@"
EOF
chmod +x %{buildroot}%{_bindir}/pix2tex

# Install icon
mkdir -p %{buildroot}%{_datadir}/icons/hicolor/scalable/apps/
install -m 644 pix2tex/resources/icon.svg %{buildroot}%{_datadir}/icons/hicolor/scalable/apps/pix2tex.svg

# Install .desktop entry
mkdir -p %{buildroot}%{_datadir}/applications/
cat > %{buildroot}%{_datadir}/applications/pix2tex.desktop << 'EOF'
[Desktop Entry]
Name=pix2tex
Exec=pix2tex
Icon=pix2tex
Terminal=false
Type=Application
Categories=Utility;
EOF

%files
%doc
%license
%{_bindir}/pix2tex
%{python3_sitelib}/pix2tex/gui.py
%{python3_sitelib}/pix2tex/__pycache__/*
%{_datadir}/applications/pix2tex.desktop
%{_datadir}/icons/hicolor/scalable/apps/pix2tex.svg
%{python3_sitelib}/pynput/
%{python3_sitelib}/pynput-*.dist-info/
%{python3_sitelib}/screeninfo/
%{python3_sitelib}/screeninfo-*.dist-info/

%changelog
%autochangelog