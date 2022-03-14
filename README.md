# rucio-tools
Tools around or integrating with Rucio

## Status

These tools currently hardcode some settings, but are in general usable to check usage and quotas or adjust quotas in an automated way.

Most of them require a valid VOMS proxy certificate and correct environment setup (including a working version of Rucio).

## Description

### `setup-rucio`, `rucio_homes`
Function which can be used in your shell environment to get a VOMS proxy certificate and set up the `X509_USER_PROXY` environment variable correctly.
It also sets up the Rucio home correctly, currently for the VOs ATLAS and BELLE.
A `rucio_homes` directory is part of this repository with the configurations for these VOs. Note the differing `LICENSE` (see `COPYRIGHT`).

### `get_accs_usage.sh`
Shell script massaging the output from `get_accs_usage.py` to produce output like:
```
name      mail                                      files  size/TB      quota/TB
cernid    max.example@cern.ch                       10652  120.728      170
```
The usage and quota are measured in the same way, i.e. if multiple people order the same datasets, they will all get this accounted to their personal quota (but storage will only have the sata once). This means the sum of the sizes is usually larger than the total storage consumption.

### `pleiades_quick.sh`
Tool to extract the data also shown at on the [Pleiades Monitor](https://localgroupdisk.pleiades.uni-wuppertal.de/). Output like:
```
Accounts           Space total  Space persistent  Space temporary
cernid             69.316       69.316            0.000
cernid,cernid      44.992       24.992            20.000
```
Data ordered by several persons or multiple times by one person is shown with grouped CERN IDs, so this does not match the Rucio quota calculation, but the sum of the sizes should match the total storage consumption.
Note that `persistent` relates to data placed by rules which do not have an expiration set, while `temporary` relates to data placed by rules with expiration. See [this PR](https://github.com/rucio/rucio/issues/4983) for details.

### `pleiades_csv.sh`
Same as `pleiades_quick.sh`, but creates a simple CSV output with the cokumns:
```
Accounts;Space persistent;Space temporary
```
for cunsmption by other tools. Can e.g. be visualized with `pleiades.html`.

### `pleiades.html`
Read a CSV file produced e.g. by `pleiades_csv.sh` and displays it graphically via Javascript.
Can be inspected via GitHub pages [here](https://unibonn.github.io/rucio-tools/pleiades.html).

### `get_and_adjust_quotas.py`
Tool which gets and adjusts quotas. Rules to be documented (basically, it rounds up usage after adding a safety margin, and sets a minimum default quota different for users and admins).

This tool has parameters:
| Parameter | Description                                                                                           |
|-----------|-------------------------------------------------------------------------------------------------------|
| -v        | Verbose mode, strongly recommended.                                                                   |
| --dry-run | Perform a _dry-run_, i.e. only show what would be done. Strongly recommended before applying changes. |

### `check_cloud_users.py`
Simple tool cross-checking whether users not in a cloud have quota on an RSE and users in a cloud are missing quota on an RSE (to cross-check e.g. LOCALGROUPDISK quotas).
