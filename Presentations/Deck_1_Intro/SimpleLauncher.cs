using System;
using System.Diagnostics;
using System.IO;

class Program
{
    [STAThread]
    static void Main()
    {
        string baseDir = AppDomain.CurrentDomain.BaseDirectory;
        string localFile = Path.Combine(baseDir, "preview.html");

        // If local preview.html exists right next to the exe, launch it; otherwise launch GitHub Pages
        string target = File.Exists(localFile)
            ? localFile
            : "https://jbirdlebough1.github.io/JRFKTools/deck1/preview.html";

        try
        {
            Process.Start(new ProcessStartInfo(target) { UseShellExecute = true });
        }
        catch
        {
            // Fallback for older shell configurations
            Process.Start("cmd.exe", "/c start \"\" \"" + target + "\"");
        }
    }
}
