using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Drawing;
using System.IO;
using System.IO.Compression;
using System.Net;
using System.Net.Sockets;
using System.Reflection;
using System.Security.Principal;
using System.Text;
using System.Threading;
using System.Windows.Forms;
using System.Runtime.InteropServices;

namespace JrfkLauncher
{
    public class StatusForm : Form
    {
        private Label lblTitle;
        private Label lblStatus;
        private TextBox txtLog;
        private Button btnOpenBrowser;
        private Button btnOpenFolder;
        private Button btnStopExit;
        private NotifyIcon trayIcon;

        private string installDir;
        private Process serverProc;
        private readonly int port = 8089;
        private volatile bool stopping = false;
        private volatile bool allowExit = false;
        private volatile bool bootstrapStarted = false;

        private const string PYTHON_EMBED_URL = "https://www.python.org/ftp/python/3.12.8/python-3.12.8-embed-amd64.zip";
        private const string RPI_IMAGER_URL = "https://downloads.raspberrypi.com/imager/imager_latest.exe";

        public StatusForm()
        {
            Text = "JRFK 32->64-Bit Migrator (Elevated)";
            Size = new Size(640, 400);
            StartPosition = FormStartPosition.CenterScreen;
            FormBorderStyle = FormBorderStyle.FixedDialog;
            MaximizeBox = false;
            ShowInTaskbar = false;
            WindowState = FormWindowState.Minimized;
            Opacity = 0;
            BackColor = Color.FromArgb(15, 23, 42);
            ForeColor = Color.FromArgb(241, 245, 249);

            ContextMenu trayMenu = new ContextMenu();
            trayMenu.MenuItems.Add("Open Migrator UI", delegate { OpenBrowser(); });
            trayMenu.MenuItems.Add("Show Status Log", delegate { ShowStatusWindow(); });
            trayMenu.MenuItems.Add("-");
            trayMenu.MenuItems.Add("Stop Server & Exit", delegate { ExitApplication(); });

            trayIcon = new NotifyIcon();
            trayIcon.Icon = SystemIcons.Application;
            trayIcon.Text = "JRFK 32->64-Bit Migrator (Port 8089)";
            trayIcon.ContextMenu = trayMenu;
            trayIcon.Visible = true;
            trayIcon.DoubleClick += delegate { OpenBrowser(); };

            lblTitle = new Label();
            lblTitle.Text = "JRFK 32-to-64-Bit RF-KIT Migrator";
            lblTitle.Font = new Font("Segoe UI", 14f, FontStyle.Bold);
            lblTitle.ForeColor = Color.FromArgb(52, 211, 153);
            lblTitle.Location = new Point(18, 14);
            lblTitle.Size = new Size(590, 28);
            Controls.Add(lblTitle);

            lblStatus = new Label();
            lblStatus.Text = "Initializing elevated bootstrap...";
            lblStatus.Font = new Font("Segoe UI", 9.5f, FontStyle.Regular);
            lblStatus.ForeColor = Color.FromArgb(203, 213, 225);
            lblStatus.Location = new Point(18, 46);
            lblStatus.Size = new Size(590, 22);
            Controls.Add(lblStatus);

            txtLog = new TextBox();
            txtLog.Multiline = true;
            txtLog.ReadOnly = true;
            txtLog.ScrollBars = ScrollBars.Vertical;
            txtLog.Font = new Font("Consolas", 9f);
            txtLog.BackColor = Color.FromArgb(2, 6, 23);
            txtLog.ForeColor = Color.FromArgb(226, 232, 240);
            txtLog.BorderStyle = BorderStyle.FixedSingle;
            txtLog.Location = new Point(18, 76);
            txtLog.Size = new Size(588, 224);
            Controls.Add(txtLog);

            btnOpenBrowser = new Button();
            btnOpenBrowser.Text = "Open Migrator UI";
            btnOpenBrowser.Enabled = false;
            btnOpenBrowser.BackColor = Color.FromArgb(22, 163, 74);
            btnOpenBrowser.ForeColor = Color.White;
            btnOpenBrowser.FlatStyle = FlatStyle.Flat;
            btnOpenBrowser.Location = new Point(18, 314);
            btnOpenBrowser.Size = new Size(165, 34);
            btnOpenBrowser.Click += delegate { OpenBrowser(); };
            Controls.Add(btnOpenBrowser);

            btnOpenFolder = new Button();
            btnOpenFolder.Text = "Open Project Folder";
            btnOpenFolder.Enabled = false;
            btnOpenFolder.BackColor = Color.FromArgb(51, 65, 85);
            btnOpenFolder.ForeColor = Color.White;
            btnOpenFolder.FlatStyle = FlatStyle.Flat;
            btnOpenFolder.Location = new Point(195, 314);
            btnOpenFolder.Size = new Size(165, 34);
            btnOpenFolder.Click += delegate {
                if (!string.IsNullOrEmpty(installDir) && Directory.Exists(installDir))
                    Process.Start("explorer.exe", installDir);
            };
            Controls.Add(btnOpenFolder);

            btnStopExit = new Button();
            btnStopExit.Text = "Stop Server & Exit";
            btnStopExit.BackColor = Color.FromArgb(185, 28, 28);
            btnStopExit.ForeColor = Color.White;
            btnStopExit.FlatStyle = FlatStyle.Flat;
            btnStopExit.Location = new Point(441, 314);
            btnStopExit.Size = new Size(165, 34);
            btnStopExit.Click += delegate { ExitApplication(); };
            Controls.Add(btnStopExit);

            Load += delegate {
                BeginInvoke((MethodInvoker)delegate {
                    Hide();
                    Opacity = 1;
                    if (!bootstrapStarted)
                    {
                        bootstrapStarted = true;
                        Thread worker = new Thread(BootstrapAndRun);
                        worker.IsBackground = true;
                        worker.Start();
                    }
                });
            };

            FormClosing += delegate(object sender, FormClosingEventArgs e) {
                if (!allowExit && e.CloseReason == CloseReason.UserClosing)
                {
                    e.Cancel = true;
                    Hide();
                    ShowInTaskbar = false;
                    return;
                }
                stopping = true;
                try { if (trayIcon != null) { trayIcon.Visible = false; trayIcon.Dispose(); } } catch { }
                StopChildServer();
            };
        }

