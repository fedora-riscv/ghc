## ghc seeding bootstrap spec file

%define ghcver ghc64

Name:		ghc
Version:	6.4
Release:	1%{?dist}
Summary:	Glasgow Haskell Compilation system
License:	BSD style
Group:		Development/Languages
Source1:	http://www.haskell.org/ghc/dist/%{version}/ghc-%{version}-i386-unknown-linux.tar.bz2
Source2:	http://www.haskell.org/ghc/dist/%{version}/ghc-%{version}-ppc-unknown-linux.tar.bz2
Source3:	http://www.haskell.org/ghc/dist/%{version}/ghc-%{version}-x86_64-unknown-linux.tar.bz2
URL:		http://haskell.org/ghc/
Requires:	%{ghcver} = %{version}-%{release}
BuildRoot:	%{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
BuildRequires:  sed
Prefix: %{_prefix}
Patch1:		ghc-doc-no-ps-install.patch
ExclusiveArch:	i386 ppc x86_64

%description
GHC is a state-of-the-art programming suite for Haskell, a purely
functional programming language.  It includes an optimising compiler
generating good code for a variety of platforms, together with an
interactive system for convenient, quick development.  The
distribution includes space and time profiling facilities, a large
collection of libraries, and support for various language
extensions, including concurrency, exceptions, and a foreign language
interface.

%package -n %{ghcver}
Summary:	Documentation for GHC
Group:		Development/Languages
Requires:	gcc gmp-devel readline-devel

%description -n %{ghcver}
GHC is a state-of-the-art programming suite for Haskell, a purely
functional programming language.  It includes an optimising compiler
generating good code for a variety of platforms, together with an
interactive system for convenient, quick development.  The
distribution includes space and time profiling facilities, a large
collection of libraries, and support for various language
extensions, including concurrency, exceptions, and a foreign language
interfaces.

This package contains all the main files and libraries of version %{version}.

%package -n %{ghcver}-prof
Summary:	Profiling libraries for GHC
Group:		Development/Libraries
Requires:	%{ghcver} = %{version}-%{release}
Obsoletes:	ghc-prof

%description -n %{ghcver}-prof
Profiling libraries for Glorious Glasgow Haskell Compilation System
(GHC).  They should be installed when GHC's profiling subsystem is
needed.

%package doc
Summary:	Documentation for GHC
Group:		Development/Languages

%description doc
Preformatted documentation for the Glorious Glasgow Haskell
Compilation System (GHC) and its libraries.  It should be installed if
you like to have local access to the documentation in HTML format.

# the debuginfo subpackage is currently empty anyway, so don't generate it
%define debug_package %{nil}
%define __spec_install_post /usr/lib/rpm/brp-compress

%prep
rm -rf %{name}-%{version}
tar jxf ${RPM_SOURCE_DIR}/%{name}-%{version}-%{_arch}-unknown-linux.tar.bz2
%setup -T -D
%patch1 -p1 -b .ps

%build
./configure --prefix=%{_prefix} --libdir=%{_libdir}
make prefix=%{_prefix} libdir=%{_libdir}/%{name}-%{version}

%install
rm -rf $RPM_BUILD_ROOT

make prefix=$RPM_BUILD_ROOT%{_prefix} libdir=$RPM_BUILD_ROOT%{_libdir}/%{name}-%{version} datadir=$RPM_BUILD_ROOT%{_docdir}/%{name}-%{version} htmldir=$RPM_BUILD_ROOT%{_docdir}/%{name}-%{version} install-dirs install-bin install-libs install-datas install-docs

SRC_TOP=$PWD
rm -f rpm-*-filelist rpm-*.files
( cd $RPM_BUILD_ROOT
  find .%{_libdir}/%{name}-%{version} \( -type d -fprintf $SRC_TOP/rpm-dir.files "%%%%dir %%p\n" \) -o \( -type f \( -name '*.p_hi' -o -name '*_p.a' \) -fprint $SRC_TOP/rpm-prof.files \) -o \( -not -name 'package.conf' -fprint $SRC_TOP/rpm-lib.files \)
)

# make paths absolute (filter "./usr" to "/usr")
sed -i -e "s|\.%{_prefix}|%{_prefix}|" rpm-*.files

cat rpm-dir.files rpm-lib.files > rpm-base-filelist
cat rpm-dir.files rpm-prof.files > rpm-prof-filelist

%clean
rm -rf $RPM_BUILD_ROOT

%post
## tweak prefix in drivers scripts if relocating
if [ "${RPM_INSTALL_PREFIX}" != "%{_prefix}" ]; then
  BINDIR=`echo %{_bindir} | sed -e "s|%{_prefix}|${RPM_INSTALL_PREFIX}|"`
  sed -i "s|%{_prefix}|${RPM_INSTALL_PREFIX}|" ${BINDIR}/{ghcprof,hsc2hs}
fi

%post -n %{ghcver}
## tweak prefix in drivers scripts if relocating
if [ "${RPM_INSTALL_PREFIX}" != "%{_prefix}" ]; then
  BINDIR=`echo %{_bindir} | sed -e "s|%{_prefix}|${RPM_INSTALL_PREFIX}|"`
  LIBDIR=`echo %{_libdir} | sed -e "s|%{_prefix}|${RPM_INSTALL_PREFIX}|"`
  sed -i "s|%{_prefix}|${RPM_INSTALL_PREFIX}|" ${BINDIR}/ghc*-%{version} ${LIBDIR}/ghc-%{version}/package.conf
fi

%files
%defattr(-,root,root,-)
%{_bindir}/*
%exclude %{_bindir}/ghc*%{version}

%files -n %{ghcver} -f rpm-base-filelist
%defattr(-,root,root,-)
%doc ANNOUNCE LICENSE README
%{_bindir}/ghc*%{version}
%config(noreplace) %{_libdir}/ghc-%{version}/package.conf

%files -n %{ghcver}-prof -f rpm-prof-filelist
%defattr(-,root,root,-)

%files doc
%defattr(-,root,root,-)
%{_docdir}/%{name}-%{version}

%changelog
* Tue May 31 2005 Jens Petersen <petersen@redhat.com>
- initial seed bootstrap package for Fedora Extras for i386, ppc and x86_64
- add %%dist to release

* Thu May 12 2005 Jens Petersen <petersen@haskell.org>
- add build_prof and build_doc switches for -doc and -prof subpackages

* Wed May 11 2005 Jens Petersen <petersen@haskell.org>
- make package relocatable (ghc#1084122)
  - add post install scripts to replace prefix in driver scripts

* Wed Mar 16 2005 Jens Petersen <petersen@haskell.org>
- make ghc require ghcver of same ver-rel

* Tue Mar 15 2005 Jens Petersen <petersen@haskell.org>
- ghc requires ghcver (Amanda Clare)

* Sat Mar 12 2005 Jens Petersen <petersen@haskell.org>
- 6.4 release
- use sed instead of perl to tidy filelists
- no epoch for ghc64-prof's ghc64 requirement

* Fri Jan 21 2005 Jens Petersen <petersen@haskell.org> - 6.2.2-2
- add x86_64 port
  - build unregistered and without splitobjs
  - specify libdir to configure and install
- rename ghc-prof to ghcXYZ-prof, which obsoletes ghc-prof

* Mon Dec  6 2004 Jens Petersen <petersen@haskell.org> - 6.2.2-1
- move ghc requires to ghcXYZ

* Wed Nov 24 2004 Jens Petersen <petersen@haskell.org> - 6.2.2-0.fdr.1
- ghc622
  - provide ghc = %%version
- require gcc, gmp-devel and readline-devel

* Fri Oct 15 2004 Gerard Milmeister <gemi@bluewin.ch> - 6.2.2-0.fdr.1
- New Version 6.2.2

* Mon Mar 22 2004 Gerard Milmeister <gemi@bluewin.ch> - 6.2.1-0.fdr.1
- New Version 6.2.1

* Tue Dec 16 2003 Gerard Milmeister <gemi@bluewin.ch> - 6.2-0.fdr.1
- New Version 6.2

* Tue Dec 16 2003 Gerard Milmeister <gemi@bluewin.ch> - 6.0.1-0.fdr.3
- A few minor specfile tweaks

* Mon Dec 15 2003 Gerard Milmeister <gemi@bluewin.ch> - 6.0.1-0.fdr.2
- Different file list generation

* Mon Oct 20 2003 Gerard Milmeister <gemi@bluewin.ch> - 6.0.1-0.fdr.1
- First Fedora release
- Added generated html docs, so that haddock is not needed

* Wed Sep 26 2001 Manuel Chakravarty
- small changes for 5.04

* Wed Sep 26 2001 Manuel Chakravarty
- split documentation off into a separate package
- adapt to new docbook setup in RH7.1

* Mon Apr 16 2001 Manuel Chakravarty
- revised for 5.00
- also runs autoconf automagically if no ./configure found

* Thu Jun 22 2000 Sven Panne
- removed explicit usage of hslibs/docs, it belongs to ghc/docs/set

* Sun Apr 23 2000 Manuel Chakravarty
- revised for ghc 4.07; added suggestions from Pixel <pixel@mandrakesoft.com>
- added profiling package

* Tue Dec 7 1999 Manuel Chakravarty
- version for use from CVS

* Thu Sep 16 1999 Manuel Chakravarty
- modified for GHC 4.04, patchlevel 1 (no more 62 tuple stuff); minimises use
  of patch files - instead emits a build.mk on-the-fly

* Sat Jul 31 1999 Manuel Chakravarty
- modified for GHC 4.04

* Wed Jun 30 1999 Manuel Chakravarty
- some more improvements from vbzoli

* Fri Feb 26 1999 Manuel Chakravarty
- modified for GHC 4.02

* Thu Dec 24 1998 Zoltan Vorosbaranyi 
- added BuildRoot
- files located in /usr/local/bin, /usr/local/lib moved to /usr/bin, /usr/lib

* Tue Jul 28 1998 Manuel Chakravarty
- original version