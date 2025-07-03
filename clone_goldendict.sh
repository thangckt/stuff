### release tarball does not include submodules, so must clone with --recurse-submodules. And spec file does not allow to use git clone, then must use this script to create the tarball.

version="1.5.1"

# Clone the repository with submodules
git clone --recurse-submodules https://github.com/goldendict/goldendict.git
cd goldendict
git tag # list available tags
git checkout "$version"
git submodule update --init --recursive

# Create the tarball (with submodules)
cd ..
tar czf goldendict-"$version".tar.gz --transform='s/^goldendict/goldendict-"$version"/' goldendict
