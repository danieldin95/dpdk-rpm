# CentOS8

git clone https://github.com/danieldin95/dpdk-rpm.git

cd dpdk-rpm

yum-builddep --enablerepo=powertools SPECS/dpdk.spec

rpmbuild -D "_topdir $PWD" -ba SPECS/dpdk.spec
