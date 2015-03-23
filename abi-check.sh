#!/bin/sh

REL=$(rpm -q --qf "%{release}" ghc-compiler)
ARCH=$(arch)
PKGS=$(rpm -qa | grep -- -$REL | grep -v -- -devel | sort | sed -e "s/-[0-9.]\+-.*//")

for i in $PKGS; do
    LOCAL=$(rpm -q --provides $i | grep ^ghc\( | grep -v =)
    REPO=$(dnf repoquery -q --provides $i | grep ^ghc\( | grep -v = | sort | uniq)
    if [ "$LOCAL" != "$REPO" ]; then
        echo $LOCAL
        echo $REPO
    fi
done
