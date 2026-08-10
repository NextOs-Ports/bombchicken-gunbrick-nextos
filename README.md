# Bomb Chicken + Gunbrick Reloaded — NextOS

Private source and release repository for the universal AArch64 NextOS /
PortMaster compatibility ports of **Bomb Chicken** and **Gunbrick Reloaded**.

The repository contains only open-source compatibility code, framework
components, manifests, tests and BYO-data installers. It does not contain APKs,
Android libraries, game assets, videos, artwork, audio or saves.

## Ports

- `ports/bombchicken` — release 1.1.2;
- `ports/gunbrick` — release 0.2.0.

Both ports use the self-contained nxbootstrap 0.6 launcher, NXExtract 1.2.6,
nxcompat runtime evidence and NXRelease packaging. Video, audio, controller,
clean extraction UI and gameplay were validated on NextOS Mali-450, X5M and
Ark device families.

Build and installation details are in each port's `README.md` and
`INSTALLATION.md`. Release ZIPs are BYO-data and are published only through the
GitHub Releases page.

Canonical monorepo source commit:
`3ed8f2bb2e9029c2c6ae7eeac07c8d6f25a9e025`.
