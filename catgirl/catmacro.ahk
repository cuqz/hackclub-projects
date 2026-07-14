;; ============================================================
;;  CATMACRO — Cute AutoHotkey v2 Macro Suite
;;  Language: AutoHotkey v2 (download: autohotkey.com)
;;  Source:   https://github.com/AutoHotkey/AutoHotkey
;;  License:  GPL (official — no malware, open source since 2003)
;;
;;  HOW THIS WORKS:
;;  AutoHotkey reads this script and waits in the background.
;;  When you press a hotkey combo (like Win+C), it runs the
;;  associated command. All commands are listed below with
;;  full explanations. You can verify every single line.
;;
;;  TO RUN:
;;  1. Install AutoHotkey v2 from https://www.autohotkey.com/
;;  2. Right-click this file → "Run Script"
;;  3. A green "H" icon appears in your system tray
;;  4. Use the hotkeys below
;;
;;  TO EXIT:
;;  Right-click the green "H" in system tray → Exit
;; ============================================================
#Requires AutoHotkey v2.0  ;; tells Windows this is v2, not v1

;; ============================================================
;;  TEXT EXPANDER — type these shortcuts anywhere, they expand
;; ============================================================

;; Type "btw" + space/enter → expands to "by the way"
;; The :: at the start means "hotstring" — it watches what you type
::btw::by the way

;; Type "imo" → "in my opinion"
::imo::in my opinion

;; Type "idk" → "I don't know"
::idk::I don't know

;; Type "ttyl" → "talk to you later"
::ttyl::talk to you later

;; Type "brb" → "be right back"
::brb::be right back

;; Type "omw" → "on my way"
::omw::on my way

;; Type "addr" → your full address (change to yours)
;; ::addr::123 Main Street, City, State 12345

;; Type "email" → your email address (change to yours)
;; ::email::yourname@example.com

;; ============================================================
;;  HOTKEYS — Win + key combos
;; ============================================================

;; Win+C → opens Calculator
;; # means the Windows key, C is the key to press
#c::Run "calc.exe"

;; Win+N → opens Notepad
#n::Run "notepad.exe"

;; Win+T → opens the current date and time (types it for you)
#t::
{
    ;; Send the current date/time as keystrokes
    ;; A_Now gets the current timestamp
    ;; FormatTime converts it to a readable string
    currentTime := FormatTime(A_Now, "yyyy-MM-dd HH:mm")
    SendInput currentTime
}

;; Win+Q → quickly type a pre-written message
;; This opens an input box, you type a quick note,
;; and it gets inserted at the cursor position
#q::
{
    note := InputBox("What's on your mind?", "Quick Note")
    if note.Result = "OK"  ;; if they clicked OK, not Cancel
        SendInput note.Value
}

;; Win+W → close the active window (like Alt+F4 but with Win key)
#w::WinClose "A"   ;; "A" means "active window"

;; Win+D → open Downloads folder
#d::Run "explorer.exe C:\Users\WezaMwiwa\Downloads"

;; ============================================================
;;  WINDOW MANAGEMENT
;; ============================================================

;; Win+Up Arrow → maximize the active window
#Up::WinMaximize "A"

;; Win+Down Arrow → restore/minimize the active window
#Down::WinMinimize "A"

;; Win+Left/Right already handled by Windows natively.
;; Removing AHK override to avoid infinite loop.

;; ============================================================
;;  MOUSE SHORTCUTS
;; ============================================================

;; Middle-click on the desktop → show/hide hidden files
;; (This is a fun one — just to show AHK can do system stuff)
;; WARNING: Requires running as admin for full system access
#MButton::
{
    ;; Toggle hidden files visibility using regedit
    ;; HKCU = HKEY_CURRENT_USER (Windows registry)
    current := RegRead("HKCU\Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced", "Hidden")
    newValue := current = 1 ? 2 : 1
    RegWrite(newValue, "REG_DWORD", "HKCU\Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced", "Hidden")
    ;; Tell Windows to refresh (so the change takes effect immediately)
    Send "{F5}"
}

;; ============================================================
;;  SYSTEM TRAY MENU
;; ============================================================

;; Customize the tray menu that appears when you right-click
;; the green "H" icon
A_TrayMenu.Delete()  ;; remove default items
A_TrayMenu.Add("About CatMacro", AboutMsg)
A_TrayMenu.Add()     ;; separator line
A_TrayMenu.Add("Reload Script", ReloadScript)
A_TrayMenu.Add("Exit", ExitScript)

AboutMsg(*)
{
    MsgBox "CatMacro v1.0`n" 
        . "Safe AutoHotkey v2 macros`n"
        . "Every line is commented — verify before running.`n"
        . "GitHub: https://github.com/AutoHotkey/AutoHotkey"
}

ReloadScript(*)
{
    Reload  ;; reloads the script (applies changes)
}

ExitScript(*)
{
    ExitApp  ;; completely exits the script
}

;; ============================================================
;;  TRAY TIP — shows when the script starts
;; ============================================================

TrayTip "CatMacro loaded!", "Win+?, Win+T, text expanders active", "Iconi"

;; ============================================================
;;  END OF SCRIPT
;;  Every line shown above is safe and transparent.
;;  No network access. No file reading/writing (except registry
;;  for hidden files toggle). No data collection.
;;  Verified open-source: github.com/AutoHotkey/AutoHotkey
;; ============================================================
