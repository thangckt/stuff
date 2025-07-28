### REF: https://github.com/JakubMelka/PDF4QT?tab=readme-ov-file#compiling-from-sources
# Note: the official guide used VCPKG, but on Linux systems, there is no need for it.

Name:           pdf4qt
Version:        1.5.1.0
Release:        1%{?dist}
Summary:        PDF4QT: An open-source PDF editor
License:        LGPLv3
URL:            https://github.com/JakubMelka/PDF4QT
Source0:        %{url}/archive/refs/tags/v%{version}.tar.gz

BuildRequires: cmake ninja-build gcc-c++ git pkgconfig
BuildRequires: qt6-qtbase-devel qt6-qtsvg-devel qt6-qttools-devel qt6-qtspeech-devel qt6-qtmultimedia-devel
BuildRequires: openssl-devel zlib-devel freetype-devel tbb-devel cups-devel
BuildRequires: openjpeg2-devel libjpeg-turbo-devel libpng-devel lcms2-devel blend2d-devel

%description
PDF4QT is an open-source Qt-based PDF editor and viewer. It supports basic editing functions and uses Poppler for PDF rendering.

%prep
%autosetup -n PDF4QT-%{version}

%build
printf "\n%s\n" "#ANCHOR Build PDF4QT"
%cmake \
	-DLIB_INSTALL_DIR:PATH=%{_libdir} \
	-DSHARE_INSTALL_PREFIX:PATH=%{_datadir} \
    -DINCLUDE_INSTALL_DIR:PATH=%{_includedir} \
	-DLIB_SUFFIX=64 \
    -DPDF4QT_INSTALL_QT_DEPENDENCIES=OFF \
    -DPDF4QT_INSTALL_DEPENDENCIES=OFF \
    -DCMAKE_BUILD_TYPE=Release
%cmake_build

%install
%cmake_install

%files
%license LICENSE
%doc README.md
%{_bindir}/*
%{_libdir}/libpdf4qt*.so.*
%{_datadir}/applications/*.desktop
%{_datadir}/icons/hicolor/*/apps/*.png

%changelog
%autochangelog