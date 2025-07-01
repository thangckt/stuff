#!/bin/bash

##### ANCHOR: Info
# This script to update the versions of .spec files in the current directory.

##### ANCHOR: Parameters
### Helper functions
function fetch_github_version() {
    local repo_url="$1"
    new_version=$(curl -sL "${repo_url}/releases/latest" | sed -nE 's|.*href="[^"]*/tag/v?([0-9]+(\.[0-9]+)*)".*|\1|p' | head -n1)
    if [[ -z "$new_version" ]]; then
        echo "0.0"
        echo "Error: Unable to fetch the latest version from $repo_url"
        exit 1
    fi
    echo "$new_version"
}

function update_spec_version() {
    local spec_file="$1"
    local new_version="$2"

    current_version=$(grep -E '^Version:' "$spec_file" | awk '{print $2}')
    # Compare versions using sort -V (version sort)
    if [[ "$new_version" != "$current_version" ]] && [[ "$(printf "%s\n%s" "$current_version" "$new_version" | sort -V | tail -n1)" == "$new_version" ]]; then
        echo "Updating version: $current_version to $new_version"
        sed -i "s/^Version:[[:space:]]\+$current_version/Version:        $new_version/" "$spec_file"
    else
        echo "Current version ($current_version) is up to date."
    fi
}

##### SECTION: From GitHub
##### ANCHOR: rustdesk
repo_url="https://github.com/rustdesk/rustdesk"
spec_files="rpm_rustdesk.spec"
update_spec_version "$spec_files" $(fetch_github_version "$repo_url")

##### ANCHOR: electerm
repo_url="httpEs://github.com/electerm/electerm"
spec_files="rpm_electerm.spec"
update_spec_version "$spec_files" $(fetch_github_version "$repo_url")

##### ANCHOR: github-desktop
repo_url="https://github.com/pol-rivero/github-desktop-plus"
spec_files="rpm_github-desktop-plus.spec"
update_spec_version "$spec_files" $(fetch_github_version "$repo_url")
##### !SECTION
