Name: ghc
Version: 6.12.3
Release: 31%{?dist}
Summary: Glasgow Haskell Compilation system
License: BSD
Group: Development/Languages
Source0: ghc-7.0.4-31.3.fc16.ppc64.tar.gz
URL: http://haskell.org/ghc/
ExclusiveArch: ppc64

%description
GHC is a state-of-the-art programming suite for Haskell, a purely
functional programming language.  It includes an optimising compiler
generating good code for a variety of platforms, together with an
interactive system for convenient, quick development.  The
distribution includes space and time profiling facilities, a large
collection of libraries, and support for various language
extensions, including concurrency, exceptions, and a foreign language
interface.

# the debuginfo subpackage is currently empty anyway, so don't generate it
%global debug_package %{nil}

%prep

%build

%install
cd ${RPM_BUILD_ROOT}
tar zxvf %{SOURCE0}


%post
update-alternatives --install %{_bindir}/runhaskell runhaskell \
  %{_bindir}/runghc 500
update-alternatives --install %{_bindir}/hsc2hs hsc2hs \
  %{_bindir}/hsc2hs-ghc 500

%preun
if [ "$1" = 0 ]; then
  update-alternatives --remove runhaskell %{_bindir}/runghc
  update-alternatives --remove hsc2hs     %{_bindir}/hsc2hs-ghc
fi

%files
%{_bindir}/*
%{_libdir}/*
%{_docdir}/*
%{_mandir}/man1/*
%{_sysconfdir}/*


%changelog
* Tue May  8 2012 Jens Petersen <petersen@redhat.com> - 6.12.3-31
- import ghc-7.0.4-31.3.fc16.ppc64

* Sat Sep 25 2010 Jens Petersen <petersen@redhat.com> - 6.10.4-1
- fix the arch for i686 and use _target_cpu

* Fri Sep 24 2010 Jens Petersen <petersen@redhat.com> - 6.10.4-0
- bootstrap F12 ghc bin packages to EPEL 6
