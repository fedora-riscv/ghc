#!/bin/sh

[ $# -ne 2 ] && echo "Usage: $(basename $0) ver-rel1 ver-rel2" && exit 1

if [ "$1" = "$2" ]; then
    echo "ver-rel's must be different!"
    exit 1
fi

#set -x

mkdir -p koji
cd koji

for i in $1 $2; do
    if [ ! -d "$i" ]; then
        mkdir -p $i/{x86_64,i686,armv7hl}
        cd $i
        for a in x86_64 i686 armv7hl; do
            cd $a
            koji download-build --arch=$a ghc-$i
            cd ..
        done
        cd ..
    fi
done

for a in x86_64 i686 armv7hl; do
    echo "= $a ="
    for i in $1/$a/*; do
        PKGVER=$(rpm -qp --qf "%{name}-%{version}" $i)
        PKG2=$(ls $2/$a/$PKGVER*.$a.rpm)
        PROV1=$(rpm -qp --provides $i | grep ^ghc\( | grep -v =)
        PROV2=$(rpm -qp --provides $PKG2 | grep ^ghc\( | grep -v =)
#        if [ -n "$PROV1" ]; then
#            echo $PROV1
#        else
#            echo "no provides for $i"
#        fi
        if [ -n "$PROV2" ]; then
            if [ "$PROV1" != "$PROV2" ]; then
                echo $PROV2
            fi
#        else
#            echo "no provides for $PKG2"
        fi
    done
done
