# Ombi

Ombi built from the upstream release tarballs with a fixed non-root user and no root-only init layer.

---

## Image

Tags (actual set depends on CI configuration):

- `latest` - latest successful build from the `main` branch
- `<OMBI_VERSION>` - based on Ombi version only

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
| `5000` | TCP      | `Web UI` |

### Storage

Paths inside the container that are intended for persistent or external data:

| Path in container          | Contents / purpose                         | Notes                                                                        |
|----------------------------|--------------------------------------------|------------------------------------------------------------------------------|
| `/config`                  | Ombi databases, logs, and runtime state    | Mount persistent storage here. Must be writable by the runtime user.         |
| `/app/ombi/ClientApp/dist` | Frontend assets and startup rewrite target | Must be writable by the runtime user when using a read-only root filesystem. |

### User / permissions

Runtime user and permissions expectations:

- Default user inside container: `ombi:ombi / 10001:10001`.
- The mounted `/config` path must already be writable by this user for fully rootless operation.
- `/app/ombi/ClientApp/dist` is writable by the runtime user on a normal writable root filesystem because Ombi rewrites `index.html` there on startup.
- The image keeps a bundled copy of the upstream `dist` assets at `/app/ombi-dist-template` and re-seeds `/app/ombi/ClientApp/dist` during startup.
- .NET diagnostics are disabled by default via `DOTNET_EnableDiagnostics=0` to reduce attach/debug surface inside the container.

### Read-only root filesystem

- Supported when both `/config` and `/app/ombi/ClientApp/dist` are writable.
- When running with `--read-only`, mount writable storage at `/app/ombi/ClientApp/dist` so the entrypoint can seed the frontend assets and Ombi can rewrite
  `index.html` in place.
- Provide writable temporary storage such as `--tmpfs /tmp` when using `--read-only`.

### Startup arguments

- Default command: `--storage /config --host http://*:5000`
- Add Ombi startup arguments at runtime if needed, for example `--baseurl /ombi` when serving behind a reverse proxy path.
