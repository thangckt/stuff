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

# Obsolete your own basic package, and the Fedora ones we are replacing.
# The 'texlive' Provides is what dnf will use to handle most other dependencies.
Obsoletes:      texlive-core < 1:%{version}
Obsoletes:      texlive-kpathsea < 1:%{version}
Obsoletes:      texlive-latex < 1:%{version}
Obsoletes:      texlive-scheme-basic < 1:%{version}

BuildRequires:  perl wget tar xz
Requires:       perl

%global install_dir /opt/texlive/%{version}

%description
TeX Live provides a comprehensive TeX system for GNU/Linux. This RPM installs a TeX Live tree in /opt/texlive.

%prep
mkdir extracted
cd extracted
tar -xf %{SOURCE0}
texlive_dir=$(ls -d install-tl-* | head -n1)
mv "$texlive_dir" ../texlive_dir
cd ..

%build
# Nothing to build

%install
## Install texlive to a temporary directory to avoid embedding %{buildroot} in the file-paths
mkdir -p tmp_texlive
tmp_install_dir=$(realpath tmp_texlive)

# Create a custom install profile with absolute paths
cat > texlive.profile <<EOF
selected_scheme scheme-basic
TEXDIR          ${tmp_install_dir}
TEXMFLOCAL      ${tmp_install_dir}/texmf-local
TEXMFSYSVAR     ${tmp_install_dir}/texmf-var
TEXMFSYSCONFIG  ${tmp_install_dir}/texmf-config
TEXMFVAR        ${tmp_install_dir}/texmf-var
TEXMFCONFIG     ${tmp_install_dir}/texmf-config
TEXMFHOME       ${tmp_install_dir}/texmf-home
binary_x86_64-linux 1
option_doc 0
option_src 0
EOF

./texlive_dir/install-tl -profile texlive.profile -no-interaction -gui text

## Fix ambiguous and legacy python2 shebangs
find ${tmp_install_dir} -type f -exec sed -i \
  -e '1s|^#! */usr/bin/python2$|#!/usr/bin/python3|' \
  -e '1s|^#! */usr/bin/env python2$|#!/usr/bin/python3|' \
  -e '1s|^#! */usr/bin/python -O$|#!/usr/bin/python3|' \
  -e '1s|^#! */usr/bin/python$|#!/usr/bin/python3|' \
  -e '1s|^#! */usr/bin/env python$|#!/usr/bin/python3|' \
  {} +

## Remove unnecessary build files
find ${tmp_install_dir} -type f \( -name 'install-tl.log' -o -name 'texlive.profile' \) -delete || :

## Copy staged install into %{buildroot}
mkdir -p %{buildroot}%{install_dir}
cp -a "$tmp_install_dir"/* %{buildroot}%{install_dir}/


%post
## registers each binary file in opt/ folder of TeX Live 2025
for bin_path in %{install_dir}/bin/x86_64-linux/*; do
    [ -f "$bin_path" ] || continue
    bin_name=$(basename "$bin_path")
    # If /usr/bin/$bin_name exists and is not a symlink, back it up
    if [ -e "/usr/bin/$bin_name" ] && [ ! -L "/usr/bin/$bin_name" ]; then
        mv "/usr/bin/$bin_name" "/usr/bin/$bin_name.bak_by_texlive_thang" || :
    fi
    alternatives --install /usr/bin/$bin_name $bin_name "$bin_path" 100 || :
done

## Inform
echo "======================================================="
echo "TeX Live has been installed to /opt/texlive/%{version}."
echo "======================================================="


%preun
## Only if uninstalling
if [ "$1" -eq 0 ]; then
    for bin_path in %{install_dir}/bin/x86_64-linux/*; do
        [ -f "$bin_path" ] || continue
        bin_name=$(basename "$bin_path")
        # Only remove if this path is currently registered
        if alternatives --display "$bin_name" | grep -q "$bin_path"; then
            alternatives --remove "$bin_name" "$bin_path" || :
        fi
    done
fi


%files
%{install_dir}

%changelog
%autochangelog