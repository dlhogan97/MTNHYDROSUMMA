# SUMMA and mizuRoute install
SUMMA and mizuRoute are both under active development. This code downloads the latest version of the code base and gives examples of how to compile the Fortran source code of both programs.

Running SUMMA and mizuRoute requires a linux-based environment, because both programs use the `netcdf-fortran` library for which no Windows alternative currently exists.

Requirements:
- linux environment
- fortran compiler (e.g. gcc)
- `netcdf-fortran` library
- `openblas` library 

## Workflow steps

### 1. Install Required Libraries
Before compiling, install required compilers and libraries via apt:

```
    sudo apt update
    sudo apt install build-essential gfortran make \
    libnetcdf-dev libnetcdff-dev libopenblas-dev
```
- `gfortran`: GNU Fortran compiler
- `make`: Needed to build with Makefiles
- `libnetcdf-dev`: NetCDF C library (required for Fortran)
- `libnetcdff-dev`: NetCDF Fortran bindings (provides netcdf.mod)
- `libopenblas-dev`: BLAS library for numerical computations

### 2.
Find netcdf.mod Location
To properly point the compiler to NetCDF Fortran, check where netcdf.mod is installed:

```dpkg -L libnetcdff-dev | grep netcdf.mod```
Typical result:

```/usr/include/x86_64-linux-gnu/fortran/netcdf.mod```

### 3. Update the Build Script
Edit 1b_compile_summa.sh to reflect your local install paths.

Set compiler and flags:

```
    export FC=gfortran
    export FC_EXE='gfortran'
```

Set includes and libraries:

```
    export INCLUDES="-I/usr/include -I/usr/include/x86_64-linux-gnu/fortran"
    export LIBRARIES="-L/usr/lib/x86_64-linux-gnu -lnetcdff -lnetcdf -lopenblas"
```
These ensure that gfortran can find netcdf.mod and link the right libraries.
## Assumptions not specified in `control_active.txt`
This code by default clones the `develop` branch of both repositories, which contains the latest available fixes and updates before they are included in new releases on the respective `master` branches. 
### 4. Clean Prior Builds (Optional but Recommended)
If you’re recompiling after a failed attempt, run:

```
    cd $F_MASTER/build
    make clean
    cd -
```
This removes partial .mod and .o files that can cause further errors.

### 5. Run the Compile Script
Finally, compile SUMMA:

```bash 1b_compile_summa.sh```
If successful, the executable will appear in:

```$F_MASTER/bin/```

## Control file settings
This section lists all the settings in `control_active.txt` that the code in this folder uses.
- **github_summa, github_mizu**: GitHub URLs from which to clone SUMMA and mizuRoute.
- **install_path_summa, install_path_mizu**: install locations for both models.
- **exe_name_summa, exe_name_mizu**: names for compiled executables of both models
