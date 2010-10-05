# speed up test builds by not building profiled libraries
%define build_prof 1
%define build_doc 1

Name:		ghc
Version:	6.8.3
Release:	12%{?dist}
Summary:	Glasgow Haskell Compilation system
# See https://bugzilla.redhat.com/bugzilla/show_bug.cgi?id=239713
ExcludeArch:	alpha ppc
License:	BSD
Group:		Development/Languages
Source0:	http://www.haskell.org/ghc/dist/%{version}/ghc-%{version}-src.tar.bz2
Source1:	http://www.haskell.org/ghc/dist/%{version}/ghc-%{version}-src-extralibs.tar.bz2
URL:		http://haskell.org/ghc/
Requires:	gcc, gmp-devel, readline-devel
Requires(post): policycoreutils
BuildRoot:	%{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
Obsoletes:      ghc682, ghc681, ghc661, ghc66
BuildRequires:  ghc, sed
BuildRequires:  gmp-devel, readline-devel
BuildRequires:  freeglut-devel, openal-devel
%if %{build_doc}
# haddock generates docs in libraries
BuildRequires: libxslt, docbook-style-xsl, haddock
%endif

%description
GHC is a state-of-the-art programming suite for Haskell, a purely
functional programming language.  It includes an optimising compiler
generating good code for a variety of platforms, together with an
interactive system for convenient, quick development.  The
distribution includes space and time profiling facilities, a large
collection of libraries, and support for various language
extensions, including concurrency, exceptions, and a foreign language
interface.

%if %{build_prof}
%package prof
Summary:	Profiling libraries for GHC
Group:		Development/Libraries
Requires:	%{name} = %{version}-%{release}
Obsoletes:	ghc682-prof, ghc681-prof, ghc661-prof, ghc66-prof

%description prof
Profiling libraries for Glorious Glasgow Haskell Compilation System
(GHC).  They should be installed when GHC's profiling subsystem is
needed.
%endif

%package doc
Summary:	Documentation for GHC
Group:		Development/Languages
Requires:	%{name} = %{version}-%{release}
Requires(post): haddock

%description doc
Preformatted documentation for the Glorious Glasgow Haskell
Compilation System (GHC) and its libraries.  It should be installed if
you like to have local access to the documentation in HTML format.

# the debuginfo subpackage is currently empty anyway, so don't generate it
%define debug_package %{nil}

%prep
%setup -q -n %{name}-%{version} -b1

%build
%if !%{build_prof}
echo "GhcLibWays=" >> mk/build.mk
echo "GhcRTSWays=thr debug" >> mk/build.mk
%endif

%if %{build_doc}
echo "XMLDocWays   = html" >> mk/build.mk
echo "HADDOCK_DOCS = YES" >> mk/build.mk
%endif

#export HaddockCmd=%{_bindir}/haddock-0.9

./configure --prefix=%{_prefix} --exec-prefix=%{_exec_prefix} \
  --bindir=%{_bindir} --sbindir=%{_sbindir} --sysconfdir=%{_sysconfdir} \
  --datadir=%{_datadir} --includedir=%{_includedir} --libdir=%{_libdir} \
  --libexecdir=%{_libexecdir} --localstatedir=%{_localstatedir} \
  --sharedstatedir=%{_sharedstatedir} --mandir=%{_mandir}

make %{_smp_mflags}
make %{_smp_mflags} -C libraries

%if %{build_doc}
make %{_smp_mflags} html
%endif

%install
rm -rf $RPM_BUILD_ROOT

make DESTDIR=${RPM_BUILD_ROOT} install

%if %{build_doc}
make DESTDIR=${RPM_BUILD_ROOT} install-docs
%endif

SRC_TOP=$PWD
rm -f rpm-*-filelist rpm-*.files
( cd $RPM_BUILD_ROOT
  find .%{_libdir}/%{name}-%{version} \( -type d -fprintf $SRC_TOP/rpm-dir.files "%%%%dir %%p\n" \) -o \( -type f \( -name '*.p_hi' -o -name '*_p.a' \) -fprint $SRC_TOP/rpm-prof.files \) -o \( -not -name 'package.conf*' -fprint $SRC_TOP/rpm-lib.files \)
  find .%{_docdir}/%{name}/* -type d ! -name libraries > $SRC_TOP/rpm-doc-dir.files
)

# make paths absolute (filter "./usr" to "/usr")
sed -i -e "s|\.%{_prefix}|%{_prefix}|" rpm-*.files

cat rpm-dir.files rpm-lib.files > rpm-base-filelist
%if %{build_prof}
cat rpm-prof.files > rpm-prof-filelist
%endif

# these are handled as alternatives
for i in hsc2hs runhaskell; do
  if [ -x ${RPM_BUILD_ROOT}%{_bindir}/$i-ghc ]; then
    rm ${RPM_BUILD_ROOT}%{_bindir}/$i
  else
    mv ${RPM_BUILD_ROOT}%{_bindir}/$i{,-ghc}
  fi
done

%clean
rm -rf $RPM_BUILD_ROOT

%post
semanage fcontext -a -t unconfined_execmem_exec_t %{_libdir}/ghc-%{version}/{ghc-%{version},ghc-pkg.bin,hsc2hs-bin} >/dev/null 2>&1 || :
restorecon %{_libdir}/ghc-%{version}/{ghc-%{version},ghc-pkg.bin,hsc2hs-bin}

# Alas, GHC, Hugs, and nhc all come with different set of tools in
# addition to a runFOO:
#
#   * GHC:  hsc2hs
#   * Hugs: hsc2hs, cpphs
#   * nhc:  cpphs
#
# Therefore it is currently not possible to use --slave below to form
# link groups under a single name 'runhaskell'. Either these tools
# should be disentangled from the Haskell implementations, or all
# implementations should have the same set of tools. *sigh*

update-alternatives --install %{_bindir}/runhaskell runhaskell \
  %{_bindir}/runghc 500
update-alternatives --install %{_bindir}/hsc2hs hsc2hs \
  %{_bindir}/hsc2hs-ghc 500

%post doc
( cd %{_docdir}/ghc/libraries && ./gen_contents_index ) || :

%preun
if [ "$1" = 0 ]; then
  update-alternatives --remove runhaskell %{_bindir}/runghc
  update-alternatives --remove hsc2hs     %{_bindir}/hsc2hs-ghc
fi

%files -f rpm-base-filelist
%defattr(-,root,root,-)
%doc ANNOUNCE HACKING LICENSE README
%if %{build_doc}
%doc %{_mandir}/man1/ghc.*
%endif
%{_bindir}/*
%config(noreplace) %{_libdir}/ghc-%{version}/package.conf
%ghost %{_libdir}/ghc-%{version}/package.conf.old

%if %{build_prof}
%files prof -f rpm-prof-filelist
%defattr(-,root,root,-)
%endif

%files doc -f rpm-doc-dir.files
%defattr(-,root,root,-)
%dir %{_docdir}/%{name}
%dir %{_docdir}/%{name}/libraries
%if %{build_doc}
%{_docdir}/%{name}/index.html
%{_docdir}/%{name}/libraries/gen_contents_index
%ghost %{_docdir}/%{name}/libraries/doc-index*.html
%ghost %{_docdir}/%{name}/libraries/haddock.css
%ghost %{_docdir}/%{name}/libraries/haddock*.js
%ghost %{_docdir}/%{name}/libraries/haskell_icon.gif
%ghost %{_docdir}/%{name}/libraries/index.html
%ghost %{_docdir}/%{name}/libraries/minus.gif
%ghost %{_docdir}/%{name}/libraries/plus.gif
%endif


%changelog
* Fri Oct  1 2010 Jens Petersen <petersen@redhat.com> - 6.8.3-12.el4
- build with haddock rather than haddock09 and
  drop ghc-6.8.3-libraries-config.patch for haddock09
- drop buildrequires on happy
- drop macros.ghc from here
- exclude ppc

* Fri Feb 13 2009 Jens Petersen <petersen@redhat.com> - 6.8.3-11
- backport latest macros.ghc:

* Mon Dec  1 2008 Jens Petersen <petersen@redhat.com>
- update macros.ghc to latest proposed revised packaging guidelines:
  - use runghc
  - drop trivial cabal_build and cabal_haddock macros
  - ghc_register_pkg and ghc_unregister_pkg replace ghc_preinst_script,
    ghc_postinst_script, ghc_preun_script, and ghc_postun_script
- ghc-prof does not need to own libraries dirs owned by main package

* Thu Oct 23 2008 Jens Petersen <petersen@redhat.com> - 6.8.3-10.fc9
- remove redundant --haddockdir (interfacedir in Cabal-1.2) from cabal_configure
- add a ghc682-prof dummy package to stop ghc-prof and ghc682-prof obsoleting
  each other (reported by thingwath, #467893)

* Thu Oct 23 2008 Jens Petersen <petersen@redhat.com> - 6.8.3-9
- use gen_contents_index to re-index haddock
- add %%pkg_docdir to cabal_configure
- requires(post) haddock09 for doc
- improve doc file lists
- no longer need to create ghost package.conf.old
- remove or rename alternatives files more consistently

* Tue Oct 14 2008 Bryan O'Sullivan <bos@serpentine.com> 6.8.3-8
- Regenerate the haddock doc index automatically
- Update macros to fit in with this scheme

* Mon Oct 13 2008 Jens Petersen <petersen@redhat.com> - 6.8.3-7
- add selinux file context for unconfined_execmem following darcs package

* Wed Oct  1 2008 Bryan O'Sullivan <bos@serpentine.com> 6.8.3-6
* Rename hsc2hs to hsc2hs-ghc so the alternatives symlink to it will work

* Wed Sep 24 2008 Jens Petersen <petersen@redhat.com> - 6.8.3-5
- bring back including haddock-generated lib docs, now under docdir/ghc
- fix macros.ghc filepath (#460304)
- spec file cleanups:
- fix the source urls back
- drop requires chkconfig
- do not override __spec_install_post
- setup docs building in build.mk
- no longer need to remove network/include/Typeable.h
- install binaries under libdir not libexec
- remove hsc2hs and runhaskell binaries since they are alternatives

* Wed Sep 17 2008 Jens Petersen <petersen@redhat.com> - 6.8.3-4
- add macros.ghc for new Haskell Packaging Guidelines (#460304)

* Wed Jun 18 2008 Bryan O'Sullivan <bos@serpentine.com> - 6.8.3-3
- Add symlinks from _libdir, where ghc looks, to _libexecdir
- Patch libraries/gen_contents_index to use haddock-0.9

* Wed Jun 18 2008 Bryan O'Sullivan <bos@serpentine.com> - 6.8.3-2
- Remove unnecessary dependency on alex

* Wed Jun 18 2008 Bryan O'Sullivan <bos@serpentine.com> - 6.8.3-1
- Upgrade to 6.8.3
- Drop the ghc682-style naming scheme, obsolete those packages
- Manually strip binaries

* Tue Apr  8 2008 Jens Petersen <petersen@redhat.com> - 6.8.2-10
- another rebuild attempt

* Thu Feb 14 2008 Jens Petersen <petersen@redhat.com> - 6.8.2-9
- remove unrecognized --docdir and --htmldir from configure
- drop old buildrequires on libX11-devel and libXt-devel
- rebuild with gcc43

* Sun Jan 06 2008 Bryan O'Sullivan <bos@serpentine.com> - 6.8.2-7
- More attempts to fix docdir

* Sun Jan 06 2008 Bryan O'Sullivan <bos@serpentine.com> - 6.8.2-6
- Fix docdir

* Tue Dec 12 2007 Bryan O'Sullivan <bos@serpentine.com> - 6.8.2-1
- Update to 6.8.2

* Fri Nov 23 2007 Bryan O'Sullivan <bos@serpentine.com> - 6.8.1-2
- Exclude alpha

* Thu Nov  8 2007 Bryan O'Sullivan <bos@serpentine.com> - 6.8.1-2
- Drop bit-rotted attempts at making package relocatable

* Sun Nov  4 2007 Michel Salim <michel.sylvan@gmail.com> - 6.8.1-1
- Update to 6.8.1

* Sat Sep 29 2007 Bryan O'Sullivan <bos@serpentine.com> - 6.8.0.20070928-2
- add happy to BuildRequires

* Sat Sep 29 2007 Bryan O'Sullivan <bos@serpentine.com> - 6.8.0.20070928-1
- prepare for GHC 6.8.1 by building a release candidate snapshot

* Thu May 10 2007 Bryan O'Sullivan <bos@serpentine.com> - 6.6.1-3
- install man page for ghc

* Thu May 10 2007 Bryan O'Sullivan <bos@serpentine.com> - 6.6.1-2
- exclude ppc64 for now, due to lack of time to bootstrap

* Wed May  9 2007 Bryan O'Sullivan <bos@serpentine.com> - 6.6.1-1
- update to 6.6.1 release

* Mon Jan 22 2007 Jens Petersen <petersen@redhat.com> - 6.6-2
- remove truncated duplicate Typeable.h header in network package
  (Bryan O'Sullivan, #222865)

* Fri Nov  3 2006 Jens Petersen <petersen@redhat.com> - 6.6-1
- update to 6.6 release
- buildrequire haddock >= 0.8
- fix summary of ghcver package (Michel Salim, #209574)

* Thu Sep 28 2006 Jens Petersen <petersen@redhat.com> - 6.4.2-4
- turn on docs generation again

* Mon Sep 25 2006 Jens Petersen <petersen@redhat.com> - 6.4.2-3.fc6
- ghost package.conf.old (Gérard Milmeister)
- set unconfined_execmem_exec_t context on executables with ghc rts (#195821)
- turn off building docs until haddock is back

* Sat Apr 29 2006 Jens Petersen <petersen@redhat.com> - 6.4.2-2.fc6
- buildrequire libXt-devel so that the X11 package and deps get built
  (Garrett Mitchener, #190201)

* Thu Apr 20 2006 Jens Petersen <petersen@redhat.com> - 6.4.2-1.fc6
- update to 6.4.2 release

* Thu Mar  2 2006 Jens Petersen <petersen@redhat.com> - 6.4.1-3.fc5
- buildrequire libX11-devel instead of xorg-x11-devel (Kevin Fenzi, #181024)
- make ghc-doc require ghc (Michel Salim, #180449)

* Tue Oct 11 2005 Jens Petersen <petersen@redhat.com> - 6.4.1-2.fc5
- turn on build_doc since haddock is now in Extras
- no longer specify ghc version to build with (Ville Skyttä, #170176)

* Tue Sep 20 2005 Jens Petersen <petersen@redhat.com> - 6.4.1-1.fc5
- 6.4.1 release
  - the following patches are now upstream: ghc-6.4-powerpc.patch,
    rts-GCCompact.h-x86_64.patch, ghc-6.4-dsforeign-x86_64-1097471.patch,
    ghc-6.4-rts-adjustor-x86_64-1097471.patch
  - builds with gcc4 so drop %%_with_gcc32
  - x86_64 build restrictions (no ghci and split objects) no longer apply

* Tue May 31 2005 Jens Petersen <petersen@redhat.com>
- add %%dist to release

* Thu May 12 2005 Jens Petersen <petersen@redhat.com> - 6.4-8
- initial import into Fedora Extras

* Thu May 12 2005 Jens Petersen <petersen@haskell.org>
- add build_prof and build_doc switches for -doc and -prof subpackages
- add _with_gcc32 switch since ghc-6.4 doesn't build with gcc-4.0

* Wed May 11 2005 Jens Petersen <petersen@haskell.org> - 6.4-7
- make package relocatable (ghc#1084122)
  - add post install scripts to replace prefix in driver scripts
- buildrequire libxslt and docbook-style-xsl instead of docbook-utils and flex

* Fri May  6 2005 Jens Petersen <petersen@haskell.org> - 6.4-6
- add ghc-6.4-dsforeign-x86_64-1097471.patch and
  ghc-6.4-rts-adjustor-x86_64-1097471.patch from trunk to hopefully fix
  ffi support on x86_64 (Simon Marlow, ghc#1097471)
- use XMLDocWays instead of SGMLDocWays to build documentation fully

* Mon May  2 2005 Jens Petersen <petersen@haskell.org> - 6.4-5
- add rts-GCCompact.h-x86_64.patch to fix GC issue on x86_64 (Simon Marlow)

* Thu Mar 17 2005 Jens Petersen <petersen@haskell.org> - 6.4-4
- add ghc-6.4-powerpc.patch (Ryan Lortie)
- disable building interpreter rather than install and delete on x86_64

* Wed Mar 16 2005 Jens Petersen <petersen@haskell.org> - 6.4-3
- make ghc require ghcver of same ver-rel
- on x86_64 remove ghci for now since it doesn't work and all .o files

* Tue Mar 15 2005 Jens Petersen <petersen@haskell.org> - 6.4-2
- ghc requires ghcver (Amanda Clare)

* Sat Mar 12 2005 Jens Petersen <petersen@haskell.org> - 6.4-1
- 6.4 release
  - x86_64 build no longer unregisterised
- use sed instead of perl to tidy filelists
- buildrequire ghc64 instead of ghc-6.4
- no epoch for ghc64-prof's ghc64 requirement
- install docs directly in docdir

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
