# jarvis
full local open source voice assistent for COSMIC DE

## about

free local voice assistant for controlling a computer with the cosmic de

## whisper model setup

the whisper model files are split into parts due to github size limits. after cloning the repository, assemble the original model file by running this command in your terminal:

```bash
cat models/whisper/model.bin.part* > models/whisper/model.bin
```

after successful assembly, you can safely delete the .part* files to save space

## aliases and custom commands:

to add an alias (a custom name for an application) or a custom command (a bash command executed when a specific phrase or word is spoken), use this template:

`phrase:what jarvis receives`

then, add it to the `support_files/aliases.txt` or `support_files/custom_commands.txt` file, respectively

## note: 

the frontend was built using chatGPT
