### REF: https://tug.org/texlive/

Name:           texlive
Version:        2025
Release:        1%{?dist}
Summary:        TeX Live distribution

License:        GPLv2+
URL:            https://tug.org/texlive/
Source0:        http://mirror.ctan.org/systems/texlive/tlnet/install-tl-unx.tar.gz

ExclusiveArch:  x86_64

BuildRequires:  perl wget tar xz
Requires:       perl

%description
TeX Live provides a comprehensive TeX system for GNU/Linux. This RPM installs a full TeX Live tree in /opt/texlive.

%prep
%autosetup -n install-tl-*

# Create a custom install profile
cat > texlive.profile <<EOF
selected_scheme scheme-full
TEXDIR /opt/texlive/%{version}
TEXMFCONFIG ~/.texlive%{version}/texmf-config
TEXMFVAR ~/.texlive%{version}/texmf-var
binary_x86_64-linux 1
collection-basic 1
option_doc 0
option_src 0
EOF

%build
# Nothing to build

%install
mkdir -p %{buildroot}/opt
./install-tl -profile texlive.profile -portable -no-interaction -gui text

# Symlink binaries to /usr/bin
mkdir -p %{buildroot}%{_bindir}
for bin in %{buildroot}/opt/texlive/%{version}/bin/x86_64-linux/*; do
    ln -s /opt/texlive/%{version}/bin/x86_64-linux/$(basename $bin) %{buildroot}%{_bindir}/$(basename $bin)
done

%files
/opt/texlive
%{_bindir}/*

%changelog
%autochangelog