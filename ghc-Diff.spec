#
# Conditional build:
%bcond_without	prof	# profiling library
#
%define		pkgname	Diff
Summary:	Diff algorithm in pure Haskell
Name:		ghc-%{pkgname}
Version:	1.0.2
Release:	1
License:	BSD
Group:		Development/Languages
#Source0Download: https://hackage.haskell.org/package/Diff
Source0:	https://hackage.haskell.org/package/%{pkgname}-%{version}/%{pkgname}-%{version}.tar.gz
# Source0-md5:	a846311f7c08a5331dbacfcc66e7af07
URL:		https://hackage.haskell.org/package/Diff
BuildRequires:	ghc
%if %{with prof}
BuildRequires:	ghc-prof
%endif
BuildRequires:	rpmbuild(macros) >= 1.608
%requires_eq	ghc
Requires(post,postun):	/usr/bin/ghc-pkg
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

# debuginfo is not useful for ghc
%define		_enable_debug_packages	0

# don't compress haddock files
%define		_noautocompressdoc	*.haddock

%description
Implementation of the standard diff algorithm in Haskell.

Time complexity is O(ND) (input length * number of differences). Space
complexity is O(D^2).  Includes utilities for pretty printing.

%package prof
Summary:	Profiling %{pkgname} library for GHC
Group:		Development/Libraries
Requires:	%{name} = %{version}-%{release}

%description prof
Profiling %{pkgname} library for GHC. Should be installed when GHC's
profiling subsystem is needed.

%prep
%setup -q -n %{pkgname}-%{version}

%build
runhaskell Setup.lhs configure -v2 \
	%{?with_prof:--enable-library-profiling} \
	--prefix=%{_prefix} \
	--libdir=%{_libdir} \
	--libexecdir=%{_libexecdir} \
	--docdir=%{_docdir}/%{name}-%{version}

runhaskell Setup.lhs build

runhaskell Setup.lhs haddock --executables

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT%{_libdir}/%{ghcdir}/lib/package.conf.d

runhaskell Setup.lhs copy --destdir=$RPM_BUILD_ROOT

# work around automatic haddock docs installation
rm -rf %{name}-%{version}-doc
%{__mv} $RPM_BUILD_ROOT%{_docdir}/%{name}-%{version} %{name}-%{version}-doc

runhaskell Setup.lhs register \
	--gen-pkg-config=$RPM_BUILD_ROOT%{_libdir}/%{ghcdir}/lib/package.conf.d/%{pkgname}.conf

# the library directory name contains an ABI hash, so build the file lists
pkgdir=$(echo $RPM_BUILD_ROOT%{_libdir}/*-linux-%{ghcdir}/%{pkgname}-%{version}-*)
find $pkgdir -type d | sed -e "s|^$RPM_BUILD_ROOT|%dir |" > %{name}.files
find $pkgdir -type f ! -name '*_p.a' ! -name '*.p_hi' | sed -e "s|^$RPM_BUILD_ROOT||" >> %{name}.files
find $pkgdir -type f \( -name '*_p.a' -o -name '*.p_hi' \) | sed -e "s|^$RPM_BUILD_ROOT||" > %{name}-prof.files

%clean
rm -rf $RPM_BUILD_ROOT

%post
%ghc_pkg_recache

%postun
%ghc_pkg_recache

%files -f %{name}.files
%defattr(644,root,root,755)
%doc CHANGELOG.md LICENSE %{name}-%{version}-doc/html
%{_libdir}/%{ghcdir}/lib/package.conf.d/%{pkgname}.conf
%dir %{_libdir}/*-linux-%{ghcdir}
%{_libdir}/*-linux-%{ghcdir}/libHS%{pkgname}-%{version}-*.so

%if %{with prof}
%files prof -f %{name}-prof.files
%defattr(644,root,root,755)
%endif
