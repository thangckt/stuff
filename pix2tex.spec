### NOTE: prior to use `BuildRequires`, if not found packages, then try install using `pip`

Name:           pix2tex
Version:        0.0.31
Release:        1%{?dist}
Summary:        GUI frontend for LaTeX-OCR (pix2tex)

License:        MIT
URL:            https://github.com/lukas-blecher/LaTeX-OCR
Source0:        %{url}/archive/refs/tags/%{version}.tar.gz

# Fully disable auto dependency/provides generation for vendored Python files
%global __requires_exclude_from ^/usr/pix2tex_vendor/lib/python3.13/site-packages/.*$
%global __provides_exclude_from ^/usr/pix2tex_vendor/lib/python3.13/site-packages/.*$

%undefine _debugsource_packages
%undefine _debuginfo_packages
%undefine _missing_build_ids_terminate_build

BuildRequires:  python3-devel python3-pip python3-setuptools python3-wheel pyproject-rpm-macros
Requires:       python3 python3-pyqt6 python3-pyqt6-webengine

%description
A GUI application that allows users to convert images of math equations into LaTeX using deep learning.

%prep
%autosetup -n LaTeX-OCR-%{version}

%build
%pyproject_wheel

%install
%pyproject_install

# Create vendor directory for isolated dependencies
mkdir -p %{buildroot}%{_prefix}/pix2tex_vendor

# Install PyPI dependencies using pip into the isolated Python environment
PYTHONUSERBASE=%{buildroot}%{_prefix}/pix2tex_vendor \
pip3 install --user --no-deps --no-warn-script-location \
  albumentations timm tokenizers transformers x-transformers opencv-python-headless

# Remove prebuilt binary blobs (which cause unresolvable .so requires)
find %{buildroot}%{_prefix}/pix2tex_vendor -type f -name '*.so' -delete
find %{buildroot}%{_prefix}/pix2tex_vendor -type f -name '*.so.*' -delete

# Install launcher script
install -Dpm 0755 /dev/stdin %{buildroot}%{_bindir}/pix2tex <<'EOF'
#!/bin/bash
export PYTHONPATH=%{_prefix}/pix2tex_vendor/lib/python*/site-packages:$PYTHONPATH
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
Categories=Utility;Education;Science;
EOF

%pyproject_save_files pix2tex

%files -f %{pyproject_files}
%license LICENSE
%doc README.md
%{_bindir}/pix2tex
%{_bindir}/pix2tex_cli
%{_bindir}/pix2tex_gui
%{_bindir}/latexocr

%{_prefix}/pix2tex_vendor/
%{_datadir}/applications/pix2tex.desktop
%{_datadir}/icons/hicolor/scalable/apps/pix2tex.svg

%changelog
%autochangelog
