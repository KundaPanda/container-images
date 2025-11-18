# renovate: datasource=github-releases depName=jellyfin/jellyfin
ARG JELLYFIN_VERSION=10.11.2


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
    sha256sum -c *.sum


FROM ghcr.io/jellyfin/jellyfin:${JELLYFIN_VERSION}

ARG UID=10001
ARG GID=10001

COPY --from=packages /tmp/neo /tmp/neo
WORKDIR /tmp

RUN groupadd -g $GID jellyfin && \
    useradd --create-home --home-dir /config --shell /bin/bash -u $UID -g $GID -G video jellyfin

RUN dpkg -i neo/*.deb && rm -rf neo

USER jellyfin