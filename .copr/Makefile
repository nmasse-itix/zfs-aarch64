srpm:
	@mkdir -p $(outdir)
	ls -l $(spec)
	pwd
	ls -l $(outdir)
	rpm -qa
	/bin/bash -xEeuo pipefail -c 'rootdir="$$(basename $(spec))"; ln -s $(outdir) $$rootdir/SRPMS; rpmbuild --define "_topdir $(outdir)" -bs $(spec)'
