# ♡ my diary ♡

a personal diary application built with python and tkinter, designed to be cute, customizable, and functional.

## features

- **daily entries**: write thoughts for any day using the built-in calendar navigation.
- **rich text editor**: format your text with **bold**, *italic*, <u>underline</u>, custom colors. includes an emoji picker (kind of shit atm).
- **drawing of the day**: a full-featured drawing tool, can open them up in-program but also saves drawings locally too.
  - layer support (add, remove, move layers).
  - tools: brush, eraser, fill bucket.
  - shapes: line, rectangle, oval, star, heart.
  - adjustable opacity and brush size.
- **image of the day**: upload a photo to remember the day by.
- **health tracker**: track your daily status (healthy eating, exercise, etc.) which highlights the calendar day.
- **themes**: choose a UI-color theme.

## how to run

### using the executable
if you have the `diary.exe` file, simply double-click it to launch the application. it's currently unsigned so your computer may treat it as malware lol, sorry.

### from source
1. ensure you have python installed.
2. install the required dependency:
   ```bash
   pip install pillow
   ```
   *(note: `tkinter` is usually included with python)*
3. run the application:
   ```bash
   python diary.py
   ```

## data
- your entries are saved in `entries/diary_data.json`.
- drawings are saved in the `drawings/` folder.
- images are stored in the `images/` folder.

## planned features

- currently the "mood tracker" only tracks health, but id like to track actual moods (happy, sad, anxious, etc) as well.
- i want to let users manage what color the days change for different moods (for some people happy might be orange, yellow, pink, etc)
- for the health stats that do currently exist - i want to add more details. weight/bmi tracking, weight lifting stats, etc?
- the text color changer does correctly apply changes when text is selected, but no selected color is maintained.
