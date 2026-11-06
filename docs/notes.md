# Technical Notes

> Draft - will be finalized at the end of the assignment.

## Biggest Docker Problem and How I Solved It

_To be completed after building and running the container._

## Most Important Git/GitHub Lesson

_To be completed after publishing the repository._

---

## Development Log (problems met during setup)

| # | Problem | Cause | Fix |
|---|---------|-------|-----|
| 1 | `wsl --install` failed with `Wsl/InstallDistro/ERROR_ALREADY_EXISTS` | WSL and an Ubuntu distro were already installed | Checked with `wsl -l -v` that Ubuntu runs on WSL version 2, then installed Docker Desktop on the WSL 2 backend |
| 2 | `docker run hello-world0` failed: `pull access denied ... repository does not exist` | Typo in the image name, so Docker searched Docker Hub for a non-existent image | Ran `docker run hello-world` with the exact image name - Docker printed "Hello from Docker!" |
| 3 | Column `quantity` was detected as `float64` instead of `int64` | pandas stores missing values as `NaN` (a float), so the whole column becomes float | Expected behaviour - documented so the API output is not misread |
| 4 | `docker build` failed: `failed to connect to the docker API at npipe:////./pipe/dockerDesktopLinuxEngine` | Docker Desktop was closed, so the Docker daemon (engine) was not running - the `docker` CLI is only a client | Opened Docker Desktop, waited for "Engine running", then re-ran the build |
| 5 | First `docker build` took ~20 minutes | Slow network: pulling `python:3.13-slim` (~743s) and `pip install` (~398s) | Expected for the first build only - `requirements.txt` is copied and installed before the source code, so later builds reuse the cached dependency layer |
