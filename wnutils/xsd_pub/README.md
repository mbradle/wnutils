# Vendored XML schemas

This directory contains the XML schemas required by `wnutils` validation.
They are vendored so normal checkouts, tests, installations, and builds do not
fetch schemas or depend on mutable upstream schema state.

The libnucnet schemas and `catalog` come from
<https://bitbucket.org/mbradle/libnucnet_xsd>.

Upstream commit: `d91368e70a789712de0724167e54d25d7cec3545`

The same revision is recorded in the repository-root `XSD_REVISION` file. The
schema files retain their original GPL-2.0-or-later notices; wnutils distributes
them under those terms alongside its GPL-3.0-or-later code.

`xml.xsd` is an unchanged copy of the W3C XML namespace schema at
<https://www.w3.org/2005/08/xml.xsd>. It is distributed under the W3C Software
and Document License reproduced in `W3C_LICENSE.txt`.

Maintainers update this snapshot with:

```console
tools/update_xsd_pub.sh <full-upstream-commit-sha>
```

The tool checks the expected file set, copies only approved schema files,
updates `XSD_REVISION`, runs the unit suite, builds the package, and verifies
the wheel contents. It leaves the resulting source changes uncommitted for
review.
