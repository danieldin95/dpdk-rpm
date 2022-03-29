# Add option to build with examples
%bcond_with examples
# Add option to build without tools
%bcond_without tools

# Dont edit Version: and Release: directly, only these:
#% define commit0 7001c8fdb27357c67147c0a13cb3826e48c0f2bf
#% define date 20191128
#% define shortcommit0 %(c=%{commit0}; echo ${c:0:7})

%define ver 20.11.4
%define rel 3

%define srcname dpdk-stable

%define ninjaver  1.8.2
%define mesonver  0.49.2

Name: dpdk
Version: %{ver}
Release: %{rel}%{?commit0:.%{date}git%{shortcommit0}}%{?dist}
URL: http://dpdk.org
%if 0%{?commit0:1}
Source: http://dpdk.org/browse/dpdk/snapshot/dpdk-%{commit0}.tar.xz
%else
Source: http://fast.dpdk.org/rel/dpdk-%{ver}.tar.xz
%endif

%if 0%{?rhel} && 0%{?rhel} < 8
Source1: https://github.com/ninja-build/ninja/archive/v%{ninjaver}.tar.gz#/ninja-build-%{ninjaver}.tar.gz
Source2: https://github.com/mesonbuild/meson/releases/download/%{mesonver}/meson-%{mesonver}.tar.gz
%else
BuildRequires: meson
%endif

# Only needed for creating snapshot tarballs, not used in build itself
Source100: dpdk-snapshot.sh

# Patches only in dpdk package


Summary: Set of libraries and drivers for fast packet processing

#
# Note that, while this is dual licensed, all code that is included with this
# Pakcage are BSD licensed. The only files that aren't licensed via BSD is the
# kni kernel module which is dual LGPLv2/BSD, and thats not built for fedora.
#
License: BSD and LGPLv2 and GPLv2

#
# The DPDK is designed to optimize througput of network traffic using, among
# other techniques, carefully crafted assembly instructions.  As such it
# needs extensive work to port it to other architectures.
ExclusiveArch: x86_64 aarch64 ppc64le

%define sdkdir  %{_datadir}/%{name}
%define docdir  %{_docdir}/%{name}
%define incdir  %{_includedir}/%{name}
%define pmddir  %{_libdir}/%{name}-pmds

%define venvdir %{_builddir}/venv

%if 0%{?rhel} > 7 || 0%{?fedora}
%define _py python3
%define _py_exec %{?__python3}
%else
%define _py python
%define _py_exec %{?__python2}
%endif

%if 0%{?rhel} > 7
# Fix conflicts with README and MAINTAINERS (included in dpdk-doc < 18.11-2)
Conflicts: dpdk-doc < 18.11-2
%endif

BuildRequires: gcc, kernel-headers, zlib-devel, numactl-devel
BuildRequires: doxygen, %{_py}-devel, %{_py}-sphinx
BuildRequires: python3-devel
%ifarch x86_64
BuildRequires: rdma-core-devel >= 15
%endif

# Macros taked from ninja-build and meson packages and adapted to be defined here
# See /usr/lib/rpm/macros.d/macros.{ninja,meson}
%if 0%{?rhel} && 0%{?rhel} < 8

# RHEL-7 doesn't define _vpath_* macros yet
%if 0%{!?_vpath_srcdir:1}
%define _vpath_srcdir .
%endif
%if 0%{!?_vpath_builddir:1}
%define _vpath_builddir %_target_platform
%endif

%define __ninja %{venvdir}/bin/ninja
%define __ninja_common_opts -v %{?_smp_mflags}

%define ninja_build \
    %{__ninja} %{__ninja_common_opts}

%define ninja_install \
    DESTDIR=%{buildroot} %{__ninja} install %{__ninja_common_opts}

%define ninja_test \
    %{__ninja} test %{__ninja_common_opts}

%define __meson %{venvdir}/bin/meson
%define __meson_wrap_mode nodownload
%define __meson_auto_features enabled

