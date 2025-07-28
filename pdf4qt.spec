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
BuildRequires: qt6-qtbase-devel qt6-qtsvg-devel qt6-qttools-devel qt6-qtspeech-devel
BuildRequires: qt6-qtmultimedia-devel qt6-qtpdf-devel
BuildRequires: openssl-devel zlib-devel freetype-devel tbb-devel cups-devel
BuildRequires: openjpeg2-devel libjpeg-turbo-devel libpng-devel lcms2-devel blend2d-devel

%description
PDF4QT is an open-source Qt-based PDF editor and viewer. It supports basic editing functions and uses Poppler for PDF rendering.

%prep
%autosetup -n PDF4QT-%{version}

mkdir -p cmake
# Write minimal Findlcms2.cmake
cat > cmake/Findlcms2.cmake << 'EOF'
find_package(PkgConfig REQUIRED)
pkg_check_modules(LCMS2 REQUIRED lcms2)
add_library(lcms2::lcms2 UNKNOWN IMPORTED)
set_target_properties(lcms2::lcms2 PROPERTIES
    INTERFACE_INCLUDE_DIRECTORIES "${LCMS2_INCLUDE_DIRS}"
    IMPORTED_LOCATION "${LCMS2_LINK_LIBRARIES}"
)
EOF

# Add cmake/ to CMAKE_MODULE_PATH
sed -i '/include(GNUInstallDirs)/a\
set(CMAKE_MODULE_PATH "${CMAKE_SOURCE_DIR}/cmake" ${CMAKE_MODULE_PATH})' CMakeLists.txt

%build
printf "\n%s\n" "#ANCHOR Build PDF4QT"
%cmake \
	-DLIB_INSTALL_DIR:PATH=%{_libdir} \
	-DSHARE_INSTALL_PREFIX:PATH=%{_datadir} \
    -DINCLUDE_INSTALL_DIR:PATH=%{_includedir} \
	-DLIB_SUFFIX=64 \
    -DPDF4QT_INSTALL_QT_DEPENDENCIES=OFF \
    -DPDF4QT_INSTALL_DEPENDENCIES=OFF \
    -DQT_NO_MISSING_CATALOG_LANGUAGE_WARNING=ON \
    -DCMAKE_BUILD_TYPE=Release
%cmake_build

%install
%cmake_install

## Generate file list (include everything)
find %{buildroot} -type f | sed "s|^%{buildroot}||" > filelist.txt

%files -f filelist.txt

%changelog
%autochangelog