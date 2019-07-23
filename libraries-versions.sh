#!/bin/sh

if [ ! -d libraries ]; then
    echo Is CWD a ghc source tree?
    exit 1
fi

cd libraries

grep -i ^version: $(find * -name "*.cabal" | sort) | grep -v -e "\(Win32\|cabal-\|gmp.old\|gmp2\|integer-simple\|tests\|bench\)" | sed -e "s!.*/\([^/]*\).cabal:[Vv]ersion: \+!\1-!"
