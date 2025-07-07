# Admin Team Tools v2.0.3 Release Script
# PowerShell version

Write-Host "==========================================" -ForegroundColor Green
Write-Host "   Admin Team Tools v2.0.3 Release" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Green
Write-Host ""

# Check git
Write-Host "Checking git..." -ForegroundColor Yellow
try {
    $gitVersion = git --version
    Write-Host "✅ Git found: $gitVersion" -ForegroundColor Green
}
catch {
    Write-Host "❌ Git is not installed" -ForegroundColor Red
    Write-Host "Download Git from: https://git-scm.com/download/win" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

# Get user configuration
Write-Host "Configuring Git user..." -ForegroundColor Yellow
$userName = Read-Host "Enter your Git username (or press Enter for default)"
if ([string]::IsNullOrWhiteSpace($userName)) {
    $userName = "Developer"
}
$userEmail = Read-Host "Enter your Git email (or press Enter for default)"
if ([string]::IsNullOrWhiteSpace($userEmail)) {
    $userEmail = "developer@example.com"
}

git config user.name "$userName"
git config user.email "$userEmail"
Write-Host "✅ Git user configured: $userName <$userEmail>" -ForegroundColor Green

# Initialize git repository if not exists
if (-not (Test-Path ".git")) {
    Write-Host "Initializing Git repository..." -ForegroundColor Yellow
    git init
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Git repository initialized" -ForegroundColor Green
    }
}

# Get repository URL
$repoUrl = Read-Host "Enter your GitHub repository URL (e.g., https://github.com/username/google-workspace-admin-tools.git)"
if (-not [string]::IsNullOrWhiteSpace($repoUrl)) {
    Write-Host "Adding remote origin..." -ForegroundColor Yellow
    git remote remove origin 2>$null
    git remote add origin $repoUrl
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Remote origin added: $repoUrl" -ForegroundColor Green
    }
}

# Add all files
Write-Host "Adding all files..." -ForegroundColor Yellow
git add .
if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Files added successfully" -ForegroundColor Green
}

# Create commit
Write-Host "Creating commit..." -ForegroundColor Yellow
$commitMessage = @"
Initial commit: Google Workspace Admin Tools v2.0.3

Major refactoring and modular architecture:
- Refactored monolithic main.py (952 lines) into modular structure (48 lines)
- Organized code into src/api, src/ui, src/utils directories
- Fixed all imports to use relative imports
- Added comprehensive documentation and tests
- Prepared release v2.0.3 with full functionality

Features:
- Google Workspace Admin SDK integration
- User management (list, create, update, delete)
- Group management with member operations
- Modern Tkinter GUI with theming
- Comprehensive error handling and logging
- Security audit and monitoring
- Async operations support
- Configuration management
- Data caching system

Tech stack: Python 3.12, Google Admin SDK, Tkinter
Ready for production use and team collaboration.
"@

git commit -m $commitMessage
if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Commit created successfully" -ForegroundColor Green
}

# Create tag
Write-Host "Creating tag..." -ForegroundColor Yellow
$tagMessage = @"
Release v2.0.3: Modular Architecture with Full Google Admin SDK Integration

Major refactoring:
- Split monolithic main.py (952 lines) into 48-line entry point
- Created modular structure: src/api, src/ui, src/utils
- Fixed all relative imports
- Added comprehensive documentation
- Full test coverage
- Security enhancements

New features:
- Enhanced group management
- Improved error handling
- Modern UI components
- Advanced caching system
- Monitoring and audit logging

Breaking changes: None (backward compatible)
Migration: Automatic import resolution
"@

git tag -a v2.0.3 -m $tagMessage
if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Tag created successfully" -ForegroundColor Green
}

# Push changes
Write-Host "Pushing changes..." -ForegroundColor Yellow
git push -u origin main
if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Changes pushed successfully" -ForegroundColor Green
} else {
    Write-Host "⚠️  Push failed. You may need to:" -ForegroundColor Yellow
    Write-Host "   • Authenticate with GitHub" -ForegroundColor Cyan
    Write-Host "   • Check repository URL" -ForegroundColor Cyan
    Write-Host "   • Use GitHub Desktop for easier auth" -ForegroundColor Cyan
}

# Push tags
Write-Host "Pushing tags..." -ForegroundColor Yellow
git push origin --tags
if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Tags pushed successfully" -ForegroundColor Green
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "   Release v2.0.3 completed!" -ForegroundColor Green  
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "🎉 Release highlights:" -ForegroundColor Cyan
Write-Host "   • Modular architecture (main.py: 952→48 lines)" -ForegroundColor White
Write-Host "   • Organized folder structure (src/api, src/ui, src/utils)" -ForegroundColor White
Write-Host "   • Fixed relative imports" -ForegroundColor White
Write-Host "   • Comprehensive documentation" -ForegroundColor White
Write-Host "   • Production-ready code" -ForegroundColor White
Write-Host ""
Write-Host "📋 Next steps:" -ForegroundColor Cyan
Write-Host "   1. Go to your GitHub repository" -ForegroundColor White
Write-Host "   2. Click 'Releases' → 'Create a new release'" -ForegroundColor White
Write-Host "   3. Select tag v2.0.3" -ForegroundColor White
Write-Host "   4. Title: v2.0.3 - Modular Architecture Release" -ForegroundColor White
Write-Host "   5. Copy description from docs/releases/RELEASE_NOTES_v2.0.3.md" -ForegroundColor White
Write-Host "   6. Publish release" -ForegroundColor White
Write-Host ""
Write-Host "📚 Documentation:" -ForegroundColor Cyan
Write-Host "   • README_GITHUB.md - GitHub repository README" -ForegroundColor White
Write-Host "   • docs/CHANGELOG.md - Change history" -ForegroundColor White
Write-Host "   • docs/releases/ - Release materials" -ForegroundColor White

Read-Host "Press Enter to exit"
