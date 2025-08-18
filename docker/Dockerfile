FROM ghcr.io/fnr1r/ventoy-ng-toolchain/toolchain-alpine:alpha-1

RUN --mount=type=cache,sharing=locked,target=/var/cache/apk \
    apk add \
        wget xz

RUN --mount=type=cache,sharing=locked,target=/var/cache/apk \
    apk add \
        cmake just uv

RUN --mount=type=cache,sharing=locked,target=/var/cache/apk \
    apk add \
        build-base

RUN addgroup -g 1000 builder
RUN adduser -D -u 1000 -G builder builder

ENV PATH="$PATH:/opt/ventoy-toolchain/x86_64-unknown-linux-musl/bin:/opt/ventoy-toolchain/i386-unknown-linux-musl/bin:/opt/ventoy-toolchain/aarch64-unknown-linux-musl/bin:/opt/ventoy-toolchain/mips64el-unknown-linux-musl/bin"

RUN mkdir -p /usr/src/ventoy-ng-cpio

WORKDIR /usr/src/ventoy-ng-cpio

# hardlinking fails due to mounts
ENV UV_LINK_MODE=symlink

USER builder
