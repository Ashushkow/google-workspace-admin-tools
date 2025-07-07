# Google Workspace Admin Tools v2.0.3 Release Script
# Simple and reliable version

Write-Host "=========================================="
Write-Host "   Admin Team Tools v2.0.3 Release"
Write-Host "=========================================="
Write-Host ""

# Check git
Write-Host "Checking git..." -ForegroundColor Yellow
try {
    $gitVersion = git --version
    Write-Host "Git found: $gitVersion" -ForegroundColor Green
}
catch {
    Write-Host "Git is not installed" -ForegroundColor Red
    Write-Host "Download from: https://git-scm.com/download/win" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

# Get user input
Write-Host "Setting up Git configuration..." -ForegroundColor Yellow
$userName = Read-Host "Enter your Git username"
$userEmail = Read-Host "Enter your Git email"
$repoUrl = Read-Host "Enter your GitHub repository URL"

# Configure git
git config user.name "$userName"
git config user.email "$userEmail"
Write-Host "Git configured for: $userName <$userEmail>" -ForegroundColor Green

# Initialize repository if needed
if (-not (Test-Path ".git")) {
    Write-Host "Initializing Git repository..." -ForegroundColor Yellow
    git init
    Write-Host "Repository initialized" -ForegroundColor Green
}

# Add remote
Write-Host "Setting up remote..." -ForegroundColor Yellow
git remote remove origin 2>$null
git remote add origin $repoUrl
Write-Host "Remote added: $repoUrl" -ForegroundColor Green

# Add files
Write-Host "Adding files..." -ForegroundColor Yellow
git add .
Write-Host "Files added" -ForegroundColor Green

# Create commit
Write-Host "Creating commit..." -ForegroundColor Yellow
git commit -m "Initial commit: Google Workspace Admin Tools v2.0.3

Major refactoring and modular architecture:
- Refactored monolithic main.py into modular structure
- Organized code into src/api, src/ui, src/utils directories
- Fixed all imports to use relative imports
- Added comprehensive documentation
- Production-ready release v2.0.3

Features:
- Google Workspace Admin SDK integration
- User and group management
- Modern Tkinter GUI
- Comprehensive error handling and logging
- Security monitoring and caching

Tech stack: Python 3.12, Google Admin SDK, Tkinter"

if ($LASTEXITCODE -eq 0) {
    Write-Host "Commit created successfully" -ForegroundColor Green
}

# Create tag
Write-Host "Creating tag..." -ForegroundColor Yellow
git tag -a v2.0.3 -m "Release v2.0.3: Modular Architecture with Google Admin SDK Integration"
if ($LASTEXITCODE -eq 0) {
    Write-Host "Tag created successfully" -ForegroundColor Green
}

# Push to repository
Write-Host "Pushing to repository..." -ForegroundColor Yellow
git push -u origin main
if ($LASTEXITCODE -eq 0) {
    Write-Host "Code pushed successfully" -ForegroundColor Green
} else {
    Write-Host "Push failed - you may need to authenticate" -ForegroundColor Yellow
}

# Push tags
Write-Host "Pushing tags..." -ForegroundColor Yellow
git push origin --tags
if ($LASTEXITCODE -eq 0) {
    Write-Host "Tags pushed successfully" -ForegroundColor Green
}

Write-Host ""
Write-Host "========================================"
Write-Host "   Release v2.0.3 completed!"
Write-Host "========================================"
Write-Host ""
Write-Host "Next steps:"
Write-Host "1. Go to your GitHub repository"
Write-Host "2. Create a new release with tag v2.0.3"
Write-Host "3. Use docs/releases/RELEASE_NOTES_v2.0.3.md for description"
Write-Host ""

Read-Host "Press Enter to exit"
