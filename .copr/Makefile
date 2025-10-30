srpm:
	@mkdir -p $(outdir)
	/bin/bash -xEeuo pipefail -c 'rootdir="$$(dirname $(spec))/../"; ln -s $(outdir) $$rootdir/SRPMS; rpmbuild --define "_topdir $$rootdir" -bs $(spec)'
