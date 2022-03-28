#!/bin/sh

# script to generate dependency graph for fedora haskell libraries
# requires ghc, ghc-*-devel and graphviz to be installed 

set -e +x

mkdir -p .pkg-deps

cd .pkg-deps

# remove the closing line
ghc-pkg dot --global | sed '$d' > pkgs.dot

# check for binary deps too
# (exclude binlib for now since covered by libs): cpphs, darcs, hlint, hscolour, xmonad
for i in alex cabal-install ghc happy gtk2hs-buildtools haskell-platform xmobar; do
  PKG_THERE=yes
  PKG=`rpm -q --qf "%{name}-%{version}" $i` || { PKG_THERE=no ; echo "missing $i" ; }
  if [ "$PKG_THERE" = "yes" ]; then
    echo \"$PKG\" >> pkgs.dot
    case $i in
      haskell-platform)
        rpm -q --requires $i | grep -v rpmlib | grep -v ghc | sed -e "s/^/\"$PKG\" -> \"/g" -e "s/ = \(.*\)/-\1\"/" >> pkgs.dot
        ;;
      *)
        rpm -q --requires $i | grep -- -ghc | sed -e "s/libHS/\"$PKG\" -> \"/g" -e "s/-ghc.*/\"/" >> pkgs.dot
        ;;
    esac
  fi
done

# make sure all libs there
rpm -qa --qf "\"%{name}-%{version}\"\n" ghc-\* | egrep -v -- "(ghc-libs|-prof|-devel|-doc|rpm-macros)-" | sed -e s/^\"ghc-/\"/g >> pkgs.dot

# and add it back
echo "}" >> pkgs.dot

cp -p pkgs.dot pkgs.dot.orig

# ignore library packages provided by ghc (except ghc-6.12)
GHC_PKGS="array base-4 base-3 bin-package-db bytestring Cabal containers directory dph extensible-exceptions filepath ffi ghc-binary ghc-prim haskell98 hpc integer-gmp old-locale old-time pretty process random rts template-haskell time unix Win32"
for i in $GHC_PKGS; do sed -i -e /$i/d pkgs.dot; done

which tred &>/dev/null || { echo "graphviz is needed to generate graph" ; exit 1 ; }
cat pkgs.dot | tred | dot -Nfontsize=8 -Tsvg >pkgs.svg

if [ -n "$DISPLAY" ]; then
  xdg-open pkgs.svg
else
  echo open ".pkg-deps/pkgs.svg" to display pkg graph
fi
