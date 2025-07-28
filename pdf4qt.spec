### REF: https://www.ovito.org/docs/current/development/build_linux.html

Name:           pdf4qt
Version:        1.5.1.0
Release:        1%{?dist}
Summary:        PDF4QT: An open-source PDF editor
License:        LGPLv3
URL:            https://github.com/JakubMelka/PDF4QT
Source0:        %{url}/archive/refs/tags/v%{version}.tar.gz

BuildRequires:  cmake ninja-build gcc-c++ git
BuildRequires:  qt6-qtbase-devel qt6-qtsvg-devel

%description
OVITO is a scientific data visualization and analysis software for atomistic, molecular and other particle-based simulations.

%prep
# Install vcpkg
git clone https://github.com/Microsoft/vcpkg.git
./vcpkg/bootstrap-vcpkg.sh -disableMetrics
VCPKG_ROOT=$(pwd)/vcpkg

# Clone PDF4QT source code
git clone https://github.com/JakubMelka/PDF4QT pdf4qt
cd pdf4qt
git checkout v%{version}

# Move source to expected build directory root
cd ..
cp -a pdf4qt/. ./
rm -rf pdf4qt

%build
export CFLAGS="$RPM_OPT_FLAGS -fPIC -Wno-sign-compare -Wno-deprecated-declarations -flto"

printf "\n%s\n" "#ANCHOR: Build PDF4QT"
%cmake \
	-DLIB_INSTALL_DIR:PATH=%{_libdir} \
	-DSHARE_INSTALL_PREFIX:PATH=%{_datadir} \
    -DINCLUDE_INSTALL_DIR:PATH=%{_includedir} \
	-DLIB_SUFFIX=64 \
    -DCMAKE_TOOLCHAIN_FILE=$VCPKG_ROOT/scripts/buildsystems/vcpkg.cmake \
    -DPDF4QT_INSTALL_QT_DEPENDENCIES=0 \
    -DCMAKE_BUILD_TYPE=Release
%cmake_build -j%{?_smp_build_ncpus}

%install
%cmake_install

## Generate file list (include everything)
find %{buildroot} -type f | sed "s|^%{buildroot}||" > filelist.txt

%files -f filelist.txt

%changelog
%autochangelog