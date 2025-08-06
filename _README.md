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


# Sections in spec files

## Auto replacement
- Add `Provides: <package_name>`: Let other packages know this package can replace the `<package_name>`
- Add `Obsoletes: <package_name> <version>`: Replace the `<package_name>` with this package.
- Add `Conflicts: <package_name> <version>`: Prevent installation of this package if `<package_name>` is already installed, and vice versa. Need manually remove the conflicting package first.


# Setting the Spec files

## `Texlive`
- Install `texlive` using `install-tl` script.

The concepts between *compile-time paths* and *runtime paths*. If compile errors related to {%buildroot} being in paths, it means one of two things:
1. The TeX Live installer itself is generating incorrect, hardcoded paths. This is a less common scenario for a robust installer like `install-tl`, which is designed to handle `DESTDIR` environments.
2. The build process or a subsequent check is finding {%buildroot} in a file that it shouldn't, and this is being flagged as an error. This is the more likely scenario.

TeX Live's installer defaults to `/usr/local/texlive/<year>`, but the `%install` section of an RPM must install into `%{buildroot}` only.
This is the critical line from the log:
```
mkdir(/usr/local/texlive/) failed: Permission denied
```
RPM doesn’t allow writes to `/usr/local/` during `%install`.


Deal with this problem:
- Remove prebuilt format files to avoid embedded %{buildroot}. Then rebuild formats at install time.
```sh
%install
## other install here

## Remove prebuilt format files to avoid embedded %{buildroot}
find %{buildroot}/opt/texlive/%{version} -type f \
  \( -name 'install-tl.log' -o -name 'texlive.profile' -o -name '*.log' -o -name '*.map' -o -name '*.fmt' -o -name '*.base' -o -name '*.conf' \) -delete

%posttrans
## This part runs after all packages are installed
## Rebuild formats at install time
/opt/texlive/%{version}/bin/x86_64-linux/mktexlsr > /dev/null 2>&1 || :
/opt/texlive/%{version}/bin/x86_64-linux/updmap-sys > /dev/null 2>&1 || :
/opt/texlive/%{version}/bin/x86_64-linux/fmtutil-sys --all > /dev/null 2>&1 || :
```


There are 2 ways to set ENV paths for `texlive` packages:
1. Use `alternaives` to set the default path. (this way may better)
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
2. Use `PATH` environment variable to set the default path
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
- Also need to see `env` in `latex-workshop` to work properly.
```js
"latex-workshop.latex.tools": [
    "env": {
        "PATH": "/opt/texlive/%{version}/bin/x86_64-linux:${env:PATH}"
    }
  ]
"
```