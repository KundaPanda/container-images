# Jellyfin

Jellyfin built with a default non-root user and removed unused packages.

---

## Image

Tags (actual set depends on CI configuration):

- `latest` – latest successful build from the `main` branch
- `<JELLYFIN_VERSION>` – Based on Jellyfin version only

---

## Platforms

Published platforms:

- `linux/amd64`
- `linux/arm64`

---

## Runtime interface

### Network

Exposed ports inside the container:

| Port   | Protocol | Purpose  |
|--------|----------|----------|
| `8096` | TCP      | `Web UI` |

### Storage

Paths inside the container that are intended for persistent or external data:

| Path in container | Contents / purpose     | Notes                                                       |
|-------------------|------------------------|-------------------------------------------------------------|
| `/config`         | Jellyfin config        | Shouldn't use network or CoW storage according to Jellyfin. |
| `/cache`          | Cache / temporary data | Should be in-memory or on an SSD                            |

### User / permissions

Runtime user and permissions expectations:

- Default user inside container: `jellyfin:jellyfin / 10001:10001`.
- Files under the configured config and cache paths should be writable by this user.
- Needs access to the `/dev/dri` or `/dev/nvidia*` GPU devices when using hardware acceleration.
- Must be run with the `render` additional group (`--group-add` or `supplementalGroups: ...`) to access the GPU device. This is usually 993 on Ubuntu, but may differ per installation.