        private void ShowStatusWindow()
        {
            if (IsDisposed) return;
            try
            {
                BeginInvoke((MethodInvoker)delegate {
                    Opacity = 1;
                    ShowInTaskbar = true;
                    WindowState = FormWindowState.Normal;
                    Show();
                    Activate();
                });
            }
            catch { }
        }

        private void HideToTray()
        {
            if (IsDisposed) return;
            try
            {
                BeginInvoke((MethodInvoker)delegate {
                    Hide();
                    ShowInTaskbar = false;
                });
            }
            catch { }
        }

        private void ExitApplication()
        {
            allowExit = true;
            Close();
        }

        private void Log(string line)
        {
            if (IsDisposed) return;
            try
            {
                BeginInvoke((MethodInvoker)delegate {
                    string ts = DateTime.Now.ToString("HH:mm:ss");
                    txtLog.AppendText(string.Format("[{0}] {1}{2}", ts, line, Environment.NewLine));
                });
            }
            catch { }
        }

        private void SetStatus(string text)
        {
            if (IsDisposed) return;
            try
            {
                BeginInvoke((MethodInvoker)delegate { lblStatus.Text = text; });
            }
            catch { }
        }

        private void EnableReadyButtons()
        {
            if (IsDisposed) return;
            try
            {
                BeginInvoke((MethodInvoker)delegate {
                    btnOpenBrowser.Enabled = true;
                    btnOpenFolder.Enabled = true;
                });
            }
            catch { }
        }

        private static bool IsAdministrator()
        {
            try
            {
                WindowsIdentity id = WindowsIdentity.GetCurrent();
                WindowsPrincipal pr = new WindowsPrincipal(id);
                return pr.IsInRole(WindowsBuiltInRole.Administrator);
            }
            catch { return false; }
        }

