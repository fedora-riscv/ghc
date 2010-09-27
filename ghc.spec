Name: ghc
Version: 6.10.4
Release: 0%{?dist}
Summary: Glasgow Haskell Compilation system
License: BSD
Group: Development/Languages
Source1: http://kojipkgs.fedoraproject.org/packages/ghc/6.10.4/2.fc12/i686/ghc-6.10.4-2.fc12.i686.rpm
Source2: http://kojipkgs.fedoraproject.org/packages/ghc/6.10.4/2.fc12/ppc/ghc-6.10.4-2.fc12.ppc.rpm
Source3: http://kojipkgs.fedoraproject.org/packages/ghc/6.10.4/2.fc12/x86_64/ghc-6.10.4-2.fc12.x86_64.rpm
URL: http://haskell.org/ghc/
Requires: gcc, gmp-devel
Requires(post): policycoreutils
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
ExclusiveArch: i386 ppc x86_64

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
mkdir -p .%{_bindir} .%{_libdir} .%{_docdir} .%{_mandir}/man1
rpm2cpio ${RPM_SOURCE_DIR}/%{name}-%{version}-2.fc12.%{_arch}.rpm | cpio --extract

%clean
rm -rf $RPM_BUILD_ROOT

%post
semanage fcontext -a -t unconfined_execmem_exec_t %{_libdir}/ghc-%{version}/ghc >/dev/null 2>&1 || :
restorecon %{_libdir}/ghc-%{version}/ghc

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
%defattr(-,root,root,-)
%{_bindir}/*
%{_libdir}/*
%{_docdir}/*
%{_mandir}/man1/*

%changelog
* Fri Sep 24 2010 Jens Petersen <petersen@redhat.com> - 6.10.4-0
- bootstrap F12 ghc bin packages to EPEL 6
