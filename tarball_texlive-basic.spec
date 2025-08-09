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

BuildRequires:  tar perl-devel
Requires:       perl perl-YAML-Tiny

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
###ANCHOR Install texlive to a temporary directory to avoid embedding %{buildroot} in the file-paths
mkdir -p tmp_texlive
tmp_install_dir=$(realpath tmp_texlive)

## Create a custom install profile with absolute paths
cat > texlive.profile <<EOF
selected_scheme scheme-basic
TEXDIR          ${tmp_install_dir}
TEXMFLOCAL      ${tmp_install_dir}/texmf-local
TEXMFSYSVAR     ${tmp_install_dir}/texmf-var
TEXMFSYSCONFIG  ${tmp_install_dir}/texmf-config
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

###ANCHOR Fix some issues
## Create wrapper for tlmgr to override system /usr/sbin/tlmgr when use sudo
mkdir -p %{buildroot}/usr/local/bin
cat > %{buildroot}/usr/local/bin/tlmgr <<EOF
#!/bin/sh
exec %{install_dir}/bin/x86_64-linux/tlmgr "\$@"
EOF
chmod +x %{buildroot}/usr/local/bin/tlmgr

###ANCHOR Set Texlive PATH
## export environment variables (PATH, MANPATH, etc.)
mkdir -p %{buildroot}/etc/profile.d
cat > %{buildroot}/etc/profile.d/texlive.sh <<EOF
export PATH=%{install_dir}/bin/x86_64-linux:\$PATH
export MANPATH=%{install_dir}/texmf-dist/doc/man:\$MANPATH
export INFOPATH=%{install_dir}/texmf-dist/doc/info:\$INFOPATH
EOF

## To ensure non-login shells also get the PATH
mkdir -p %{buildroot}/etc/bashrc.d
cat > %{buildroot}/etc/bashrc.d/texlive.sh <<EOF
if [ -f /etc/profile.d/texlive.sh ]; then
  . /etc/profile.d/texlive.sh
fi
EOF

%post
## Fix broken biber (update its versions)
PATH=%{install_dir}/bin/x86_64-linux:$PATH \
    %{install_dir}/bin/x86_64-linux/tlmgr install --reinstall biber

## Info
echo "======================================================="
echo "TeX Live has been installed to %{install_dir}."
echo "To use, open a new terminal session, or source this script manually:"
echo "  source /etc/profile.d/texlive.sh"
echo "======================================================="

%files
%{install_dir}
/usr/local/bin/tlmgr
/etc/profile.d/texlive.sh
/etc/bashrc.d/texlive.sh

%changelog
%autochangelog