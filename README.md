# jarvis
full local open source voice assistent for COSMIC DE

## about

free local voice assistant for controlling a computer with the cosmic de

## whisper model setup

the whisper model files are split into parts due to github size limits. after cloning the repository, assemble the original model file by running this command in your terminal:

```bash
cat models/whisper/model.bin.part* > models/whisper/model.bin
```

after successful assembly, you can safely delete the .part* files to save space.
EOF
