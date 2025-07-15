### NOTE: prior to use `BuildRequires`, if not found packages, then try install using `pip`

Name:           pix2tex
Version:        0.0.31
Release:        1%{?dist}
Summary:        GUI frontend for LaTeX-OCR (pix2tex)

License:        MIT
URL:            https://github.com/lukas-blecher/LaTeX-OCR
Source0:        %{url}/archive/refs/tags/%{version}.tar.gz

BuildRequires:  python3-devel python3-pip python3-setuptools python3-wheel pyproject-rpm-macros
BuildRequires:  python3-opencv python3-pyqt6 python3-pyqt6-webengine

%undefine _debugsource_packages
%undefine _debuginfo_packages

%description
A GUI application that allows users to convert images of math equations into LaTeX using deep learning.

%prep
%autosetup -n LaTeX-OCR-%{version}

%build
%pyproject_wheel

%install
%pyproject_install

# Install PiPy dependencies using pip into the buildroot
pip3 install --no-deps --prefix=%{buildroot}%{_prefix} albumentations timm tokenizers transformers x-transformers

# Install launcher script
install -Dpm 0755 /dev/stdin %{buildroot}%{_bindir}/pix2tex <<'EOF'
#!/bin/bash
PYVER=$(python3 -c "import sys; print(f'%d.%d' % (sys.version_info.major, sys.version_info.minor))")
export PYTHONPATH=/usr/lib/python${PYVER}/site-packages:$PYTHONPATH
exec python3 -m pix2tex.gui "$@"
EOF

# Install icon
install -Dpm 0644 pix2tex/resources/icon.svg \
  %{buildroot}%{_datadir}/icons/hicolor/scalable/apps/pix2tex.svg

# Install desktop file
install -Dpm 0644 /dev/stdin %{buildroot}%{_datadir}/applications/pix2tex.desktop <<'EOF'
[Desktop Entry]
Name=pix2tex
Exec=pix2tex
Icon=pix2tex
Terminal=false
Type=Application
Categories=Utility;
EOF

%pyproject_save_files pix2tex

%files -f %{pyproject_files}
%license LICENSE
%doc README.md
%{_bindir}/pix2tex
%{_bindir}/pix2tex_cli
%{_bindir}/pix2tex_gui
%{_bindir}/latexocr
%{_bindir}/transformers
%{_bindir}/transformers-cli

%{_datadir}/applications/pix2tex.desktop
%{_datadir}/icons/hicolor/scalable/apps/pix2tex.svg

%{python3_sitelib}/albumentations/
%{python3_sitelib}/albumentations-*.dist-info/
%{python3_sitelib}/timm/
%{python3_sitelib}/timm-*.dist-info/
%{python3_sitelib}/transformers/
%{python3_sitelib}/transformers-*.dist-info/
%{python3_sitelib}/x_transformers/
%{python3_sitelib}/x_transformers-*.dist-info/

/usr/lib64/python3.13/site-packages/tokenizers/
/usr/lib64/python3.13/site-packages/tokenizers-*.dist-info/

%changelog
%autochangelog
