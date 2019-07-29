# lastversion

[![Build Status](https://travis-ci.org/dvershinin/lastversion.svg?branch=master)](https://travis-ci.org/dvershinin/lastversion)
[![PyPI version](https://badge.fury.io/py/lastversion.svg)](https://badge.fury.io/py/lastversion)

A tiny command line utility that helps to answer one simple question:

> What is the latest released version for a GitHub project?

GitHub has an API endpoint [here](https://developer.github.com/v3/repos/releases/#get-the-latest-release). But if you're here, then you know how it sucks:

A release would show up in this API response *only* if it was filed formally using GitHub release interface.
Sometimes project authors use formal releases, and next thing you know, for next release they won't.
There is no consistency in human beings.

OK, you think you could use another API endpoint to [list tags](https://developer.github.com/v3/repos/#list-tags).
Tags *usually* represent a release, however, you might get something like "latest-stable" for a tag name value.

So in general, quite many project authors do things like:

* Filing a formal release that is clearly a Release Candidate (`rc` in tag), but do not mark it as a pre-release
* Put extraneous text in release tag e.g. 'release-1.2.3' or `name-1.2.3-2019` anything fancy like that
* Put or not put a 'v' prefix to release tags. Today yes, tomorrow not. I'm not consistent about it myself :)

To deal with all this mess and simply get well-formatted, last *stable* version (or download URL!) on the command line, you can use `lastversion`.

Its primary use is for build systems - whenever you want to watch specific repositories for released versions in order to build packages automatically.
Or otherwise require getting latest version in your automation scripts.

[Like I do](https://www.getpagespeed.com/redhat)

`lastversion` does a little bit of AI in order to detect if releasers mistakenly filed beta version as a stable release.
It uses both of the API endpoints and incorporates logic for cleaning up human inconsistency from version information.

## Synopsis

    lastversion apache/incubator-pagespeed-ngx #> 1.13.35.2

### Download latest version of something     

You can also use `lastversion` to get assets/source download URLs for the latest release.

    wget $(lastversion --assets mautic/mautic)

This will download all assets of the newest stable Mautic, which are 2 zip files.

How this works: `lastversion` outputs all asset URLs, each on new line, and `wget` is smart enough to download each URL. Magic :) 

For releases which have no assets added, it will download source archive.  

To always download source, use `--source` instead:

    wget $(lastversion --source mautic/mautic)  



An asset is a downloadable file that typically represents an executable, or otherwise "ready to launch" project. It's what you see filed under formal releases, and is usually a compiled (for specific platform), program.

Source files, are either tarballs or zipballs of sources for the source code of release.    

### Get last version (betas are fine)

We consider latest release is the one which is stable / not marked as beta.
If you think otherwise, then pass `--pre` switch and if the latest version of repository is a pre-release, then you'll get its version instead:

    lastversion --pre mautic/mautic #> 2.15.2b0

## Usage

 Typically, you would just pass the repository URL (or repo owner/name to it) as the only argument, e.g.:

    lastversion https://github.com/gperftools/gperftools

Equivalently accepted invocation with same output is:

    lastversion gperftools/gperftools    

For more options to control output or behavior, see `--help` output:    

 ```
 usage: lastversion [-h] [--pre] [--verbose]
                    [--format {version,assets,source,json}] [--assets]
                    [--version]
                    REPO

 Get latest release from GitHub.

 positional arguments:
   REPO                  GitHub repository in format owner/name

 optional arguments:
   -h, --help            show this help message and exit
   --pre                 Include pre-releases in potential versions
   --verbose
   --format {version,assets,source,json}
                         Output format
   --assets              Returns only download URLs for last release
   --version             show program's version number and exit

```

The `--format` will affect what kind of information from last release and in which format will be displayed, e.g.:

* `version` is the default. Just outputs well format version number
* `assets` will output newline separated list of assets URLs (if any), otherwise link to sources archive
* `source` will output link to source archive, no matter if the release has some assets added
* `json` can be used by external Python modules or for debugging, it is JSON output of an API call that satisfied last version checks

You can use shortcuts `--source` instead of `--format source`, and `--assets` instead of `--format assets`, as in the above examples.

    lastversion --source mautic/mautic #> https://github.com/mautic/mautic/archive/2.15.1/mautic-2.15.1.tar.gz

### Installation for CentOS 7

    yum install https://extras.getpagespeed.com/release-el7-latest.rpm
    yum install lastversion

## Installation for other systems

The script is primarily developed for Python 2.7, but is known to work with recent versions like Python 3.7.
Installing with `pip` is easiest:

    pip install lastversion

## Tips

Note that `lastversion` makes use of caching API response to be fast and light on GitHub API,
It does conditional ETag validation, which, as per GitHub API will not count towards rate limit.
The cache is stored in `~/.cache/lastversion` on Linux systems.

If you're planning to fetch versions for a whole lot of projects, setup your [GitHub API token](https://github.com/settings/tokens) in `~/.bashrc` like this:

    export GITHUB_API_TOKEN=xxxxxxxxxxxxxxx

Then run `source ~/.bashrc`. After this, `lastversion` will use it to get larger API calls allowance from GitHub. Although this is rarely needed, because `lastversion` usually does not resort to API calls because it finds release version through parsing Releases page earlier.

## Usage in a Python module

    from lastversion import lastversion
    repo = "mautic/mautic"
    lastVersion = lastversion.latest(repo, 'version', True)
    print(lastVersion)

Will yield: `2.15.2b0`.

The `lastversion.latest` function accepts 3 arguments

* `repo`, in format of `<owner>/<name>`, or any URL under this repository, e.g. `https://github.com/dvershinin/lastversion/issues`   
* `format`, which accepts same values as when you run `lastversion` interactively
* `preOk`, boolean for whether to include pre-releases as potential versions
