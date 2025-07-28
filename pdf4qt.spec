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
    -DCMAKE_INSTALL_PREFIX='/' \
    -DCMAKE_BUILD_TYPE=Release\
    -DPDF4QT_INSTALL_QT_DEPENDENCIES=OFF \
    -DPDF4QT_INSTALL_DEPENDENCIES=OFF \
    -DQT_NO_MISSING_CATALOG_LANGUAGE_WARNING=ON
%cmake_build -j$(nproc)

## debug PATH
cat %{_vpath_builddir}/CMakeCache.txt | grep CMAKE_INSTALL_PREFIX

%install
%cmake_install

## Desktop file
%global _app_dir %{buildroot}%{_datadir}/applications
mkdir -p %{_app_dir}
cp Desktop/io.github.JakubMelka.Pdf4qt.desktop %{_app_dir}/Pdf4qt.desktop
cp Desktop/io.github.JakubMelka.Pdf4qt.Pdf4QtDiff.desktop %{_app_dir}/Pdf4qt.Pdf4QtDiff.desktop
cp Desktop/io.github.JakubMelka.Pdf4qt.Pdf4QtEditor.desktop %{_app_dir}/Pdf4qt.Pdf4QtEditor.desktop
cp Desktop/io.github.JakubMelka.Pdf4qt.Pdf4QtPageMaster.desktop %{_app_dir}/Pdf4qt.Pdf4QtPageMaster.desktop
cp Desktop/io.github.JakubMelka.Pdf4qt.Pdf4QtViewer.desktop %{_app_dir}/Pdf4qt.Pdf4QtViewer.desktop

## Icons
%global _icon_dir %{buildroot}%{_datadir}/icons/hicolor/128x128/apps
mkdir -p %{_icon_dir}
cp Desktop/128x128/io.github.JakubMelka.Pdf4qt.png %{_icon_dir}/io.github.JakubMelka.Pdf4qt.png
cp Desktop/128x128/io.github.JakubMelka.Pdf4qt.Pdf4QtDiff.png %{_icon_dir}/io.github.JakubMelka.Pdf4qt.Pdf4QtDiff.png
cp Desktop/128x128/io.github.JakubMelka.Pdf4qt.Pdf4QtEditor.png %{_icon_dir}/io.github.JakubMelka.Pdf4qt.Pdf4QtEditor.png
cp Desktop/128x128/io.github.JakubMelka.Pdf4qt.Pdf4QtPageMaster.png %{_icon_dir}/io.github.JakubMelka.Pdf4qt.Pdf4QtPageMaster.png
cp Desktop/128x128/io.github.JakubMelka.Pdf4qt.Pdf4QtViewer.png %{_icon_dir}/io.github.JakubMelka.Pdf4qt.Pdf4QtViewer.png

## Generate file list (include everything)
find %{buildroot} -type f | sed "s|^%{buildroot}||" > filelist.txt

%files -f filelist.txt
/usr/lib/libPdf4QtLib*.so
/usr/lib/pdf4qt/lib*.so

%changelog
%autochangelog