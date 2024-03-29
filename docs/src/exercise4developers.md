### Adding an ALARO+SURFEX test to DAVAÏ

This section describes what was done to add an ALARO+SURFEX test to DAVAÏ. It may serve as a recipe to add other tests.

First, create a new DAVAÏ experiment with `davai-new_xp`. Also, run following commands to set the environment:

```bash
source ~acrd/.vortexrc/profile
cp ~rm9/.vortexrc/uget-client-defaults.ini .vortexrc/
```

Next, initialize the hack directory for your user:

```bash
uget.py bootstrap_hack ${USER}
```

Note: directories in this document are usually relative to the experiment's base directory.

#### Creating the test itself

##### Modifications to the file `conf/davai_nrv.ini`:

* add a section for the model:
  ```ini
  [alaro]
  model               = alaro
  LAM                 = True
  input_shelf         = &{input_shelf_lam}
  fcst_term           = 12
  expertise_term      = 12
  coupling_frequency  = 3
  ```

* add a section for the forecast itself:
  ```ini
  [forecast-alaro1_sfx-chmh2325]
  alaro_version       = 1_sfx
  rundate             = date(2021022000)
  ```

* since we're using a new domain (chmh2325), add a section for this domain:
  ```ini
  [chmh2325]
  geometry            = geometry(chmh2325)
  timestep            = 90
  ```

##### Modifications to the file `tasks/forecasts/standalone_forecasts.py`:

The easiest is to copy and modify an existing forecast. In this case, we added to the following to the `alaro` family:
```python
                    Family(tag='chmh2325', ticket=t, nodes=[
                          StandaloneAlaroForecast(tag='forecast-alaro1_sfx-chmh2325', ticket=t, **kw),
                    , **kw),
```
					   
##### Modifications to the file `tasks/forecasts/standalone/alaro.py`:

We need to add the fetching of the SURFEX initial file, the SURFEX namelist and the PGD file. This was done using the AROME forecast task as an example. The fetching of these files is put under a condition `self.conf.alaro_version == '1_sfx'`, to make sure the files are only fetched when running ALARO with SURFEX.

#### Setup a custom catalogue

Find out which catalogue is used by your test. In the case of ALARO, the file `alaro.py` uses ```self.conf.davaienv```, which is set in `davai_nrv.ini` to be `cy49.davai_specials.02@davai`. A local copy of this catalogue is created with

```
uget.py hack env cy49.davai_specials.02@davai into cy49.davai_specials.02@@${USER}
```

This will create a local catalogue file under `~/.vortexrc/hack/uget/${USER}/env/`. Make sure to modify the value in `davai_nrv.ini` to use your local copy.

#### Adding constant files such as namelist files, PGD file, etc.

Constant files go into the `~/.vortexrc/hack/` directory. To add/modify a namelist file, first find out which namelists are used by your test in the local catalogue file you copied before (`cy49.davai_specials.02@${USER}`). In the case of the ALARO forecast, the namelists that are used are `49.arpifs@davai.02.nam.tgz@davai`, so a local copy is taken of these with

```
uget.py hack data 49.arpifs@davai.02.nam.tgz@davai into 49.arpifs@davai.02.nam.tgz@${USER}
```

This creates a tgz file under `~/.vortexrc/hack/uget/${USER}/data/`, which then needs to be unpacked. Make sure to modify the catalogue file to use your local copy of the namelists.

You then can modify existing namelist files, or - as was the case for the ALARO+SURFEX test - add new namelist files. The location and name of the required namelists can be found in the forecast script (`alaro.py`). The namelists created were `model/alaro/fcst.alaro1_sfx.nam` and `model/alaro/fcst.alaro1_sfx.nam_surfex`. Make sure to use the following variables/values:

```
CNMEXP=__CEXP__,
NPROC=__NBPROC__,
NSTRIN=__NBPROC__,
NSTROUT=__NBPROC__,
CSTOP=__FCSTOP__,
TSTEP=__TIMESTEP__,
```
since these are substituted by DAVAÏ.

The name of the PGD file needs to be set in the catalogue `cy49.davai_specials.02@${USER}` by adding the line

```
PGD_FA_CHMH2325=uget:pgd.chmh2325-02km33.fa.01@${USER}
```

The PGD file itself should be put just under `~/.vortexrc/hack/uget/${USER}/data/`.

#### Setting non-constant files such as initial conditions, LBC files, etc.

These files should go into the shelf (since in mixed tests they could be generated by an earlier task). The name of the shelf can be found in `davai_nrv.ini`, and turns out to be `input_shelf_LAM = shelf_cy48t1_LAM.01@davai`, so we'll create a directory `/scratch/${USER}/mtool/cache/vortex/davai/shelves/shelf_cy48t1_LAM.01@davai/`. Following files are put in this directory:

```
20210220T0000A/surfan/analysis.surf-surfex.chmh2325-02km33.fa
20210220T0000A/coupling/cpl.arpege-4dvarfr-prod.chmh2325-02km33+0003:00.fa
20210220T0000A/coupling/cpl.arpege-4dvarfr-prod.chmh2325-02km33+0009:00.fa
20210220T0000A/coupling/cpl.arpege-4dvarfr-prod.chmh2325-02km33+0000:00.fa
20210220T0000A/coupling/cpl.arpege-4dvarfr-prod.chmh2325-02km33+0006:00.fa
20210220T0000A/coupling/cpl.arpege-4dvarfr-prod.chmh2325-02km33+0012:00.fa
```

To know how to name these files, look at similar data for other experiments, or just your experiment and see where it crashes.

### Defining a new geometry

Since the ALARO+SURFEX test runs on a new domain, this domain should also be registred. This is done in a file `~/.vortexrc/geometries.ini`, following the examples from the file `vortex/conf/geometries.ini`.