%define meson \
    export CFLAGS="${CFLAGS:-%__global_cflags}"       \
    export CXXFLAGS="${CXXFLAGS:-%__global_cxxflags}" \
    export FFLAGS="${FFLAGS:-%__global_fflags}"       \
    export FCFLAGS="${FCFLAGS:-%__global_fcflags}"    \
    export LDFLAGS="${LDFLAGS:-%__global_ldflags}"    \
    %{__meson}                                    \\\
        --buildtype=plain                         \\\
        --prefix=%{_prefix}                       \\\
        --libdir=%{_libdir}                       \\\
        --libexecdir=%{_libexecdir}               \\\
        --bindir=%{_bindir}                       \\\
        --sbindir=%{_sbindir}                     \\\
        --includedir=%{_includedir}               \\\
        --datadir=%{_datadir}                     \\\
        --mandir=%{_mandir}                       \\\
        --infodir=%{_infodir}                     \\\
        --localedir=%{_datadir}/locale            \\\
        --sysconfdir=%{_sysconfdir}               \\\
        --localstatedir=%{_localstatedir}         \\\
        --sharedstatedir=%{_sharedstatedir}       \\\
        --wrap-mode=%{__meson_wrap_mode}          \\\
        --auto-features=%{__meson_auto_features}  \\\
        %{_vpath_srcdir} %{_vpath_builddir}       \\\
        %{nil}

%define meson_build \
    %ninja_build -C %{_vpath_builddir}

%define meson_install \
    %ninja_install -C %{_vpath_builddir}

%define meson_test \
    %ninja_test -C %{_vpath_builddir}

%endif

%description
The Data Plane Development Kit is a set of libraries and drivers for
fast packet processing in the user space.

%package devel
Summary: Data Plane Development Kit development files
Requires: %{name}%{?_isa} = %{version}-%{release}
%ifarch x86_64
Requires: rdma-core-devel
%endif

%description devel
This package contains the headers and other files needed for developing
applications with the Data Plane Development Kit.

%package doc
Summary: Data Plane Development Kit API documentation
BuildArch: noarch

%description doc
API programming documentation for the Data Plane Development Kit.

%if %{with tools}
%package tools
Summary: Tools for setting up Data Plane Development Kit environment
Requires: %{name} = %{version}-%{release}
Requires: kmod pciutils findutils iproute %{_py_exec}

%description tools
%{summary}
%endif

%if %{with examples}
%package examples
Summary: Data Plane Development Kit example applications
BuildRequires: libvirt-devel

%description examples
Example applications utilizing the Data Plane Development Kit, such
as L2 and L3 forwarding.
%endif

%prep
%if 0%{?rhel} && 0%{?rhel} < 8
%setup -q -a 1 -a 2 -n %{srcname}-%{?commit0:%{commit0}}%{!?commit0:%{ver}}
%else
%setup -q -n %{srcname}-%{?commit0:%{commit0}}%{!?commit0:%{ver}}
%endif
%autopatch -p1

%build
%if 0%{?rhel} && 0%{?rhel} < 8
%{__python3} -m venv --clear %{venvdir}
pushd ninja-%{ninjaver}
%{venvdir}/bin/python configure.py --bootstrap --with-python %{venvdir}/bin/python
mv ninja %{venvdir}/bin
popd

pushd meson-%{mesonver}
%{venvdir}/bin/python setup.py install
popd

export PATH="%{venvdir}/bin:$PATH"
%endif

ENABLED_DRIVERS=(
    bus/pci
    bus/vdev
    mempool/ring
    net/failsafe
    net/i40e
    net/ring
    net/vhost
    net/virtio
    net/tap
)

%ifarch x86_64
ENABLED_DRIVERS+=(
    bus/vmbus
    common/iavf
    common/mlx5
    net/bnxt
    net/enic
    net/iavf
    net/ice
    net/mlx4
    net/mlx5
    net/netvsc
    net/nfp
    net/qede
    net/vdev_netvsc
)
%endif

%ifarch aarch64 x86_64
ENABLED_DRIVERS+=(
    net/e1000
    net/ixgbe
)
%endif

