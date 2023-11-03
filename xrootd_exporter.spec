%define         __spec_install_post %{nil}
%define         debug_package %{nil}

Name:           xrootd_exporter
Version:        1.0.0
Release:        1%{?dist}
Summary:        A prometheus exporter that queries xrootd/mpx usage statistics and makes them available.
Group:          XRootD/Plugins

License:        LGPLv3
URL:            https://github.com/GSI-HPC/xrootd_exporter
Source0:        %{name}-%{version}.tar.gz

Requires(pre):  xrootd-server
Requires:       python36
Requires:       python3-prometheus_client


%description
A service that queries xrootd statistics that are exposed via mpx
Contains the python service and a systemd unit file/

%prep
%setup -q

%install
rm -rf %{buildroot}/src/
mkdir -p %{buildroot}%{_bindir}
cp -av /root/xrootd_exporter.py %{buildroot}%{_bindir}/
mkdir -p %{buildroot}/usr/lib/systemd/system/
cp -av /root/xrootd_exporter@.service %{buildroot}/usr/lib/systemd/system/
mkdir -p %{buildroot}%{_sysconfdir}/xrootd
cp -av /root/descriptions.cfg %{buildroot}%{_sysconfdir}/xrootd/

mkdir -p ${buildroot}/etc/xrootd/
%files
%attr(755,root,root)/usr/bin/xrootd_exporter.py
%attr(644,root,root)/usr/lib/systemd/system/xrootd_exporter@.service
%attr(644,root,root)/etc/xrootd/descriptions.cfg

%doc

