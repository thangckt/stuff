### REF: https://tug.org/texlive/

Name:           texlive-full
Version:        2025
Release:        1%{?dist}
Summary:        TeX Live distribution

License:        GPLv2+
URL:            https://tug.org/texlive/
#Source0:        http://mirror.ctan.org/systems/texlive/tlnet/install-tl-unx.tar.gz
Source0:        https://ftp.math.utah.edu/pub/tex/historic/systems/texlive/%{version}/install-tl-unx.tar.gz

ExclusiveArch:  x86_64

## Force replace the Fedora TeX Live
Obsoletes: texlive-core < 2025
Obsoletes: texlive-dist < 2025
Obsoletes: texlive-latex < 2025
Provides:  texlive

BuildRequires:  perl wget tar xz
Requires:       perl

%description
TeX Live provides a comprehensive TeX system for GNU/Linux. This RPM installs a full TeX Live tree in /opt/texlive.

%prep
mkdir extracted
cd extracted
tar -xf %{SOURCE0}
texlive_dir=$(ls -d install-tl-* | head -n1)
mv "$texlive_dir" ../texlive_dir
cd ..

# Create a custom install profile
# Use ${RPM_BUILD_ROOT} to ensure buildroot path is expanded correctly at shell execution time
cat <<EOF > texlive.profile
selected_scheme scheme-full
TEXDIR ${RPM_BUILD_ROOT}/opt/texlive/%{version}
TEXMFLOCAL ${RPM_BUILD_ROOT}/opt/texlive/%{version}/texmf-local
TEXMFSYSVAR ${RPM_BUILD_ROOT}/opt/texlive/%{version}/texmf-var
TEXMFSYSCONFIG ${RPM_BUILD_ROOT}/opt/texlive/%{version}/texmf-config
TEXMFVAR ${RPM_BUILD_ROOT}/opt/texlive/%{version}/texmf-var
TEXMFCONFIG ${RPM_BUILD_ROOT}/opt/texlive/%{version}/texmf-config
TEXMFHOME ${RPM_BUILD_ROOT}/opt/texlive/%{version}/texmf-home
binary_x86_64-linux 1
collection-latexextra 1
collection-binextra 1
option_doc 0
option_src 0
EOF

%build
# Nothing to build

%install
mkdir -p %{buildroot}/opt
./texlive_dir/install-tl -profile texlive.profile -no-interaction -gui text

## Fix ambiguous and legacy python2 shebangs
find %{buildroot}/opt/texlive/%{version} -type f -exec sed -i \
  -e '1s|^#! */usr/bin/python2$|#!/usr/bin/python3|' \
  -e '1s|^#! */usr/bin/env python2$|#!/usr/bin/python3|' \
  -e '1s|^#! */usr/bin/python -O$|#!/usr/bin/python3|' \
  -e '1s|^#! */usr/bin/python$|#!/usr/bin/python3|' \
  -e '1s|^#! */usr/bin/env python$|#!/usr/bin/python3|' \
  {} +

## Clean up files containing buildroot paths
rm -f %{buildroot}/opt/texlive/%{version}/install-tl.log
rm -f %{buildroot}/opt/texlive/%{version}/tlpkg/texlive.profile
find %{buildroot}/opt/texlive/%{version}/texmf-var -type f \( -name '*.log' -o -name '*.map' -o -name '*.fmt' -o -name '*.base' \) -delete

## export environment variables (PATH, MANPATH, etc.) (not use).
#mkdir -p %{buildroot}/etc/profile.d
#cat > %{buildroot}/etc/profile.d/texlive.sh <<EOF
#export PATH=/opt/texlive/%{version}/bin/x86_64-linux:\$PATH
#export MANPATH=/opt/texlive/%{version}/texmf-dist/doc/man:\$MANPATH
#export INFOPATH=/opt/texlive/%{version}/texmf-dist/doc/info:\$INFOPATH
#EOF

%post
## registers each binary file in opt/ folder of TeX Live 2025
for bin_path in /opt/texlive/%{version}/bin/x86_64-linux/*; do
    [ -f "$bin_path" ] || continue
    bin_name=$(basename "$bin_path")
    if [ -f "/usr/bin/$bin_name" ] && [ ! -L "/usr/bin/$bin_name" ]; then
        mv "/usr/bin/$bin_name" "/usr/bin/${bin_name}.backup-by-texlive-full"
    fi
    alternatives --install /usr/bin/$bin_name $bin_name "$bin_path" 100 || :
done

%preun
## Only if uninstalling
if [ "$1" -eq 0 ]; then
    for bin_path in /opt/texlive/%{version}/bin/x86_64-linux/*; do
        [ -f "$bin_path" ] || continue
        bin_name=$(basename "$bin_path")
        # Only remove if this path is currently registered
        if alternatives --display "$bin_name" | grep -q "$bin_path"; then
            alternatives --remove "$bin_name" "$bin_path" || :
        fi
    done
fi


%files
/opt/texlive
%license /opt/texlive/%{version}/LICENSE.CTAN
#%config(noreplace) /etc/profile.d/texlive.sh

%changelog
%autochangelog