# -*- coding: utf-8 -*-
# Auto-commit script for Google Workspace Admin Tools
# Usage: .\auto_commit.ps1 "Commit message"

param(
    [Parameter(Mandatory=$true)]
    [string]$CommitMessage
)

# Set UTF-8 encoding
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

# Add Git to PATH
$env:PATH += ";C:\Program Files\Git\bin"

# Change to project directory
Set-Location "c:\Users\sputnik8\Documents\Project"

Write-Host "Checking repository status..." -ForegroundColor Green
git status

Write-Host "`nAdding all changes..." -ForegroundColor Green
git add .

Write-Host "`nCreating commit..." -ForegroundColor Green
git commit -m $CommitMessage

Write-Host "`nPushing changes to GitHub..." -ForegroundColor Green
git push

Write-Host "`nDone! Changes pushed to GitHub." -ForegroundColor Green