# Since upstream doesn't have a way
for driver in drivers/*/*/; do
    driver=${driver#drivers/}
    driver=${driver%/}
    [[ " ${ENABLED_DRIVERS[@]} " == *" $driver "* ]] || \
        disable_drivers="${disable_drivers:+$disable_drivers,}"$driver
done

%meson --includedir=include/dpdk \
       --default-library=shared \
       -Ddisable_drivers="$disable_drivers" \
       -Ddrivers_install_subdir=dpdk-pmds \
       -Denable_docs=true \
       -Dmachine=default \
       -Dmax_ethports=32 \
       -Dmax_numa_nodes=8 \
       -Dtests=false
%meson_build

%install
%if 0%{?rhel} && 0%{?rhel} < 8
export PATH="%{venvdir}/bin:$PATH"
%endif

%meson_install

# FIXME this file doesn't have chmod +x upstream
chmod +x %{buildroot}%{sdkdir}/examples/pipeline/examples/vxlan_table.py

rm -f %{buildroot}%{_bindir}/dpdk-pdump
rm -f %{buildroot}%{_bindir}/dpdk-proc-info
rm -f %{buildroot}%{_bindir}/dpdk-test{,-acl,-bbdev,-cmdline,-compress-perf,-crypto-perf,-eventdev,-pipeline,-sad,-fib,-flow-perf,-regex}
rm -f %{buildroot}%{_libdir}/*.a

%files
# BSD
%doc README MAINTAINERS
%{_bindir}/dpdk-testpmd
%dir %{pmddir}
%{_libdir}/*.so.*
%{pmddir}/*.so.*

%files doc
#BSD
%exclude %{docdir}/README
%exclude %{docdir}/MAINTAINERS
%{docdir}

%files devel
#BSD
%{incdir}/
%{sdkdir}/
%if %{with tools}
%exclude %{_bindir}/dpdk-*.py
%endif
%if %{with examples}
%exclude %{sdkdir}/examples/
%endif
%{_libdir}/*.so
%{pmddir}/*.so
%{_libdir}/pkgconfig/libdpdk.pc
%{_libdir}/pkgconfig/libdpdk-libs.pc
%if %{with examples}
%files examples
%{_bindir}/dpdk-*
%doc %{sdkdir}/examples/
%endif

%if %{with tools}
%files tools
%{_bindir}/dpdk-*.py
%endif

%changelog
* Tue Feb 16 2021 Timothy Redaelli <tredaelli@redhat.com> - 20.11-3
- Fix gating since on DPDK 20.11 testpmd is called dpdk-testpmd

* Wed Feb 10 2021 Timothy Redaelli <tredaelli@redhat.com> - 20.11-2
- Enable ice PMD for x86_64 (#1927179)

* Tue Dec 01 2020 Timothy Redaelli <tredaelli@redhat.com> - 20.11-1
- Rebase DPDK to 20.11 using meson build system (#1908446)

* Thu Aug 13 2020 Timothy Redaelli <tredaelli@redhat.com> - 19.11.3-1
- Rebase DPDK to 19.11.3 (#1868708)

* Wed May 20 2020 Timothy Redaelli <tredaelli@redhat.com> - 19.11.2-1
- Rebase DPDK to 19.11.2 (#1836830, #1837024, #1837030, #1837022)

* Fri Apr 17 2020 Timothy Redaelli <tredaelli@redhat.com> - 19.11.1-1
- Rebase DPDK to 19.11.1 (#1824905)
- Remove dpdk-pmdinfo.py (#1801361)
- Add Requires: rdma-core-devel libmnl-devel on x86_64 for dpdk-devel (#1813252)

* Thu Feb 20 2020 Timothy Redaelli <tredaelli@redhat.com> - 19.11-4
- Remove MLX{4,5} glue libraries since RHEL 8 ships the correct libibverbs
  library. (#1805140)

* Mon Feb 17 2020 Timothy Redaelli <tredaelli@redhat.com> - 19.11-3
- Remove /usr/share/dpdk/mk/exec-env/{bsd,linux}app symlinks (#1773889)

* Thu Feb 13 2020 Timothy Redaelli <tredaelli@redhat.com> - 19.11-2
- Add pretrans to handle /usr/share/dpdk/mk/exec-env/{bsd,linux}app (#1773889)

* Thu Nov 28 2019 David Marchand <david.marchand@redhat.com> - 19.11-1
- Rebase to 19.11 (#1773889)
- Remove dpdk-pdump (#1779229)

* Mon Nov 04 2019 Timothy Redaelli <tredaelli@redhat.com> - 18.11.2-4
- Pass the correct LDFLAGS to host apps (dpdk-pmdinfogen) too (#1755538)

* Mon Sep 16 2019 Jens Freimann <jfreimann@redhat.com> - 18.11.2-3
- Add fix for wrong pointer calculation to fix Covscan issue
- https://cov01.lab.eng.brq.redhat.com/covscanhub/task/135452/log/added.html

* Wed Aug 14 2019 Jens Freimann <jfreimann@redhat.com> - 18.11.2-2
- Backport "net/virtio: allocate vrings on device NUMA node" (#1700373)

* Thu Jun 27 2019 Timothy Redaelli <tredaelli@redhat.com> - 18.11.2-1
- Updated to DPDK 18.11.2 (#1713704)

* Fri May 24 2019 Maxime Coquelin <maxime.coquelin@redhat.com> - 18.11.8
- Backport "net/virtio: allocate vrings on device NUMA node" (#1525039)

* Thu May 23 2019 Timothy Redaelli <tredaelli@redhat.com> - 18.11-7
- Really use the security cflags (copied from Fedora RPM) (#1703985)

* Fri May 17 2019 Maxime Coquelin <maxime.coquelin@redhat.com> - 18.11-6
- Fix basic CI gating test (#1682308)
- Add manual gating test (#1682308)

* Tue Mar 26 2019 Maxime Coquelin <maxime.coquelin@redhat.com> - 18.11-5
- Add basic CI gating test (#1682308)

* Mon Feb 18 2019 Jens Freimann <jfreiman@redhat.com> - 18.11-4
- Set correct offload flags for virtio and allow jumbo frames (#1676646)

* Mon Feb 18 2019 Maxime Coquelin <maxime.coquelin@redhat.com> - 18.11.3
- Backport NETVSC pmd fixes (#1676534)

* Tue Nov 27 2018 Timothy Redaelli <tredaelli@redhat.com> - 18.11-2
- Remove meson.build from dpdk-tools
- Don't install README and MAINTAINERS in dpdk-doc

* Tue Nov 27 2018 Timothy Redaelli <tredaelli@redhat.com> - 18.11-1
- Updated to DPDK 18.11 (#1492326):
  - Updated configs
  - Added libmnl-devel BuildRequires for Mellanox

* Thu Sep 20 2018 Tomas Orsava <torsava@redhat.com> - 17.11-14
- Require the Python interpreter directly instead of using the package name
- Related: rhbz#1619153

* Mon Sep 10 2018 Timothy Redaelli <tredaelli@redhat.com> - 17.11-13
- Backport "net/mlx{4,5}: Avoid stripping the glue library" (#1609659)

* Fri Jul 20 2018 Timothy Redaelli <tredaelli@redhat.com> - 17.11-12
- Use python3 packages on RHEL8 and Fedora
- Remove dpdk-pmdinfo (#1494462)
- Backport "net/mlx5: fix build with rdma-core v19"

* Thu Jun 14 2018 Timothy Redaelli <tredaelli@redhat.com> - 17.11-11
- Re-align with DPDK patches inside OVS FDP 18.06 (#1591198)

* Mon Jun 11 2018 Aaron Conole <aconole@redhat.com> - 17.11-10
- Fix mlx5 memory region boundary checks (#1581230)

* Thu Jun 07 2018 Timothy Redaelli <tredaelli@redhat.com> - 17.11-9
- Add 2 missing QEDE patches
- Fix previous changelog date

* Thu Jun 07 2018 Timothy Redaelli <tredaelli@redhat.com> - 17.11-8
- Align with DPDK patches inside OVS FDP 18.06
- Enable BNXT, MLX4, MLX5, NFP and QEDE PMDs
- Backport "net/mlx: fix rdma-core glue path with EAL plugins" (only needed on
  DPDK package)

* Wed Jan 31 2018 Kevin Traynor <ktraynor@redhat.com> - 17.11-7
- Backport to forbid IOVA mode if IOMMU address width too small (#1530957)

* Wed Jan 31 2018 Aaron Conole <aconole@redhat.com> - 17.11-6
- Backport to protect active vhost_user rings (#1525446)

* Tue Jan 09 2018 Timothy Redaelli <tredaelli@redhat.com> - 17.11-5
- Real backport of "net/virtio: fix vector Rx break caused by rxq flushing"

* Thu Dec 14 2017 Timothy Redaelli <tredaelli@redhat.com> - 17.11-4
- Backport "net/virtio: fix vector Rx break caused by rxq flushing"

* Wed Dec 06 2017 Timothy Redaelli <tredaelli@redhat.com> - 17.11-3
- Enable ENIC only for x86_64

* Wed Dec 06 2017 Timothy Redaelli <tredaelli@redhat.com> - 17.11-2
- Re-add main package dependency from dpdk-tools
- Add explicit python dependency to dpdk-tools

* Tue Nov 28 2017 Timothy Redaelli <tredaelli@redhat.com> - 17.11-1
- Update to DPDK 17.11 (#1522700)
- Use a static configuration file
- Remove i686 from ExclusiveArch since it's not supported on RHEL7
- Remove "--without shared" support

* Fri Oct 13 2017 Josh Boyer <jwboyer@redhat.com> - 16.11.2-6
- Rebuild to pick up all arches

* Fri Oct 13 2017 Timothy Redaelli <tredaelli@redhat.com> - 16.11.2-5
- Enable only supported PMDs (#1497384)

* Fri Jun 23 2017 John W. Linville <linville@redhat.com> - 16.11.2-4
- Backport "eal/ppc: fix mmap for memory initialization"

* Fri Jun 09 2017 John W. Linville <linville@redhat.com> - 16.11.2-3
- Enable i40e driver in PowerPC along with its altivec intrinsic support
- Add PCI probing support for vfio-pci devices in Power8

* Thu Jun 08 2017 John W. Linville <linville@redhat.com> - 16.11.2-2
- Enable aarch64, ppc64le (#1428587)

* Thu Jun 08 2017 Timothy Redaelli <tredaelli@redhat.com> - 16.11.2-1
- Import from fdProd
- Update to 16.11.2 (#1459333)

* Wed Mar 22 2017 Timothy Redaelli <tredaelli@redhat.com> - 16.11-4
- Avoid infinite loop while linking with libdpdk.so (#1434907)

* Thu Feb 02 2017 Timothy Redaelli <tredaelli@redhat.com> - 16.11-3
- Make driverctl a different package

* Thu Dec 08 2016 Kevin Traynor <ktraynor@redhat.com> - 16.11-2
- Update to DPDK 16.11 (#1335865)

* Wed Oct 05 2016 Panu Matilainen <pmatilai@redhat.com> - 16.07-1
- Update to DPDK 16.07 (#1383195)
- Disable unstable bnx2x driver (#1330589)
- Enable librte_vhost NUMA support again (#1279525)
- Enable librte_cryptodev, its no longer considered experimental
- Change example prefix to dpdk- for consistency with other utilities
- Update driverctl to 0.89

* Thu Jul 21 2016 Flavio Leitner <fbl@redhat.com> - 16.04-4
- Updated to DPDK 16.04

* Wed Mar 16 2016 Panu Matilainen <pmatilai@redhat.com> - 2.2.0-3
- Disable librte_vhost NUMA support for now, it causes segfaults

* Wed Jan 27 2016 Panu Matilainen <pmatilai@redhat.com> - 2.2.0-2
- Use a different quoting method to avoid messing up vim syntax highlighting
- A string is expected as CONFIG_RTE_MACHINE value, quote it too
- Enable librte_vhost NUMA-awareness

* Tue Jan 12 2016 Panu Matilainen <pmatilai@redhat.com> - 2.2.0-1
- Update DPDK to 2.2.0 final
- Add README and MAINTAINERS docs
- Adopt new upstream standard installation layout, including
  dpdk_nic_bind.py renamed to dpdk_nic_bind
- Move the unversioned pmd symlinks from libdir -devel
- Establish a driver directory for automatic driver loading
- Disable CONFIG_RTE_SCHED_VECTOR, it conflicts with CONFIG_RTE_MACHINE default
- Disable experimental cryptodev library
- More complete dtneeded patch
- Make option matching stricter in spec setconf
- Update driverctl to 0.59

* Wed Dec 09 2015 Panu Matilainen <pmatilai@redhat.com> - 2.1.0-5
- Fix artifacts from driverctl having different version
- Update driverctl to 0.58

* Fri Nov 13 2015 Panu Matilainen <pmatilai@redhat.com> - 2.1.0-4
- Add driverctl sub-package

* Fri Oct 23 2015 Panu Matilainen <pmatilai@redhat.com> - 2.1.0-3
- Enable bnx2x pmd, which buildrequires zlib-devel

* Mon Sep 28 2015 Panu Matilainen <pmatilai@redhat.com> - 2.1.0-2
- Make lib and include available both ways in the SDK paths

* Thu Sep 24 2015 Panu Matilainen <pmatilai@redhat.com> - 2.1.0-1
- Update to dpdk 2.1.0 final
  - Disable ABI_NEXT
  - Rebase patches as necessary
  - Fix build of ip_pipeline example
  - Drop no longer needed -Wno-error=array-bounds
  - Rename libintel_dpdk to libdpdk

* Tue Aug 11 2015 Panu Matilainen <pmatilai@redhat.com> - 2.0.0-9
- Drop main package dependency from dpdk-tools

* Wed May 20 2015 Panu Matilainen <pmatilai@redhat.com> - 2.0.0-8
- Drop eventfd-link patch, its only needed for vhost-cuse

* Tue May 19 2015 Panu Matilainen <pmatilai@redhat.com> - 2.0.0-7
- Drop pointless build conditional, the linker script is here to stay
- Drop vhost-cuse build conditional, vhost-user is here to stay
- Cleanup comments a bit
- Enable parallel build again
- Dont build examples by default

* Thu Apr 30 2015 Panu Matilainen <pmatilai@redhat.com> - 2.0.0-6
- Fix potential hang and thread issues with VFIO eventfd

* Fri Apr 24 2015 Panu Matilainen <pmatilai@redhat.com> - 2.0.0-5
- Fix a potential hang due to missed interrupt in vhost library

* Tue Apr 21 2015 Panu Matilainen <pmatilai@redhat.com> - 2.0.0-4
- Drop unused pre-2.0 era patches
- Handle vhost-user/cuse selection automatically based on the copr repo name

* Fri Apr 17 2015 Panu Matilainen <pmatilai@redhat.com> - 2.0.0-3
- Dont depend on fuse when built for vhost-user support
- Drop version from testpmd binary, we wont be parallel-installing that

* Thu Apr 09 2015 Panu Matilainen <pmatilai@redhat.com> - 2.0.0-2
- Remove the broken kmod stuff
- Add a new dkms-based eventfd_link subpackage if vhost-cuse is enabled

* Tue Apr 07 2015 Panu Matilainen <pmatilai@redhat.com> - 2.0.0-1
- Update to 2.0 final (http://dpdk.org/doc/guides-2.0/rel_notes/index.html)

* Thu Apr 02 2015 Panu Matilainen <pmatilai@redhat.com> - 2.0.0-0.2086.git263333bb.2
- Switch (back) to vhost-user, thus disabling vhost-cuse support
- Build requires fuse-devel for now even when fuse is unused

* Mon Mar 30 2015 Panu Matilainen <pmatilai@redhat.com> - 2.0.0-0.2049.git2f95a470.1
- New snapshot
- Add spec option for enabling vhost-user instead of vhost-cuse
- Build requires fuse-devel only with vhost-cuse
- Add virtual provide for vhost user/cuse tracking

* Fri Mar 27 2015 Panu Matilainen <pmatilai@redhat.com> - 2.0.0-0.2038.git91a8743e.3
- Disable vhost-user for now to get vhost-cuse support, argh.

* Fri Mar 27 2015 Panu Matilainen <pmatilai@redhat.com> - 2.0.0-0.2038.git91a8743e.2
- Add a bunch of missing dependencies to -tools

* Thu Mar 26 2015 Panu Matilainen <pmatilai@redhat.com> - 2.0.0-0.2038.git91a8743e.1
- Another day, another snapshot
- Disable IVSHMEM support for now

* Fri Mar 20 2015 Panu Matilainen <pmatilai@redhat.com> - 2.0.0-0.2022.gitfe4810a0.2
- Dont fail build for array bounds warnings for now, gcc 5 is emitting a bunch

* Fri Mar 20 2015 Panu Matilainen <pmatilai@redhat.com> - 2.0.0-0.2022.gitfe4810a0.1
- Another day, another snapshot
- Avoid building pdf docs

* Tue Mar 03 2015 Panu Matilainen <pmatilai@redhat.com> - 2.0.0-0.1916.gita001589e.2
- Add missing dependency to tools -subpackage

* Tue Mar 03 2015 Panu Matilainen <pmatilai@redhat.com> - 2.0.0-0.1916.gita001589e.1
- New snapshot
- Work around #1198009

* Mon Mar 02 2015 Panu Matilainen <pmatilai@redhat.com> - 2.0.0-0.1911.gitffc468ff.2
- Optionally package tools too, some binding script is needed for many setups

* Mon Mar 02 2015 Panu Matilainen <pmatilai@redhat.com> - 2.0.0-0.1911.gitffc468ff.1
- New snapshot
- Disable kernel module build by default
- Add patch to fix missing defines/includes for external applications

* Fri Feb 27 2015 Panu Matilainen <pmatilai@redhat.com> - 2.0.0-0.1906.git00c68563.1
- New snapshot
- Remove bogus devname module alias from eventfd-link module
- Whack evenfd-link to honor RTE_KERNELDIR too

* Thu Feb 26 2015 Panu Matilainen <pmatilai@redhat.com> - 2.0.0-0.1903.gitb67578cc.3
- Add spec option to build kernel modules too
- Build eventfd-link module too if kernel modules enabled

* Thu Feb 26 2015 Panu Matilainen <pmatilai@redhat.com> - 2.0.0-0.1903.gitb67578cc.2
- Move config changes from spec after "make config" to simplify things
- Move config changes from dpdk-config patch to the spec

* Thu Feb 19 2015 Panu Matilainen <pmatilai@redhat.com> - 2.0.0-0.1717.gitd3aa5274.2
- Fix warnings tripping up build with gcc 5, remove -Wno-error

* Wed Feb 18 2015 Panu Matilainen <pmatilai@redhat.com> - 2.0.0-0.1698.gitc07691ae.1
- Move the unversioned .so links for plugins into main package
- New snapshot

* Wed Feb 18 2015 Panu Matilainen <pmatilai@redhat.com> - 2.0.0-0.1695.gitc2ce3924.3
- Fix missing symbol export for rte_eal_iopl_init()
- Only mention libs once in the linker script

* Wed Feb 18 2015 Panu Matilainen <pmatilai@redhat.com> - 2.0.0-0.1695.gitc2ce3924.2
- Fix gcc version logic to work with 5.0 too

* Wed Feb 18 2015 Panu Matilainen <pmatilai@redhat.com> - 2.0.0-0.1695.gitc2ce3924.1
- Add spec magic to easily switch between stable and snapshot versions
- Add tarball snapshot script for reference
- Update to pre-2.0 git snapshot

* Thu Feb 12 2015 Panu Matilainen <pmatilai@redhat.com> - 1.8.0-15
- Disable -Werror, this is not useful behavior for released versions

* Wed Feb 11 2015 Panu Matilainen <pmatilai@redhat.com> - 1.8.0-14
- Fix typo causing librte_vhost missing DT_NEEDED on fuse

* Wed Feb 11 2015 Panu Matilainen <pmatilai@redhat.com> - 1.8.0-13
- Fix vhost library linkage
- Add spec option to build example applications, enable by default

* Fri Feb 06 2015 Panu Matilainen <pmatilai@redhat.com> - 1.8.0-12
- Enable librte_acl build
- Enable librte_ivshmem build

* Thu Feb 05 2015 Panu Matilainen <pmatilai@redhat.com> - 1.8.0-11
- Drop the private libdir, not needed with versioned libs

* Thu Feb 05 2015 Panu Matilainen <pmatilai@redhat.com> - 1.8.0-10
- Drop symbol versioning patches, always do library version for shared
- Add comment on the combined library thing

* Wed Feb 04 2015 Panu Matilainen <pmatilai@redhat.com> - 1.8.0-9
- Add missing symbol version to librte_cmdline

* Tue Feb 03 2015 Panu Matilainen <pmatilai@redhat.com> - 1.8.0-8
- Set soname of the shared libraries
- Fixup typo in ld path config file name

* Tue Feb 03 2015 Panu Matilainen <pmatilai@redhat.com> - 1.8.0-7
- Add library versioning patches as another build option, enable by default

* Tue Feb 03 2015 Panu Matilainen <pmatilai@redhat.com> - 1.8.0-6
- Add our libraries to ld path & run ldconfig when using shared libs

* Fri Jan 30 2015 Panu Matilainen <pmatilai@redhat.com> - 1.8.0-5
- Add DT_NEEDED for external dependencies (pcap, fuse, dl, pthread)
- Enable combined library creation, needed for OVS
- Enable shared library creation, needed for sanity

* Thu Jan 29 2015 Panu Matilainen <pmatilai@redhat.com> - 1.8.0-4
- Include scripts directory in the "sdk" too

* Thu Jan 29 2015 Panu Matilainen <pmatilai@redhat.com> - 1.8.0-3
- Fix -Wformat clash preventing i40e driver build, enable it
- Fix -Wall clash preventing enic driver build, enable it

* Thu Jan 29 2015 Panu Matilainen <pmatilai@redhat.com> - 1.8.0-2
- Enable librte_vhost, which buildrequires fuse-devel
- Enable physical NIC drivers that build (e1000, ixgbe) for VFIO use

* Thu Jan 29 2015 Panu Matilainen <pmatilai@redhat.com> - 1.8.0-1
- Update to 1.8.0

* Wed Jan 28 2015 Panu Matilainen <pmatilai@redhat.com> - 1.7.0-8
- Always build with -fPIC

* Wed Jan 28 2015 Panu Matilainen <pmatilai@redhat.com> - 1.7.0-7
- Policy compliance: move static libraries to -devel, provide dpdk-static
- Add a spec option to build as shared libraries

* Wed Jan 28 2015 Panu Matilainen <pmatilai@redhat.com> - 1.7.0-6
- Avoid variable expansion in the spec here-documents during build
- Drop now unnecessary debug flags patch
- Add a spec option to build a combined library

* Tue Jan 27 2015 Panu Matilainen <pmatilai@redhat.com> - 1.7.0-5
- Avoid unnecessary use of %%global, lazy expansion is normally better
- Drop unused destdir macro while at it
- Arrange for RTE_SDK environment + directory layout expected by DPDK apps
- Drop config from main package, it shouldn't be needed at runtime

* Tue Jan 27 2015 Panu Matilainen <pmatilai@redhat.com> - 1.7.0-4
- Copy the headers instead of broken symlinks into -devel package
- Force sane mode on the headers
- Avoid unnecessary %%exclude by not copying unpackaged content to buildroot
- Clean up summaries and descriptions
- Drop unnecessary kernel-devel BR, we are not building kernel modules

* Sat Aug 16 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.7.0-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_22_Mass_Rebuild

* Thu Jul 17 2014 - John W. Linville <linville@redhat.com> - 1.7.0-2
- Use EXTRA_CFLAGS to include standard Fedora compiler flags in build
- Set CONFIG_RTE_MACHINE=default to build for least-common-denominator machines
- Turn-off build of librte_acl, since it does not build on default machines
- Turn-off build of physical device PMDs that require kernel support
- Clean-up the install rules to match current packaging
- Correct changelog versions 1.0.7 -> 1.7.0
- Remove ix86 from ExclusiveArch -- it does not build with above changes

* Thu Jul 10 2014 - Neil Horman <nhorman@tuxdriver.com> - 1.7.0-1.0
- Update source to official 1.7.0 release

* Thu Jul 03 2014 - Neil Horman <nhorman@tuxdriver.com>
- Fixing up release numbering

* Tue Jul 01 2014 - Neil Horman <nhorman@tuxdriver.com> - 1.7.0-0.9.1.20140603git5ebbb1728
- Fixed some build errors (empty debuginfo, bad 32 bit build)

* Wed Jun 11 2014 - Neil Horman <nhorman@tuxdriver.com> - 1.7.0-0.9.20140603git5ebbb1728
- Fix another build dependency

* Mon Jun 09 2014 - Neil Horman <nhorman@tuxdriver.com> - 1.7.0-0.8.20140603git5ebbb1728
- Fixed doc arch versioning issue

* Mon Jun 09 2014 - Neil Horman <nhorman@tuxdriver.com> - 1.7.0-0.7.20140603git5ebbb1728
- Added verbose output to build

* Tue May 13 2014 - Neil Horman <nhorman@tuxdriver.com> - 1.7.0-0.6.20140603git5ebbb1728
- Initial Build