        private string ResolveInstallDir(string exeDir)
        {
            string trimmed = exeDir.TrimEnd('\\', '/');
            string dirName = Path.GetFileName(trimmed);
            if (File.Exists(Path.Combine(exeDir, @"tools\migrator\server.py")) ||
                string.Equals(dirName, "JRFK", StringComparison.OrdinalIgnoreCase))
            {
                return trimmed;
            }
            if (Directory.Exists(@"D:\"))
            {
                return @"D:\JRFK";
            }
            return Path.Combine(
                Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData),
                "JRFK"
            );
        }

        private void ExtractEmbeddedPayload(string targetDir)
        {
            Assembly asm = Assembly.GetExecutingAssembly();
            using (Stream resStream = asm.GetManifestResourceStream("JRFK.payload.zip"))
            {
                if (resStream == null)
                {
                    Log("[!] No embedded payload zip resource found; using existing workspace files.");
                    return;
                }

                string tmpZip = Path.Combine(Path.GetTempPath(), "jrfk_payload_" + Process.GetCurrentProcess().Id + ".zip");
                using (FileStream fs = File.Create(tmpZip))
                {
                    resStream.CopyTo(fs);
                }

                int extracted = 0;
                using (ZipArchive archive = ZipFile.OpenRead(tmpZip))
                {
                    foreach (ZipArchiveEntry entry in archive.Entries)
                    {
                        if (string.IsNullOrEmpty(entry.Name)) continue;
                        string rel = entry.FullName.Replace('/', '\\');
                        if (rel.StartsWith(@"backups\", StringComparison.OrdinalIgnoreCase) ||
                            rel.StartsWith(@"images\", StringComparison.OrdinalIgnoreCase))
                        {
                            continue;
                        }
                        string destPath = Path.Combine(targetDir, rel);
                        string destParent = Path.GetDirectoryName(destPath);
                        if (!string.IsNullOrEmpty(destParent) && !Directory.Exists(destParent))
                        {
                            Directory.CreateDirectory(destParent);
                        }
                        if (!File.Exists(destPath) || entry.LastWriteTime.UtcDateTime > File.GetLastWriteTimeUtc(destPath).AddSeconds(2))
                        {
                            entry.ExtractToFile(destPath, true);
                            extracted++;
                        }
                    }
                }
                try { File.Delete(tmpZip); } catch { }
                Log(string.Format("[+] Verified/installed {0} JRFK payload files into {1}", extracted, targetDir));
            }
        }

        private void CreateDesktopShortcut(string targetExePath, string workDir)
        {
            try
            {
                string desktop = Environment.GetFolderPath(Environment.SpecialFolder.DesktopDirectory);
                string lnkPath = Path.Combine(desktop, "JRFK Migrator.lnk");
                Type shellType = Type.GetTypeFromProgID("WScript.Shell");
                if (shellType == null) return;
                dynamic shell = Activator.CreateInstance(shellType);
                dynamic shortcut = shell.CreateShortcut(lnkPath);
                shortcut.TargetPath = targetExePath;
                shortcut.WorkingDirectory = workDir;
                shortcut.Description = "JRFK 32-to-64-Bit RF-KIT SD Migrator";
                shortcut.Save();
                Log("[+] Desktop shortcut ready: " + lnkPath);
            }
            catch (Exception ex)
            {
                Log("[-] Shortcut note: " + ex.Message);
            }
        }

        private static string RunCapture(string fileName, string args, int timeoutMs)
        {
            try
            {
                ProcessStartInfo psi = new ProcessStartInfo(fileName, args);
                psi.UseShellExecute = false;
                psi.CreateNoWindow = true;
                psi.RedirectStandardOutput = true;
                psi.RedirectStandardError = true;
                using (Process p = Process.Start(psi))
                {
                    string outTxt = p.StandardOutput.ReadToEnd();
                    p.WaitForExit(timeoutMs);
                    return outTxt;
                }
            }
            catch { return ""; }
        }

        private static bool IsUsablePython(string pyPath)
        {
            if (string.IsNullOrEmpty(pyPath) || !File.Exists(pyPath)) return false;
            if (pyPath.IndexOf(@"\WindowsApps\", StringComparison.OrdinalIgnoreCase) >= 0) return false;
            string ver = RunCapture(pyPath, "--version", 5000);
            return ver.IndexOf("Python 3", StringComparison.OrdinalIgnoreCase) >= 0;
        }

        private string FindPython(string baseDir)
        {
            List<string> candidates = new List<string>();
            candidates.Add(Path.Combine(baseDir, @"tools\python\python.exe"));
            candidates.Add(@"C:\Program Files\CLE\python_runtime\python.exe");

            string pathEnv = Environment.GetEnvironmentVariable("PATH") ?? "";
            foreach (string part in pathEnv.Split(';'))
            {
                string dir = part.Trim();
                if (string.IsNullOrEmpty(dir)) continue;
                if (dir.IndexOf(@"\WindowsApps", StringComparison.OrdinalIgnoreCase) >= 0) continue;
                candidates.Add(Path.Combine(dir, "python.exe"));
            }

            string localPyRoot = Path.Combine(
                Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData),
                @"Programs\Python"
            );
            if (Directory.Exists(localPyRoot))
            {
                foreach (string d in Directory.GetDirectories(localPyRoot, "Python3*"))
                    candidates.Add(Path.Combine(d, "python.exe"));
            }

            foreach (string c in candidates)
            {
                if (IsUsablePython(c)) return c;
            }
            return null;
        }

        private void DownloadFileWithProgress(string url, string destPath, string label)
        {
            ServicePointManager.SecurityProtocol |= SecurityProtocolType.Tls12 | (SecurityProtocolType)3072;
            string parent = Path.GetDirectoryName(destPath);
            if (!string.IsNullOrEmpty(parent) && !Directory.Exists(parent))
                Directory.CreateDirectory(parent);

            string tmp = destPath + ".part";
            Log(string.Format("[*] Downloading {0}: {1}", label, url));
            int lastPct = -10;
            ManualResetEvent done = new ManualResetEvent(false);
            Exception dlErr = null;

            using (WebClient wc = new WebClient())
            {
                wc.Headers.Add("User-Agent", "JRFK-Bootstrap/2.0");
                wc.DownloadProgressChanged += delegate(object s, DownloadProgressChangedEventArgs e) {
                    if (e.ProgressPercentage >= lastPct + 20)
                    {
                        lastPct = e.ProgressPercentage;
                        SetStatus(string.Format("Downloading {0}... {1}%", label, e.ProgressPercentage));
                    }
                };
                wc.DownloadFileCompleted += delegate(object s, System.ComponentModel.AsyncCompletedEventArgs e) {
                    dlErr = e.Error;
                    done.Set();
                };
                wc.DownloadFileAsync(new Uri(url), tmp);
                done.WaitOne();
            }

            if (dlErr != null)
            {
                try { if (File.Exists(tmp)) File.Delete(tmp); } catch { }
                throw dlErr;
            }
            if (File.Exists(destPath)) File.Delete(destPath);
            File.Move(tmp, destPath);
        }

        private string EnsurePythonInstalled(string baseDir)
        {
            string py = FindPython(baseDir);
            if (py != null)
            {
                Log("[+] Python 3 found: " + py);
                return py;
            }

            SetStatus("Installing Python 3 runtime on the fly...");
            ShowStatusWindow();
            string pyDir = Path.Combine(baseDir, @"tools\python");
            string zipPath = Path.Combine(baseDir, @"tools\python_embed.zip");
            DownloadFileWithProgress(PYTHON_EMBED_URL, zipPath, "Python 3.12 Embeddable");

            if (!Directory.Exists(pyDir)) Directory.CreateDirectory(pyDir);
            ZipFile.ExtractToDirectory(zipPath, pyDir);
            try { File.Delete(zipPath); } catch { }

            string installedPy = Path.Combine(pyDir, "python.exe");
            if (!IsUsablePython(installedPy))
                throw new Exception("Downloaded Python runtime verification failed at " + installedPy);

            Log("[+] Installed Python 3 runtime into " + pyDir);
            return installedPy;
        }

        private string FindRpiImager(string baseDir)
        {
            string localApp = Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData);
            string[] candidates = new string[] {
                Path.Combine(baseDir, @"tools\rpi-imager\rpi-imager.exe"),
                @"C:\Program Files\Raspberry Pi Ltd\Imager\rpi-imager.exe",
                @"C:\Program Files\Raspberry Pi Imager\rpi-imager.exe",
                @"C:\Program Files (x86)\Raspberry Pi Imager\rpi-imager.exe",
                Path.Combine(localApp, @"Programs\Raspberry Pi Imager\rpi-imager.exe"),
            };
            foreach (string c in candidates)
            {
                if (File.Exists(c)) return c;
            }
            return null;
        }

        private void EnsureRpiImagerInstalled(string baseDir)
        {
            string existing = FindRpiImager(baseDir);
            if (existing != null)
            {
                Log("[+] Raspberry Pi Imager found: " + existing);
                return;
            }

            SetStatus("Installing Raspberry Pi Imager on the fly...");
            ShowStatusWindow();
            string imagerDir = Path.Combine(baseDir, @"tools\rpi-imager");
            string installer = Path.Combine(imagerDir, "imager_latest.exe");
            DownloadFileWithProgress(RPI_IMAGER_URL, installer, "Raspberry Pi Imager");

            Log("[*] Running silent install of Raspberry Pi Imager into " + imagerDir + "...");
            ProcessStartInfo psi = new ProcessStartInfo(installer, "/S /D=" + imagerDir);
            psi.UseShellExecute = false;
            using (Process p = Process.Start(psi))
            {
                p.WaitForExit(180000);
            }

            string verified = FindRpiImager(baseDir);
            if (verified == null)
                throw new Exception("Raspberry Pi Imager installation completed but rpi-imager.exe was not found.");

            Log("[+] Installed Raspberry Pi Imager: " + verified);
        }

        private bool IsElevatedServerAlive()
        {
            return IsServerHealthy(port, requireAdminCheck: true);
        }

        private static bool IsServerHealthy(int targetPort, bool requireAdminCheck = false)
        {
            try
            {
                string endpoint = requireAdminCheck ? "/api/tools" : "/api/logs";
                HttpWebRequest req = (HttpWebRequest)WebRequest.Create(string.Format("http://127.0.0.1:{0}{1}", targetPort, endpoint));
                req.Timeout = 2000;
                req.ReadWriteTimeout = 2000;
                using (HttpWebResponse resp = (HttpWebResponse)req.GetResponse())
                {
                    if ((int)resp.StatusCode != 200) return false;
                    if (!requireAdminCheck) return true;
                    using (StreamReader sr = new StreamReader(resp.GetResponseStream()))
                    {
                        string body = sr.ReadToEnd();
                        return body.IndexOf("\"is_admin\": true", StringComparison.OrdinalIgnoreCase) >= 0 ||
                               body.IndexOf("\"is_admin\":true", StringComparison.OrdinalIgnoreCase) >= 0;
                    }
                }
            }
            catch { return false; }
        }

        private static void KillPortAndStaleInstances(int targetPort, bool killOtherJrfkExe)
        {
            int selfPid = Process.GetCurrentProcess().Id;
            if (killOtherJrfkExe)
            {
                try
                {
                    foreach (Process p in Process.GetProcessesByName("JRFK"))
                    {
                        if (p.Id != selfPid)
                        {
                            try { p.Kill(); p.WaitForExit(3000); } catch { }
                        }
                    }
                }
                catch { }
            }
            try
            {
                string extraClause = killOtherJrfkExe ? " -or $_.CommandLine -match 'tools\\\\migrator\\\\server\\.py'" : "";
                string cmd = string.Format(
                    "-NoProfile -NonInteractive -Command \"$pids = @(Get-NetTCPConnection -LocalPort {0} -ErrorAction SilentlyContinue | Select-Object -ExpandProperty OwningProcess); Get-CimInstance Win32_Process | Where-Object {{ $_.ProcessId -ne {1} -and ($pids -contains $_.ProcessId{2}) }} | ForEach-Object {{ Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue }}\"",
                    targetPort,
                    selfPid,
                    extraClause
                );
                RunCapture("powershell.exe", cmd, 8000);
            }
            catch { }
        }

        private void KillPortListeners()
        {
            KillPortAndStaleInstances(port, killOtherJrfkExe: false);
        }

        private bool WaitForPortReady(int timeoutMs)
        {
            Stopwatch sw = Stopwatch.StartNew();
            while (sw.ElapsedMilliseconds < timeoutMs && !stopping)
            {
                try
                {
                    using (TcpClient tcp = new TcpClient())
                    {
                        tcp.Connect("127.0.0.1", port);
                        return true;
                    }
                }
                catch { Thread.Sleep(250); }
            }
            return false;
        }

        private void OpenBrowser()
        {
            try
            {
                Process.Start(string.Format("http://127.0.0.1:{0}/", port));
            }
            catch (Exception ex)
            {
                Log("[-] Browser launch note: " + ex.Message);
            }
        }

        private void StopChildServer()
        {
            try
            {
                if (serverProc != null && !serverProc.HasExited)
                {
                    serverProc.Kill();
                }
            }
            catch { }
        }

        private void BootstrapAndRun()
        {
            try
            {
                if (!IsAdministrator())
                {
                    Log("[!] Not elevated; UAC Administrator privileges are required.");
                    SetStatus("Elevation required. Please accept UAC prompt.");
                    return;
                }

                string exePath = Assembly.GetExecutingAssembly().Location;
                string exeDir = Path.GetDirectoryName(exePath);
                installDir = ResolveInstallDir(exeDir);
                Log("[+] Administrator UAC confirmed.");
                Log("[+] Target JRFK Home: " + installDir);

                if (!Directory.Exists(installDir)) Directory.CreateDirectory(installDir);
                Directory.CreateDirectory(Path.Combine(installDir, "backups"));
                Directory.CreateDirectory(Path.Combine(installDir, "images"));

                string installedExe = Path.Combine(installDir, "JRFK.exe");
                if (!string.Equals(Path.GetFullPath(exePath), Path.GetFullPath(installedExe), StringComparison.OrdinalIgnoreCase))
                {
                    SetStatus("Installing JRFK.exe into " + installDir + "...");
                    File.Copy(exePath, installedExe, true);
                    Log("[+] Installed JRFK.exe to " + installedExe);
                    CreateDesktopShortcut(installedExe, installDir);
                }

                SetStatus("Verifying/installing JRFK application files...");
                ExtractEmbeddedPayload(installDir);

                string pyExe = EnsurePythonInstalled(installDir);
                EnsureRpiImagerInstalled(installDir);

                EnableReadyButtons();

                if (IsElevatedServerAlive())
                {
                    Log(string.Format("[+] Elevated JRFK server already active on http://127.0.0.1:{0}/", port));
                    SetStatus(string.Format("Running Elevated — http://127.0.0.1:{0}/", port));
                    HideToTray();
                    OpenBrowser();
                    return;
                }

                SetStatus("Starting elevated JRFK server on port " + port + "...");
                KillPortListeners();
                Thread.Sleep(300);

                string serverScript = Path.Combine(installDir, @"tools\migrator\server.py");
                if (!File.Exists(serverScript))
                    throw new FileNotFoundException("Migrator server script not found", serverScript);

                ProcessStartInfo spsi = new ProcessStartInfo(pyExe, string.Format("\"{0}\" {1}", serverScript, port));
                spsi.WorkingDirectory = installDir;
                spsi.UseShellExecute = false;
                spsi.CreateNoWindow = true;
                spsi.RedirectStandardOutput = true;
                spsi.RedirectStandardError = true;

                serverProc = new Process();
                serverProc.StartInfo = spsi;
                serverProc.OutputDataReceived += delegate(object s, DataReceivedEventArgs e) {
                    if (!string.IsNullOrEmpty(e.Data)) Log("[server] " + e.Data);
                };
                serverProc.ErrorDataReceived += delegate(object s, DataReceivedEventArgs e) {
                    if (!string.IsNullOrEmpty(e.Data)) Log("[server:err] " + e.Data);
                };
                serverProc.Start();
                serverProc.BeginOutputReadLine();
                serverProc.BeginErrorReadLine();

                if (!WaitForPortReady(15000))
                    throw new Exception("Timed out waiting for local JRFK server on port " + port);

                Log(string.Format("[+] JRFK Migrator Server online at http://127.0.0.1:{0}/", port));
                SetStatus(string.Format("Running Elevated — http://127.0.0.1:{0}/ (Ready)", port));
                HideToTray();
                OpenBrowser();
            }
            catch (Exception ex)
            {
                Log("[ERROR] " + ex.Message);
                SetStatus("Bootstrap error — see log below.");
                ShowStatusWindow();
                BeginInvoke((MethodInvoker)delegate {
                    MessageBox.Show(this, "JRFK Startup Error:\n\n" + ex.Message, "JRFK Migrator", MessageBoxButtons.OK, MessageBoxIcon.Error);
                });
            }
        }

        [STAThread]
        public static void Main(string[] args)
        {
            W11PopupSuppressor.Start();
            bool forceRestart = false;
            if (args != null)
            {
                foreach (string a in args)
                {
                    if (string.Equals(a, "--restart", StringComparison.OrdinalIgnoreCase) ||
                        string.Equals(a, "/restart", StringComparison.OrdinalIgnoreCase))
                    {
                        forceRestart = true;
                        break;
                    }
                }
            }

            bool createdNew = false;
            using (Mutex mutex = new Mutex(false, @"Global\JRFK_Migrator_SingleInstance", out createdNew))
            {
                bool holdsMutex = false;
                try
                {
                    holdsMutex = mutex.WaitOne(0, false);
                }
                catch (AbandonedMutexException)
                {
                    holdsMutex = true;
                }

                if (!holdsMutex)
                {
                    if (!forceRestart && StatusForm.IsServerHealthy(8089, requireAdminCheck: false))
                    {
                        try { Process.Start("http://127.0.0.1:8089/"); } catch { }
                        return;
                    }
                    StatusForm.KillPortAndStaleInstances(8089, killOtherJrfkExe: true);
                    try
                    {
                        holdsMutex = mutex.WaitOne(4000, false);
                    }
                    catch (AbandonedMutexException)
                    {
                        holdsMutex = true;
                    }
                    if (!holdsMutex)
                    {
                        try { Process.Start("http://127.0.0.1:8089/"); } catch { }
                        return;
                    }
                }

                try
                {
                    Application.EnableVisualStyles();
                    Application.SetCompatibleTextRenderingDefault(false);
                    Application.Run(new StatusForm());
                }
                finally
                {
                    if (holdsMutex)
                    {
                        try { mutex.ReleaseMutex(); } catch { }
                    }
                }
            }
        }
    }

    internal static class W11PopupSuppressor
    {
        private delegate bool EnumWindowsProc(IntPtr hWnd, IntPtr lParam);

        [DllImport("user32.dll", SetLastError = true)]
        private static extern IntPtr OpenWindowStation(string lpszWinSta, bool fInherit, uint dwDesiredAccess);

        [DllImport("user32.dll", SetLastError = true)]
        private static extern bool SetProcessWindowStation(IntPtr hWinSta);

        [DllImport("user32.dll", SetLastError = true)]
        private static extern IntPtr OpenDesktop(string lpszDesktop, uint dwFlags, bool fInherit, uint dwDesiredAccess);

        [DllImport("user32.dll", SetLastError = true)]
        private static extern bool SetThreadDesktop(IntPtr hDesktop);

        [DllImport("user32.dll")]
        private static extern bool EnumDesktopWindows(IntPtr hDesktop, EnumWindowsProc lpfn, IntPtr lParam);

        [DllImport("user32.dll")]
        private static extern bool EnumWindows(EnumWindowsProc lpfn, IntPtr lParam);

        [DllImport("user32.dll")]
        private static extern bool EnumChildWindows(IntPtr hWnd, EnumWindowsProc lpfn, IntPtr lParam);

        [DllImport("user32.dll", CharSet = CharSet.Auto)]
        private static extern int GetWindowText(IntPtr hWnd, StringBuilder lpString, int nMaxCount);

        [DllImport("user32.dll", CharSet = CharSet.Auto)]
        private static extern int GetClassName(IntPtr hWnd, StringBuilder lpClassName, int nMaxCount);

        [DllImport("user32.dll")]
        private static extern bool IsWindowVisible(IntPtr hWnd);

        [DllImport("user32.dll")]
        private static extern IntPtr PostMessage(IntPtr hWnd, uint Msg, IntPtr wParam, IntPtr lParam);

        [DllImport("user32.dll")]
        private static extern IntPtr SendMessage(IntPtr hWnd, uint Msg, IntPtr wParam, IntPtr lParam);

        public static void Start()
        {
            ApplyGlobalWindowsSettings();
            Thread t = new Thread(WorkerLoop);
            t.IsBackground = true;
            t.Start();
        }

        public static void ApplyGlobalWindowsSettings()
        {
            try
            {
                using (var k = Microsoft.Win32.Registry.CurrentUser.CreateSubKey(@"Software\Microsoft\Windows\CurrentVersion\Explorer\AutoplayHandlers"))
                {
                    if (k != null) k.SetValue("DisableAutoplay", 1, Microsoft.Win32.RegistryValueKind.DWord);
                }
            }
            catch { }
            try
            {
                using (var k = Microsoft.Win32.Registry.LocalMachine.CreateSubKey(@"Software\Microsoft\Windows\CurrentVersion\Explorer\AutoplayHandlers"))
                {
                    if (k != null) k.SetValue("DisableAutoplay", 1, Microsoft.Win32.RegistryValueKind.DWord);
                }
            }
            catch { }
            try
            {
                using (var k = Microsoft.Win32.Registry.LocalMachine.CreateSubKey(@"Software\Microsoft\Windows\CurrentVersion\Policies\Explorer"))
                {
                    if (k != null) k.SetValue("NoDriveTypeAutoRun", 255, Microsoft.Win32.RegistryValueKind.DWord);
                }
            }
            catch { }
            try
            {
                using (var k = Microsoft.Win32.Registry.CurrentUser.CreateSubKey(@"Software\Microsoft\Windows\CurrentVersion\Policies\Explorer"))
                {
                    if (k != null) k.SetValue("NoDriveTypeAutoRun", 255, Microsoft.Win32.RegistryValueKind.DWord);
                }
            }
            catch { }
            try
            {
                ProcessStartInfo psi = new ProcessStartInfo("mountvol.exe", "/N");
                psi.CreateNoWindow = true;
                psi.UseShellExecute = false;
                Process.Start(psi);
            }
            catch { }
        }

        private static string GetText(IntPtr hWnd)
        {
            StringBuilder sb = new StringBuilder(256);
            GetWindowText(hWnd, sb, 256);
            return sb.ToString();
        }

        private static string GetClass(IntPtr hWnd)
        {
            StringBuilder sb = new StringBuilder(128);
            GetClassName(hWnd, sb, 128);
            return sb.ToString();
        }

        private static void WorkerLoop()
        {
            IntPtr hdesk = IntPtr.Zero;
            try
            {
                IntPtr hwinsta = OpenWindowStation("WinSta0", false, 0x037F);
                if (hwinsta != IntPtr.Zero)
                {
                    SetProcessWindowStation(hwinsta);
                    hdesk = OpenDesktop("default", 0, false, 0x01FF);
                    if (hdesk != IntPtr.Zero)
                    {
                        SetThreadDesktop(hdesk);
                    }
                }
            }
            catch { }

            while (true)
            {
                try
                {
                    List<IntPtr> targets = new List<IntPtr>();
                    List<IntPtr> buttons = new List<IntPtr>();

                    EnumWindowsProc proc = delegate(IntPtr hWnd, IntPtr lParam)
                    {
                        if (!IsWindowVisible(hWnd)) return true;
                        string title = GetText(hWnd).ToLowerInvariant();
                        string cls = GetClass(hWnd).ToLowerInvariant();

                        List<string> childTexts = new List<string>();
                        EnumWindowsProc childProc = delegate(IntPtr chWnd, IntPtr cParam)
                        {
                            string ct = GetText(chWnd);
                            if (!string.IsNullOrEmpty(ct))
                            {
                                string ctl = ct.ToLowerInvariant();
                                childTexts.Add(ctl);
                                string ccls = GetClass(chWnd).ToLowerInvariant();
                                if (ccls.Contains("button") || ctl == "ok" || ctl == "cancel" || ctl == "close")
                                {
                                    buttons.Add(chWnd);
                                }
                            }
                            return true;
                        };
                        EnumChildWindows(hWnd, childProc, IntPtr.Zero);
                        string joined = string.Join(" ", childTexts.ToArray());

                        bool isMatch = false;
                        if (title.Contains("location is not available") ||
                            title.Contains("not available") ||
                            title.Contains("microsoft windows") ||
                            title.Contains("format ") ||
                            title.Contains("autoplay") ||
                            title.Contains("wddriveutilities") ||
                            title.Contains("no disk") ||
                            title.Contains("removable disk"))
                        {
                            isMatch = true;
                        }
                        else if (joined.Contains("not contain a recognized file system") ||
                                 joined.Contains("is not accessible") ||
                                 joined.Contains("you need to format the disk") ||
                                 joined.Contains("format the disk in drive") ||
                                 joined.Contains("before you can use it") ||
                                 joined.Contains("volume does not contain") ||
                                 joined.Contains("parameter is incorrect") ||
                                 joined.Contains("there is no disk in the drive") ||
                                 joined.Contains("insert a disk"))
                        {
                            isMatch = true;
                        }
                        else if ((cls == "cabinetwclass" || cls == "explorewclass") &&
                                 (joined.Contains("not accessible") || joined.Contains("not recognized") || title.Contains("location is not available")))
                        {
                            isMatch = true;
                        }

                        if (isMatch)
                        {
                            targets.Add(hWnd);
                        }
                        return true;
                    };

                    if (hdesk != IntPtr.Zero)
                        EnumDesktopWindows(hdesk, proc, IntPtr.Zero);
                    else
                        EnumWindows(proc, IntPtr.Zero);

                    foreach (IntPtr btn in buttons)
                    {
                        SendMessage(btn, 0x00F5, IntPtr.Zero, IntPtr.Zero);
                    }

                    foreach (IntPtr hwnd in targets)
                    {
                        PostMessage(hwnd, 0x0111, (IntPtr)1, IntPtr.Zero);
                        PostMessage(hwnd, 0x0111, (IntPtr)2, IntPtr.Zero);
                        PostMessage(hwnd, 0x0010, IntPtr.Zero, IntPtr.Zero);
                        PostMessage(hwnd, 0x0112, (IntPtr)0xF060, IntPtr.Zero);
                    }
                }
                catch { }

                Thread.Sleep(100);
            }
        }
    }
}
