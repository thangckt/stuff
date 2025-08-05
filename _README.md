# Use Copr to build a package for Fedora

This file contains the `.spec` files for building multiple packages using Copr.

See https://copr.fedorainfracloud.org/coprs/thangckt/multi_packages


# Official Fedora build system
- Koji: https://koji.fedoraproject.org/koji/packages

How to get the spec file for a package:
- Search for the package on the Koji website.
- Click on the package name to view its details.
- Look for `Source	git+https://src.fedoraproject.org/rpms/evolution.git` or similar lines.
- Just go to: `https://src.fedoraproject.org/rpms/evolution` -> `files` to see the spec file.


# Some spec repos:
- https://github.com/PhantomX/chinforpms


# Spec files

## Texlive
- Install texlive using `install-tl` script.

There are tow ways to set paths for texlive packages:
1. Use `alternaives` to set the default path.
- Some packages may not work properly with this method.
```sh
%post
## registers each binary file in opt/ folder of TeX Live 2025
for bin_path in /opt/texlive/%{version}/bin/x86_64-linux/*; do
    [ -f "$bin_path" ] || continue
    bin_name=$(basename "$bin_path")
    # Prefer non-dev version by priority
    if [[ "$bin_name" == *-dev ]]; then
        priority=90
    else
        priority=100
    fi
    if [ -f "/usr/bin/$bin_name" ] && [ ! -L "/usr/bin/$bin_name" ]; then
        mv "/usr/bin/$bin_name" "/usr/bin/${bin_name}.backup-by-texlive-full"
    fi
    alternatives --install /usr/bin/$bin_name $bin_name "$bin_path" $priority || :
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
```
2. Use `PATH` environment variable to set the default path (recommended).
- Must ensure both `login` and `non-login` shells are configured.
```sh
%install

## other install here

## export environment variables (PATH, MANPATH, etc.) (not use).
mkdir -p %{buildroot}/etc/profile.d
cat > %{buildroot}/etc/profile.d/texlive.sh <<EOF
export PATH=/opt/texlive/%{version}/bin/x86_64-linux:\$PATH
export MANPATH=/opt/texlive/%{version}/texmf-dist/doc/man:\$MANPATH
export INFOPATH=/opt/texlive/%{version}/texmf-dist/doc/info:\$INFOPATH
EOF

## New section to ensure non-login shells also get the PATH
mkdir -p %{buildroot}/etc/bashrc.d
cat > %{buildroot}/etc/bashrc.d/texlive.sh <<EOF
# Source the profile.d script for interactive non-login shells
if [ -f /etc/profile.d/texlive.sh ]; then
  . /etc/profile.d/texlive.sh
fi
EOF


%post
# Inform the user how to activate immediately
echo "==================================================================="
echo "TeX Live has been installed to /opt/texlive/%{version}."
echo "Please open a new terminal session to use it."
echo "If it does not work, try to source the script manually:"
echo "  source /etc/profile.d/texlive.sh"
echo "==================================================================="

%files
/opt/texlive
%config(noreplace) /etc/profile.d/texlive.sh
%config(noreplace) /etc/bashrc.d/texlive.sh
```