group "default" {
  targets = ["server-dev"]
}

group "staging" {
  targets = ["server-staging"]
}

group "release" {
  targets = ["server-release"]
}

target "common" {
  dockerfile = "Dockerfile.common"
  platforms = ["linux/arm64/v8", "linux/amd64"]
}

target "server-dev" {
  contexts = {
    common = "target:common"
  }
  dockerfile = "Dockerfile.server"
  tags = ["carolina-radio"]
}

target "server-staging" {
  inherits = ["server-dev"]
  platforms = ["linux/arm64/v8", "linux/amd64"]
  tags = ["ghcr.io/nolanwelch/carolina-radio:staging"]
}

target "server-release" {
  inherits = ["server-staging"]
  tags = ["ghcr.io/nolanwelch/carolina-radio:latest"]
}