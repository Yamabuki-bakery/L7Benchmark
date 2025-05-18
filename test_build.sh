#!/bin/bash
# Script to test your PyInstaller build locally
# This helps ensure that the GitHub Action will succeed

echo "Testing PyInstaller build locally..."
pyinstaller l7benchmark.spec

if [ $? -eq 0 ]; then
    echo "✅ Build successful!"
    
    # Test the executable
    echo "Testing the executable..."
    ./dist/l7benchmark --help
    
    if [ $? -eq 0 ]; then
        echo "✅ Executable runs correctly!"
    else
        echo "❌ Executable has issues. Please fix before pushing to GitHub."
        exit 1
    fi
else
    echo "❌ Build failed. Please fix issues before pushing to GitHub."
    exit 1
fi

echo "Your build is ready for GitHub CI/CD!"
