#!/bin/sh

set -e

echo 'main = return ()' > test.hs
ghc test.hs && ./test
