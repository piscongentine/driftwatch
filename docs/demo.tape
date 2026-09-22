# Records docs/assets/demo.gif with VHS (https://github.com/charmbracelet/vhs).
# VHS needs ttyd and ffmpeg. Easiest: run it from its Docker image, in a folder where `make setup` has been done
# (this file was recorded that way). Or install VHS, activate the virtualenv, and from the repo root run:
#   vhs docs/demo.tape
# Each command waits for its real last line of output, so the recording never depends on how fast your machine is.
Output docs/assets/demo.gif

Set Shell "bash"
Set FontSize 15
Set Width 1200
Set Height 760
Set Padding 24
Set Framerate 24
Set Theme "Catppuccin Mocha"
Set TypingSpeed 45ms

Type "make data" Enter
Wait+Screen@60s /wrote/
Sleep 3s

Type "make train" Enter
Wait+Screen@120s /reference:/
Sleep 5s

Type "clear" Enter
Type "make live" Enter
Wait+Screen@120s /live_log/
Sleep 4s

Type "clear" Enter
Type "make drift" Enter
Wait+Screen@120s /alert\(s\)/
Sleep 8s
