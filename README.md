# Vantum

**A lean, fast, custom Linux distribution built on Puppy Linux and Ubuntu Jammy.**

---

## What is Vantum?

Vantum is a custom Linux distribution built from the ground up using [Woof-CE](https://github.com/puppylinux-woof-CE/woof-CE) — the official Puppy Linux build system — targeting Ubuntu Jammy (22.04) as its package source. It inherits everything that makes Puppy Linux great: a tiny footprint, the ability to run entirely from RAM, a lightning-fast boot, and a complete desktop environment that works on modest hardware — while layering on a custom look, feel, and toolset that makes it distinctly its own.

This is not a remaster or a respin. Vantum is compiled from source, assembled package by package, and built with deliberate decisions about what goes in and what stays out.

---

## Why Puppy? Why Jammy?

Puppy Linux has a well-earned reputation for doing more with less. It boots fast, runs in RAM, saves state to a single file, and gets out of your way. Most modern distros have drifted toward bloat; Puppy never did.

Ubuntu Jammy (22.04 LTS) was chosen as the package base because it hits a sweet spot: recent enough to have modern library versions and long-term security support, stable enough that the package ecosystem is well-tested and widely compatible. The result is a Puppy that can install and run most Ubuntu-compatible software without friction.

---

## What makes Vantum different?

- **Custom JWM configuration** — the window manager is tuned with a specific panel layout, keybindings, and theme out of the box
- **Custom GTK appearance** — a cohesive visual identity applied from first boot, not something you configure afterward
- **Custom launcher** — a purpose-built application launcher compiled from source and baked directly into the ISO
- **Stripped-down default app set** — only what's needed, nothing that isn't
- **Reproducible build** — the entire OS can be rebuilt from source on a fresh machine using this repository

---

## Technical overview

| | |
|---|---|
| **Build system** | Woof-CE |
| **Package base** | Ubuntu Jammy 22.04 (x86_64) |
| **Build host** | Ubuntu 26.04 in Multipass (Windows 11) |
| **Base Puppy** | FossaPup64 9.5 |
| **Kernel** | huge-5.4.53-fossapup64 |
| **Window manager** | JWM |
| **Architecture** | x86_64 |

---

## Repository structure

```
woof-CE/
├── woof-code/
│   ├── rootfs-skeleton/        ← Vantum UI customisations (JWM, GTK, themes)
│   ├── rootfs-petbuilds/       ← Custom launcher and other compiled-from-source packages
│   └── support/
│       ├── petbuilds.sh        ← Patched: ccache removed, non-fatal petbuild exits
│       └── huge_kernel.sh      ← Patched: KERNEL_REPO_URL variable bug fixed
└── woof-distro/x86_64/ubuntu/jammy64/
    └── _00build.conf           ← Vantum-specific build config (SFS compression, PETBUILDS list)
```

---

## Building from source

See the [Quick-start checklist](DEBUG.md#quick-start-checklist-for-a-fresh-multipass-instance) in `DEBUG.md` for the full step-by-step build process.

The short version:

```bash
# On Windows 11, launch a Multipass VM
multipass launch 22.04 --disk 50G --memory 8G --cpus 4 --name beasos-build
multipass shell beasos-build

# Inside the VM
git clone https://github.com/yourusername/woof-CE
cd woof-CE

# Download FossaPup64 base (required, not in repo — too large)
wget http://distro.ibiblio.org/puppylinux/puppy-fossa/fossapup64-9.5.iso
wget https://archive.org/download/puppy_linux_-fossapup64/devx_fossapup64_9.5_cmake_included.sfs \
     -O devx_fossapup64_9.5.sfs

# Enter the build chroot
sudo ./run_woof ./fossapup64-9.5.iso ./devx_fossapup64_9.5.sfs .

# Inside the chroot
mkdir -p /tmp/petget_proc
cd /root/share/woof-CE
./merge2out  # select jammy64 when prompted

cd ../woof-out_x86_64_x86_64_ubuntu_jammy64
./0setup
./1download
./2createpackages
./3builddistro-Z
```

The output ISO will appear in `woof-output/` when the build completes.

---

## Debugging

Building a custom Linux distribution is not a smooth process. `DEBUG.md` in this repository documents every issue encountered during Vantum's initial build — 12 distinct failures, their root causes, and their fixes — covering everything from wrong base Puppy selection and broken ccache binaries to BusyBox checksum parser quirks and overlayfs layer visibility bugs. It's intended as a reference for anyone building on this codebase or attempting a similar Woof-CE build on a modern host.

---

## Status

Vantum is actively in development. The base build is working. UI customisation, the custom launcher, and theme work are ongoing.

---

## License

Vantum is built on Puppy Linux and Ubuntu packages. All third-party components retain their original licenses. Custom code and configuration in this repository is released under the MIT License.
