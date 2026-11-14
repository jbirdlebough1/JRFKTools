# Defect Tracking Directive for JRFK

> [!IMPORTANT]
> **Every change is tracked as a bug in CLEBugger (`D:\CLEBUGGER`).**
> No file or asset may be modified without an associated defect entry.

### Protocol
1. **Initiate Defect**:
   Before modifying any file, verify or create an entry in CLEBugger:
   ```powershell
   & "C:\Program Files\CLE\python_runtime\python.exe" D:\CLEBUGGER\bug.py add JRFK "<Description>" --build "v01.00.00-beta" --comp "<Component>"
   ```
2. **Execute & Test**:
   Make code/asset modifications and run automated validations (Playwright, pytest, or script runners).
3. **Resolve Defect**:
   Once validated, mark the defect `RESOLVED`:
   ```powershell
   & "C:\Program Files\CLE\python_runtime\python.exe" D:\CLEBUGGER\bug.py resolve <ID> "<Verification and fix summary>"
   ```
4. **GitHub Daily Sync**:
   All GitHub issues are synchronized daily via:
   ```powershell
   & "C:\Program Files\CLE\python_runtime\python.exe" D:\CLEBUGGER\bug.py sync-github JRFK
   ```
