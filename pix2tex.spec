Name:           pix2tex
Version:        0.0.31
Release:        1%{?dist}
Summary:        GUI frontend for LaTeX-OCR (pix2tex)

License:        MIT
URL:            https://github.com/lukas-blecher/LaTeX-OCR
Source0:        %{url}/archive/refs/tags/%{version}.tar.gz


BuildArch:      noarch
BuildRequires:  python3-devel

Requires:       python3-pyqt6 python3-pyqt6-devel
Requires:       python3 python3-torch python3-transformers
Requires:       python3-Pillow python3-opencv python3-matplotlib python3-pyqt6 python3-requests

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

# Create a launcher script
cat > %{buildroot}%{_bindir}/pix2tex << 'EOF'
#!/bin/bash
exec python3 -m pix2tex.gui "$@"
EOF
chmod +x %{buildroot}%{_bindir}/pix2tex

%files
%doc
%license
%{_bindir}/pix2tex
%{python3_sitelib}/pix2tex/gui.py
%{python3_sitelib}/pix2tex/__pycache__/*

%changelog
%autochangelog