### NOTE: prior to use `BuildRequires`, if not found packages, then try install using `pip`

Name:           pix2tex
Version:        0.0.31
Release:        1%{?dist}
Summary:        GUI frontend for LaTeX-OCR (pix2tex)

License:        MIT
URL:            https://github.com/lukas-blecher/LaTeX-OCR
Source0:        %{url}/archive/refs/tags/%{version}.tar.gz

%global _python_disable_dependency_generator 1
%undefine _debugsource_packages
%undefine _debuginfo_packages
%undefine _missing_build_ids_terminate_build

# Disable automatic Python byte compilation and requires
%undefine __brp_mangle_shebangs
%undefine __brp_python_bytecompile
%undefine __python_requires

# Prevent RPM from scanning vendored Python modules
%define __requires_exclude_from ^/usr/pix2tex_vendor/.*\\.py$|^/usr/pix2tex_vendor/.*\\.so$

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

# Install PiPy dependencies using pip into the isolate Python environment
pip3 install --no-deps --prefix=%{buildroot}%{_prefix}/pix2tex_vendor \
  albumentations timm tokenizers transformers x-transformers opencv_python_headless

# Install launcher script
install -Dpm 0755 /dev/stdin %{buildroot}%{_bindir}/pix2tex <<'EOF'
#!/bin/bash
export PYTHONPATH=%{_prefix}/pix2tex_vendor/lib*/python3.13/site-packages:$PYTHONPATH
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
%{_prefix}/pix2tex_vendor/
%{_bindir}/pix2tex
%{_bindir}/pix2tex_cli
%{_bindir}/pix2tex_gui
%{_bindir}/latexocr

%{_datadir}/applications/pix2tex.desktop
%{_datadir}/icons/hicolor/scalable/apps/pix2tex.svg

%changelog
%autochangelog
