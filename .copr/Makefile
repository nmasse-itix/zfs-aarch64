srpm:
	@mkdir -p $(outdir)
	dnf install -y git-lfs
	git lfs install
	git lfs pull
	git lfs ls-files
	git lfs status
	/bin/bash -xEeuo pipefail -c 'rootdir="$$(dirname $(spec))/../"; ln -s $(outdir) $$rootdir/SRPMS; rpmbuild --define "_topdir $$rootdir" -bs $(spec)'
