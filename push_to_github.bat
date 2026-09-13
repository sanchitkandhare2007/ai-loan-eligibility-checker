@echo off
title Push to GitHub - AI Loan Eligibility Checker
set PATH=C:\Users\ADMIN\git\cmd;%PATH%

echo ================================================================
echo  Pushing AI Loan Eligibility Checker to GitHub
echo  Target: https://github.com/sanchitkandhare2007/ai-loan-eligibility-checker.git
echo ================================================================
echo.

git push -u origin main

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ================================================================
    echo  SUCCESS: Your project has been published to GitHub!
    echo  URL: https://github.com/sanchitkandhare2007/ai-loan-eligibility-checker
    echo ================================================================
) else (
    echo.
    echo ================================================================
    echo  Notice: If prompted for password, GitHub requires a Personal
    echo  Access Token (PAT).
    echo  Generate one at: https://github.com/settings/tokens
    echo ================================================================
)

echo.
pause
