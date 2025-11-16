# GitHub Actions Workflows

## Docker Build and Push

The `docker-build.yml` workflow automatically builds and publishes Docker images to GitHub Container Registry (GHCR).

### Triggers

- **Push to main/master**: Builds and pushes with `latest` tag
- **Version tags** (v*.*.*): Builds and pushes with semantic version tags
- **Pull requests**: Builds but does not push (validation only)
- **Manual dispatch**: Can be triggered manually from GitHub Actions UI

### Image Tags

The workflow creates multiple tags automatically:

- `latest` - Latest build from main/master branch
- `main` or `master` - Branch name tag
- `v1.2.3` - Semantic version (from git tags)
- `v1.2` - Major.minor version
- `v1` - Major version only
- `main-abc1234` - Branch name with commit SHA

### Multi-Platform Support

Images are built for:
- `linux/amd64` (x86_64)
- `linux/arm64` (ARM 64-bit, including Raspberry Pi 4/5)

### Caching

The workflow uses GitHub Actions cache to speed up builds:
- Layer caching via `type=gha`
- Cached between workflow runs
- Reduces build time significantly

### Permissions

The workflow requires:
- `contents: read` - To checkout the repository
- `packages: write` - To push to GHCR

These are automatically provided by the `GITHUB_TOKEN`.

### Usage

#### Automatic Builds

Simply push to main or create a version tag:

```bash
# Trigger build on main
git push origin main

# Trigger versioned release
git tag v1.0.0
git push origin v1.0.0
```

#### Manual Trigger

1. Go to Actions tab in GitHub
2. Select "Build and Push Docker Image"
3. Click "Run workflow"
4. Select branch and run

### Accessing Images

Images are published to:
```
ghcr.io/marcoplaisier/componentinventory:latest
ghcr.io/marcoplaisier/componentinventory:v1.0.0
```

For public repositories, images can be pulled without authentication:
```bash
docker pull ghcr.io/marcoplaisier/componentinventory:latest
```

For private repositories, authenticate first:
```bash
echo $GITHUB_TOKEN | docker login ghcr.io -u USERNAME --password-stdin
docker pull ghcr.io/marcoplaisier/componentinventory:latest
```

### Troubleshooting

**Build Fails**:
- Check the Actions tab for detailed logs
- Verify Dockerfile syntax
- Ensure all dependencies are available

**Push Fails**:
- Verify repository has packages enabled
- Check workflow permissions in Settings > Actions > General
- Ensure GITHUB_TOKEN has write access

**Image Not Found**:
- For private repos, check package visibility in Settings > Packages
- Verify authentication credentials
- Check image name matches repository name (lowercase)
