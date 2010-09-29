Name: ghc
Version: 6.10.1
Release: 0.el5
Summary: Glasgow Haskell Compilation system
License: BSD
Group: Development/Languages
Source1: http://archives.fedoraproject.org/pub/archive/fedora/linux/updates/10/i386/ghc-6.10.1-9.fc10.i386.rpm
Source2: http://archives.fedoraproject.org/pub/archive/fedora/linux/updates/10/x86_64/ghc-6.10.1-9.fc10.x86_64.rpm
Source3: http://archives.fedoraproject.org/pub/archive/fedora/linux/updates/10/ppc/ghc-6.10.1-9.fc10.ppc.rpm
URL: http://haskell.org/ghc/
Requires: gcc, gmp-devel
Requires(post): policycoreutils
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
ExclusiveArch: %{ix86} x86_64 ppc

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
rm -rf $RPM_BUILD_ROOT
mkdir -p ${RPM_BUILD_ROOT}
cd ${RPM_BUILD_ROOT}
mkdir -p .%{_bindir} .%{_libdir} .%{_docdir} .%{_mandir}/man1 .%{_sysconfdir}/rpm
rpm2cpio ${RPM_SOURCE_DIR}/%{name}-%{version}-9.fc10.%{_arch}.rpm | cpio --extract

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
%{_sysconfdir}/rpm/*

%changelog
* Tue Sep 28 2010 Jens Petersen <petersen@redhat.com> - 6.10.1-0.el5
- bootstrap F10 ghc bin packages to EPEL 5
