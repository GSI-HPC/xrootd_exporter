FROM rockylinux:8.6
MAINTAINER jknedlik <j.knedlik@gsi.de>

RUN dnf update -y
RUN dnf install -y epel-release
RUN dnf install -y bash git make gcc gcc-c++ rpm-build libtool

COPY xrootd_exporter.py xrootd_exporter@.service descriptions.cfg /root/

RUN mkdir -p /root/rpmbuild
WORKDIR /root/rpmbuild
RUN mkdir -p BUILD SOURCES SPECS RPMS SRPMS xrootd_exporter-1.0.0
RUN tar -cf SOURCES/xrootd_exporter-1.0.0.tar.gz xrootd_exporter-1.0.0
COPY xrootd_exporter.spec /root/rpmbuild/SPECS/
WORKDIR /root
RUN rpmbuild  -bb rpmbuild/SPECS/xrootd_exporter.spec

RUN mkdir /rpm
ENTRYPOINT ["cp","/root/rpmbuild/RPMS/x86_64/xrootd_exporter-1.0.0-1.el8.x86_64.rpm","/rpm"]
