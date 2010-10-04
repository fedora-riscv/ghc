Name: ghc
Version: 6.4.1
Release: 0.el4
Summary: Glasgow Haskell Compilation system
License: BSD
Group: Development/Languages
Source1: http://archives.fedoraproject.org/pub/archive/fedora/linux/extras/3/i386/ghc-6.4.1-1.fc3.i386.rpm
Source2: http://archives.fedoraproject.org/pub/archive/fedora/linux/extras/3/i386/ghc641-6.4.1-1.fc3.i386.rpm
Source3: http://archives.fedoraproject.org/pub/archive/fedora/linux/extras/3/x86_64/ghc-6.4.1-1.fc3.x86_64.rpm
Source4: http://archives.fedoraproject.org/pub/archive/fedora/linux/extras/3/x86_64/ghc641-6.4.1-1.fc3.x86_64.rpm
URL: http://haskell.org/ghc/
Requires: gcc, gmp-devel
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
ExclusiveArch: %{ix86} x86_64

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
rpm2cpio ${RPM_SOURCE_DIR}/%{name}-%{version}-1.fc3.%{_arch}.rpm | cpio --extract
rpm2cpio ${RPM_SOURCE_DIR}/%{name}641-%{version}-1.fc3.%{_arch}.rpm | cpio --extract

%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(-,root,root,-)
%{_bindir}/*
%{_libdir}/*
%{_docdir}/*

%changelog
* Tue Sep 28 2010 Jens Petersen <petersen@redhat.com> - 6.10.1-0.el5
- bootstrap FE3 ghc bin packages to EPEL 4
