def get_apt_mirrors_and_script_generating_key_files(conf):
    # extract the distribution repository urls and keys from the build file
    # and pass them as command line arguments and files
    # so that the job must not parse the build file
    apt_mirror_args = []
    script_generating_key_files = []
    if 'apt_mirrors' in conf:
        apt_mirrors = conf['apt_mirrors']
        if apt_mirrors:
            apt_mirror_args.append('--distribution-repository-urls')
            apt_mirror_args += apt_mirrors
    if 'apt_mirror_keys' in conf:
        apt_mirror_keys = conf['apt_mirror_keys']
        if apt_mirror_keys:
            apt_mirror_args.append('--distribution-repository-key-files')
            script_generating_key_files.append("mkdir -p $WORKSPACE/keys")
            script_generating_key_files.append("rm -fr $WORKSPACE/keys/*")
            for i, apt_mirror_key in enumerate(apt_mirror_keys):
                apt_mirror_args.append('$WORKSPACE/keys/%d.key' % i)
                script_generating_key_files.append(
                    'echo "%s" > $WORKSPACE/keys/%d.key' % (apt_mirror_key, i)
                )
    return apt_mirror_args, script_generating_key_files


def get_distribution_repository_keys(urls, key_files):
    # ensure that for each key file a url has been passed
    assert \
        len(urls) >= \
        len(key_files), \
        'More distribution repository keys (%d) passes in then urls (%d)' % \
        (len(key_files),
         len(urls))

    distribution_repositories = []
    for i, url in enumerate(urls):
        key_file = key_files[i] \
            if len(key_files) > i \
            else ''
        distribution_repositories.append((url, key_file))
    print('Using the following distribution repositories:')
    keys = []
    for url, key_file in distribution_repositories:
        print('  %s%s' % (url, ' (%s)' % key_file if key_file else ''))
        with open(key_file, 'r') as h:
            keys.append(h.read())
    return keys


def get_binary_package_versions(apt_cache, debian_pkg_names):
    versions = {}
    for debian_pkg_name in debian_pkg_names:
        pkg = apt_cache[debian_pkg_name]
        versions[debian_pkg_name] = max(pkg.versions).version
    return versions


def get_debian_package_name(rosdistro_name, ros_package_name):
    return 'ros-%s-%s' % (rosdistro_name, ros_package_name.replace('_', '-'))