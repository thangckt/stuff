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
%global texlive_dir $(ls -d install-tl-* | head -n1)

# Create a custom install profile
cat > texlive.profile <<EOF
selected_scheme scheme-basic
TEXDIR /opt/texlive/%{version}
TEXMFCONFIG /opt/texlive/%{version}/texmf-config
TEXMFVAR /opt/texlive/%{version}/texmf-var
binary_x86_64-linux 1
collection-latexextra 1
option_doc 0
option_src 0
EOF

%build
# Nothing to build

%install
mkdir -p %{buildroot}/opt
%{texlive_dir}/install-tl -profile texlive.profile -no-interaction -gui text

# Symlink binaries to /usr/bin
mkdir -p %{buildroot}%{_bindir}
for bin in %{buildroot}/opt/texlive/%{version}/bin/x86_64-linux/*; do
    install -D -m 755 $bin %{buildroot}%{_bindir}/$(basename $bin)
done

## export some environment variables (PATH, MANPATH, etc.).
mkdir -p %{buildroot}/etc/profile.d
cat > %{buildroot}/etc/profile.d/texlive.sh <<EOF
export PATH=/opt/texlive/%{version}/bin/x86_64-linux:\$PATH
EOF


## Validate build output before packaging:
%check
%{buildroot}%{_bindir}/latex -version
%{buildroot}%{_bindir}/tlmgr --version

%post
%{buildroot}%{_bindir}/tlmgr update --self --all || :


%files
/opt/texlive
%{_bindir}/*
%license /opt/texlive/%{version}/LICENSE.CTAN
%config(noreplace) /etc/profile.d/texlive.sh

%changelog
%autochangelog