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

Provides: texlive
Conflicts: texlive-*

BuildRequires:  perl wget tar xz
Requires:       perl

%description
TeX Live provides a comprehensive TeX system for GNU/Linux. This RPM installs a basic TeX Live tree in /opt/texlive.

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
selected_scheme scheme-basic
TEXDIR ${RPM_BUILD_ROOT}/opt/texlive/%{version}
TEXMFLOCAL ${RPM_BUILD_ROOT}/opt/texlive/%{version}/texmf-local
TEXMFSYSVAR ${RPM_BUILD_ROOT}/opt/texlive/%{version}/texmf-var
TEXMFSYSCONFIG ${RPM_BUILD_ROOT}/opt/texlive/%{version}/texmf-config
TEXMFVAR ${RPM_BUILD_ROOT}/opt/texlive/%{version}/texmf-var
TEXMFCONFIG ${RPM_BUILD_ROOT}/opt/texlive/%{version}/texmf-config
TEXMFHOME ${RPM_BUILD_ROOT}/opt/texlive/%{version}/texmf-home
binary_x86_64-linux 1
collection-latexextra 1
option_doc 0
option_src 0
EOF

%build
# Nothing to build

%install
mkdir -p %{buildroot}/opt
./texlive_dir/install-tl -profile texlive.profile -no-interaction -gui text

## export environment variables (PATH, MANPATH, etc.).
mkdir -p %{buildroot}/etc/profile.d
cat > %{buildroot}/etc/profile.d/texlive.sh <<EOF
export PATH=/opt/texlive/%{version}/bin/x86_64-linux:\$PATH
EOF

%post
# Run tlmgr update from the installed location
/opt/texlive/%{version}/bin/x86_64-linux/tlmgr update --self --all || :

%files
/opt/texlive
%license /opt/texlive/%{version}/LICENSE.CTAN
%config(noreplace) /etc/profile.d/texlive.sh

%changelog
%autochangelog