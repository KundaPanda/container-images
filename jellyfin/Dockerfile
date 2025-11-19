# renovate: datasource=github-releases depName=jellyfin/jellyfin
ARG JELLYFIN_VERSION=10.11.3
# renovate: datasource=docker depName=debian versioning=debian
ARG OS_VERSION=trixie

FROM badouralix/curl-jq AS packages

# renovate: datasource=github-releases depName=intel/intel-graphics-compiler
ARG COMPILER_VERSION=2.20.3
# renovate: datasource=github-releases depName=intel/compute-runtime
ARG COMPUTE_RUNTIME_VERSION=25.40.35563.4
ARG TARGETARCH

WORKDIR /tmp

RUN mkdir neo && \
    cd neo && \
    curl -s "https://api.github.com/repos/intel/intel-graphics-compiler/releases/tags/v${COMPILER_VERSION}"  \
        | jq -r ".assets[] | select(.name | test(\"^((?"'!'"devel).)*${TARGETARCH}\\\.deb\$\")) | .browser_download_url" \
        | xargs -I {} curl -L -O {} && \
    curl -s "https://api.github.com/repos/intel/compute-runtime/releases/tags/${COMPUTE_RUNTIME_VERSION}"  \
        | jq -r ".assets[] | select(.name | test(\"^((?"'!'"devel).)*(${TARGETARCH}\\\.(deb|ddeb)|sum)\$\")) | .browser_download_url" \
        | xargs -I {} curl -L -O {} && \
    sha256sum -c *.sum && \
    rm *.ddeb

FROM ghcr.io/jellyfin/jellyfin:${JELLYFIN_VERSION} AS src

FROM debian:${OS_VERSION}-slim

ARG UID=10001
ARG GID=10001
ARG OS_VERSION

RUN apt-get update \
    && apt-get install --no-install-recommends --yes \
       ca-certificates \
       gnupg \
       curl \
    && curl -fsSL https://repo.jellyfin.org/jellyfin_team.gpg.key | gpg --dearmor -o /etc/apt/keyrings/jellyfin.gpg \
    && printf "Types: deb\nURIs: https://repo.jellyfin.org/debian\nSuites: %s\nComponents: main\nSigned-By: /etc/apt/keyrings/jellyfin.gpg\n" "$OS_VERSION" \
      > /etc/apt/sources.list.d/jellyfin.sources \
    && apt-get update \
    && apt-get install --no-install-recommends --yes \
       locales \
       libicu76 \
       libfontconfig1 \
       libfreetype6 \
       libjemalloc2 \
       openssl \
       fonts-wqy-zenhei \
       fonts-wqy-microhei \
       fonts-arphic-ukai \
       fonts-arphic-uming \
       fonts-noto-cjk \
       fonts-ipafont-mincho \
       fonts-ipafont-gothic \
       fonts-unfonts-core \
       jellyfin-ffmpeg7 \
    && sed -i 's/# en_US.UTF-8 UTF-8/en_US.UTF-8 UTF-8/' /etc/locale.gen \
    && locale-gen \
    && apt-get purge --yes gnupg gnupg2 gnupg-agent gpg gpg-agent dirmngr curl \
    && apt-get autoremove --yes \
    && rm -rf /var/lib/apt/lists/*

COPY --from=packages /tmp/neo /tmp/neo
WORKDIR /tmp
RUN apt-get install --no-install-recommends --no-install-suggests -f -y ./neo/*.deb && rm -rf neo

RUN groupadd -g $GID jellyfin && \
    useradd --create-home --home-dir /config --shell /bin/bash -u $UID -g $GID -G video jellyfin && \
    mkdir -p /cache && \
    chown $UID:$GID /cache

# Jellyfin server + web UI
COPY --chown=${UID}:${GID} --from=src /jellyfin /jellyfin
# jemalloc link and any other Jellyfin-specific libs
COPY --chown=${UID}:${GID} --from=src /usr/lib/jellyfin /usr/lib/jellyfin

ENV JELLYFIN_DATA_DIR=/config \
    JELLYFIN_CACHE_DIR=/cache \
    JELLYFIN_CONFIG_DIR=/config/config \
    JELLYFIN_LOG_DIR=/config/log \
    JELLYFIN_WEB_DIR=/jellyfin/jellyfin-web \
    JELLYFIN_FFMPEG=/usr/lib/jellyfin-ffmpeg/ffmpeg \
    XDG_CACHE_HOME=/cache \
    LD_PRELOAD=/usr/lib/jellyfin/libjemalloc.so.2 \
    LC_ALL="en_US.UTF-8" \
    LANG="en_US.UTF-8" \
    LANGUAGE="en_US:en"

WORKDIR /jellyfin

HEALTHCHECK --interval=30s --timeout=5s --start-period=30s --retries=3 \
  CMD bash -c ' \
    exec 3<>/dev/tcp/127.0.0.1/8096 || exit 1 \
    printf "GET /health HTTP/1.0\r\nHost: localhost\r\n\r\n" >&3 \
    IFS= read -r status <&3 || exit 1 \
    echo "$status" | grep -q " 200 " || exit 1 \
  '

USER jellyfin

ENTRYPOINT ["/jellyfin/jellyfin"]
EXPOSE 8096
VOLUME ["/config", "/cache"]