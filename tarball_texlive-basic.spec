### REF: https://tug.org/texlive/

Name:           texlive-basic
Version:        2025
Release:        1%{?dist}
Summary:        TeX Live distribution

License:        GPLv2+
URL:            https://tug.org/texlive/
#Source0:        http://mirror.ctan.org/systems/texlive/tlnet/install-tl-unx.tar.gz
Source0:        https://ftp.math.utah.edu/pub/tex/historic/systems/texlive/%{version}/install-tl-unx.tar.gz

ExclusiveArch:  x86_64

## Force replace the Fedora TeX Live (Epoch to ensure our version is always "newer")
Epoch:          1
Provides:       texlive = 1:%{version}
Provides:       texlive-basic = 1:%{version}

# Obsolete our own basic package, plus the Fedora ones we are replacing.
# The 'texlive' Provides is what dnf will use to handle most other dependencies.
Obsoletes:      texlive-core < 1:%{version}
Obsoletes:      texlive-kpathsea < 1:%{version}
Obsoletes:      texlive-latex < 1:%{version}
Obsoletes:      texlive-scheme-basic < 1:%{version}

BuildRequires:  perl wget tar xz
Requires:       perl

%description
TeX Live provides a comprehensive TeX system for GNU/Linux. This RPM installs a TeX Live tree in /opt/texlive.


%prep
mkdir extracted
cd extracted
tar -xf %{SOURCE0}
texlive_dir=$(ls -d install-tl-* | head -n1)
mv "$texlive_dir" ../texlive_dir
cd ..

# Create a custom install profile
# Use ${RPM_BUILD_ROOT} to ensure buildroot path is expanded correctly at shell execution time
cat > texlive.profile <<EOF
selected_scheme scheme-basic
TEXDIR ${RPM_BUILD_ROOT}/opt/texlive/%{version}
# TEXMFLOCAL ${RPM_BUILD_ROOT}/opt/texlive/%{version}/texmf-local
# TEXMFSYSVAR ${RPM_BUILD_ROOT}/opt/texlive/%{version}/texmf-var
# TEXMFSYSCONFIG ${RPM_BUILD_ROOT}/opt/texlive/%{version}/texmf-config
# TEXMFVAR ${RPM_BUILD_ROOT}/opt/texlive/%{version}/texmf-var
# TEXMFCONFIG ${RPM_BUILD_ROOT}/opt/texlive/%{version}/texmf-config
# TEXMFHOME ${RPM_BUILD_ROOT}/opt/texlive/%{version}/texmf-home
binary_x86_64-linux 1
option_doc 0
option_src 0
EOF


%build
# Nothing to build


%install
./texlive_dir/install-tl -profile texlive.profile -no-interaction -gui text

## Fix ambiguous and legacy python2 shebangs
find %{buildroot}/opt/texlive/%{version} -type f -exec sed -i \
  -e '1s|^#! */usr/bin/python2$|#!/usr/bin/python3|' \
  -e '1s|^#! */usr/bin/env python2$|#!/usr/bin/python3|' \
  -e '1s|^#! */usr/bin/python -O$|#!/usr/bin/python3|' \
  -e '1s|^#! */usr/bin/python$|#!/usr/bin/python3|' \
  -e '1s|^#! */usr/bin/env python$|#!/usr/bin/python3|' \
  {} +

## Remove prebuilt format files to avoid embedded %{buildroot}
# find %{buildroot}/opt/texlive/%{version} -type f \
#   \( -name 'install-tl.log' -o -name 'texlive.profile' -o -name '*.log' -o -name '*.map' -o -name '*.fmt' -o -name '*.base' -o -name '*.conf' \) -delete

%post
## registers each binary file in opt/ folder of TeX Live 2025
for bin_path in /opt/texlive/%{version}/bin/x86_64-linux/*; do
    [ -f "$bin_path" ] || continue
    bin_name=$(basename "$bin_path")
    # If /usr/bin/$bin_name exists and is not a symlink, back it up
    if [ -e "/usr/bin/$bin_name" ] && [ ! -L "/usr/bin/$bin_name" ]; then
        mv "/usr/bin/$bin_name" "/usr/bin/$bin_name.bak_by_texlive_thang" || :
    fi
    alternatives --install /usr/bin/$bin_name $bin_name "$bin_path" 100 || :
done


# %posttrans
# ## Rebuild formats at install time
# export PATH=/opt/texlive/%{version}/bin/x86_64-linux:$PATH
# export TEXMFCNF=/opt/texlive/%{version}/texmf-dist/web2c
# mktexlsr > /dev/null 2>&1 || :
# updmap-sys > /dev/null 2>&1 || :
# fmtutil-sys --all > /dev/null 2>&1 || :

## Inform
echo "======================================================="
echo "TeX Live has been installed to /opt/texlive/%{version}."
echo "======================================================="


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

%changelog
%autochangelog