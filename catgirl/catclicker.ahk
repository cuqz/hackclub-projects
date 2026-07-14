;; ============================================================
;;  CATCLICKER — AutoHotkey v2 Auto-Clicker & Macro Recorder
;;  Language: AutoHotkey v2 (download: autohotkey.com)
;;  Source:   https://github.com/AutoHotkey/AutoHotkey
;;  License:  GPL
;;
;;  WHAT THIS DOES:
;;  - Auto-clicker: clicks repeatedly at your cursor position
;;  - Click recorder: records clicks and replays them
;;  - All hotkeys shown below. Every line is transparent.
;;
;;  TO RUN:
;;  1. Install AutoHotkey v2 from autohotkey.com
;;  2. Right-click this file → "Run Script"
;;  3. Use hotkeys below
;;  4. Green "H" in tray → right-click → Exit to stop
;;
;;  SAFETY: No network. No file access. No data collection.
;;  Just mouse clicks and keystrokes controlled by YOU.
;; ============================================================
#Requires AutoHotkey v2.0
#SingleInstance Force   ;; only one copy of this script at a time

;; ============================================================
;;  AUTO-CLICKER — clicks repeatedly while you hold a key
;; ============================================================

;; F1 = toggle auto-clicker ON/OFF
;; When ON, it clicks 10 times per second at your mouse cursor
F1::
{
    global autoClicking := !autoClicking
    if autoClicking {
        TrayTip "Auto-clicker", "ON - F1 to stop", "Iconi"
        SetTimer(AutoClick, 100)  ;; run AutoClick every 100ms (10 clicks/sec)
    } else {
        TrayTip "Auto-clicker", "OFF", "Iconi"
        SetTimer(AutoClick, 0)    ;; stop the timer
    }
}

AutoClick()
{
    Click  ;; clicks at current mouse position
}

;; ============================================================
;;  CLICK RECORDER — record mouse clicks and replay them
;; ============================================================

;; F2 = start/stop recording clicks
;; Press F2, then click around. Press F2 again to stop.
;; Press F3 to replay all recorded clicks.

F2::
{
    global recording := !recording
    if recording {
        global recordedClicks := []     ;; empty the list
        TrayTip "Click Recorder", "Recording... F2 to stop", "Iconi"
    } else {
        count := recordedClicks.Length
        TrayTip "Click Recorder", "Recorded " count " clicks. F3 to play.", "Iconi"
    }
}

;; This fires on every mouse click — records the position
;; ~ before the hotkey means "use the native function too"
~LButton::
{
    global recording, recordedClicks
    if recording {
        MouseGetPos(&x, &y)            ;; get cursor X,Y
        recordedClicks.Push({x: x, y: y})  ;; save it
    }
}

;; F3 = replay all recorded clicks
F3::
{
    global recordedClicks
    if recordedClicks.Length = 0 {
        TrayTip "Click Recorder", "Nothing recorded yet!", "Iconi"
        return
    }
    
    TrayTip "Click Recorder", "Replaying " recordedClicks.Length " clicks...", "Iconi"
    
    ;; Loop through each recorded click and replay it
    for index, pos in recordedClicks {
        MouseMove(pos.x, pos.y, 5)     ;; move to the position smoothly
        Sleep 50                       ;; wait 50ms
        Click                          ;; click
        Sleep 100                      ;; wait 100ms between clicks
    }
    
    TrayTip "Click Recorder", "Replay done!", "Iconi"
}

;; ============================================================
;;  SPAM CLICKER — clicks rapidly while you hold a hotkey
;; ============================================================

;; Hold F4 to spam-click (100 clicks/second while held)
;; Release F4 to stop
F4::
{
    global spamClicking := true
    SetTimer(SpamClick, 10)  ;; every 10ms = 100 clicks/sec
}

F4 Up::
{
    global spamClicking := false
    SetTimer(SpamClick, 0)
}

SpamClick()
{
    Click
}

;; ============================================================
;;  QUICK MACROS — useful click patterns
;; ============================================================

;; F5 = double-click at current position
F5::
{
    Click 2  ;; Click 2 = double-click
}

;; F6 = click 5 times (for farming/grinding in games)
F6::
{
    Loop 5 {
        Click
        Sleep 50
    }
}

;; F7 = click this exact position on your screen
;; Change the 960,540 to whatever coordinates you want
;; To find coordinates: run the script, press F8, move mouse
F7::
{
    Click 960, 540  ;; clicks at center of a 1920x1080 screen
}

;; F8 = show current mouse position (in a tooltip)
F8::
{
    MouseGetPos(&x, &y)
    ToolTip "X: " x "  Y: " y
    Sleep 2000
    ToolTip  ;; hide the tooltip after 2 seconds
}

;; ============================================================
;;  KEYBOARD MACROS
;; ============================================================

;; Win+Y = type "yes" and press Enter (useful for confirmations)
#y::
{
    Send "yes{Enter}"
}

;; Win+Z = type "no" and press Enter
#z::
{
    Send "no{Enter}"
}

;; Win+X = type current date in short format
#x::
{
    Send FormatTime(A_Now, "yyyy-MM-dd")
}

;; ============================================================
;;  STATUS DISPLAY
;; ============================================================

;; Win+S = show all active macro status
#s::
{
    global autoClicking, recording, recordedClicks
    msg := "Auto-clicker: " (autoClicking ? "ON" : "OFF") "`n"
        . "Recording: " (recording ? "ON" : "OFF") "`n"
        . "Recorded clicks: " (recordedClicks ? recordedClicks.Length : 0)
    MsgBox msg, "CatClicker Status"
}

;; ============================================================
;;  SYSTEM TRAY MENU
;; ============================================================

A_TrayMenu.Delete()
A_TrayMenu.Add("Status", ShowStatus)
A_TrayMenu.Add()
A_TrayMenu.Add("Reload", (*) => Reload())
A_TrayMenu.Add("Exit", (*) => ExitApp())

ShowStatus(*)
{
    Send "#s"  ;; reuse the Win+S hotkey
}

;; ============================================================
;;  STARTUP TIP
;; ============================================================

TrayTip "CatClicker loaded!",
    "F1=Auto-click  F2=Record  F3=Replay  F4=Spam  F8=Show pos",
    "Iconi"

;; ============================================================
;;  END — Safe, transparent, open-source.
;;  Source: https://github.com/AutoHotkey/AutoHotkey
;;  Verifiable: every single line is above.
;;  No network. No data. No malware.
;; ============================================================
