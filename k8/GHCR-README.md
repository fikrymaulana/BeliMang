# Guide: Storing Docker Images in GitHub Container Registry

## Overview
GitHub Container Registry (ghcr.io) allows you to store and manage Docker images directly within GitHub. This guide walks you through the complete process.

## Prerequisites
- Docker installed on your machine
- A GitHub account
- A Docker image to push (or we'll create one)

## Step 1: Create a Personal Access Token (PAT)

1. Go to GitHub Settings → Developer settings → Personal access tokens → Tokens (classic)
2. Click "Generate new token (classic)"
3. Give it a descriptive name (e.g., "Docker Registry Access")
4. Select the following scopes:
   - `write:packages` (to upload images)
   - `read:packages` (to download images)
   - `delete:packages` (optional, to delete images)
5. Click "Generate token"
6. **Important:** Copy the token immediately - you won't see it again!

## Step 2: Authenticate Docker with GitHub

Log in to GitHub Container Registry using your PAT:

```bash
echo "YOUR_PERSONAL_ACCESS_TOKEN" | docker login ghcr.io -u YOUR_GITHUB_USERNAME --password-stdin
```

**Example:**
```bash
echo "ghp_abc123xyz..." | docker login ghcr.io -u johndoe --password-stdin
```

You should see: `Login Succeeded`

## Step 3: Build and Tag Your Docker Image

Build the image using:
```bash
docker build --no-cache --platform linux/amd64,linux/arm64 -t IMAGE_NAME:TAG
```
Docker images must be tagged with the GitHub Container Registry format before being pushed into the registry:

```bash
docker tag LOCAL_IMAGE:TAG ghcr.io/GITHUB_USERNAME/IMAGE_NAME:TAG
```

**Example:**
```bash
# Build the image "myapp:latest"
docker build --no-cache --platform linux/amd64,linux/arm64 -t myapp:latest

# If you have a local image called "myapp:latest"
docker tag myapp:latest ghcr.io/johndoe/myapp:latest

# You can also add version tags
docker tag myapp:latest ghcr.io/johndoe/myapp:v1.0.0
```

**Format breakdown:**
- `ghcr.io` - GitHub Container Registry domain
- `GITHUB_USERNAME` - Your GitHub username (lowercase)
- `IMAGE_NAME` - Name for your image
- `TAG` - Version tag (e.g., latest, v1.0.0, dev)


## Step 4: Push the Image to GitHub

```bash
docker push ghcr.io/GITHUB_USERNAME/IMAGE_NAME:TAG
```

**Example:**
```bash
docker push ghcr.io/johndoe/myapp:latest
docker push ghcr.io/johndoe/myapp:v1.0.0
```

## Step 5: Make Your Image Public (Optional)

By default, images are private. If you found a 401 Unauthorized error during the app deployment then you need to make them public:

1. Go to your GitHub profile
2. Click on "Packages" tab
3. Select your image
4. Click "Package settings"
5. Scroll to "Danger Zone"
6. Click "Change visibility" → Select "Public"

## Troubleshooting

**"denied: permission denied"**
- Check your PAT has correct scopes (write:packages)
- Ensure you're logged in: `docker login ghcr.io`

**"unauthorized: authentication required"**
- Your token may have expired
- Re-authenticate with a new token

**"invalid reference format"**
- Ensure username is lowercase
- Check image name doesn't contain invalid characters

## Viewing Your Images

Visit: `https://github.com/USERNAME?tab=packages`

Or view a specific package: `https://github.com/users/USERNAME/packages/container/IMAGE_NAME`