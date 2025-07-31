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

## Step 1: Sanitize text files for buildroot references. Filter for text files only to avoid corrupting binaries.
find %{buildroot} -type f -print0 | xargs -0 grep -l "$RPM_BUILD_ROOT" | while read -r f; do
    # Check if the file is likely a text file before attempting sed
    if file -b --mime-encoding "$f" | grep -q 'charset=us-ascii\|charset=utf-8\|charset=iso-8859-1\|charset=binary'; then
        sed -i "s|$RPM_BUILD_ROOT||g" "$f"
    fi
done

## Step 2. Delete problematic binary format/base files (mf.base, tex.fmt) that embed buildroot paths.
rm -f %{buildroot}/opt/texlive/%{version}/texmf-var/web2c/metafont/mf.base
rm -f %{buildroot}/opt/texlive/%{version}/texmf-var/web2c/tex/tex.fmt

## Step 3. Regenerate all system formats/bases using TeX Live's own tools.
#    This ensures they are created correctly within the RPM's build environment.
#    Set necessary environment variables for fmtutil-sys to work within the buildroot.
export PATH=%{buildroot}/opt/texlive/%{version}/bin/x86_64-linux:$PATH
export TEXMFROOT=%{buildroot}/opt/texlive/%{version}/texmf-dist
export TEXMFVAR=%{buildroot}/opt/texlive/%{version}/texmf-var
export TEXMFCONFIG=%{buildroot}/opt/texlive/%{version}/texmf-config
export TEXMFSYSVAR=%{buildroot}/opt/texlive/%{version}/texmf-var
export TEXMFSYSCONFIG=%{buildroot}/opt/texlive/%{version}/texmf-config

# Use fmtutil-sys --all which handles most common format/base files
# This is usually the most comprehensive way to regenerate.
if [ -x %{buildroot}/opt/texlive/%{version}/bin/x86_64-linux/fmtutil-sys ]; then
    %{buildroot}/opt/texlive/%{version}/bin/x86_64-linux/fmtutil-sys --all
else
    # Fallback if fmtutil-sys is not available in basic scheme (less likely but possible)
    # Directly run inimf and initex if fmtutil-sys is absent.
    if [ -x %{buildroot}/opt/texlive/%{version}/bin/x86_64-linux/inimf ]; then
        %{buildroot}/opt/texlive/%{version}/bin/x86_64-linux/inimf < /dev/null
    fi
    if [ -x %{buildroot}/opt/texlive/%{version}/bin/x86_64-linux/initex ]; then
        %{buildroot}/opt/texlive/%{version}/bin/x86_64-linux/initex < /dev/null
    fi
fi

## Step 4. Remove any remaining log or temporary profile files that aren't part of the final install.
find %{buildroot} -type f \( -name "*.log" -o -name "*.profile" -o -name "*.map" \) -delete


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