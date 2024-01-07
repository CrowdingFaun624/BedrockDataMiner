@echo off
title Command Repeating Batch File
for %%a in (*.fsb) do "fsb_aud_extr.exe" "%%a"
