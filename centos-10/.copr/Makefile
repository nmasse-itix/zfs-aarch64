srpm:
	@mkdir -p $(outdir)
	ls -l $(spec)
	pwd
	ls -l $(outdir)
	spectool -g -R $(spec)
	rpmbuild --define "_topdir $(outdir)" -bs $(spec)
