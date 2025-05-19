# Links to download dictionaries for GoldenDict
`GoldenDict_ng`/`GoldenDict` supports various [dictionary formats](https://xiaoyifang.github.io/goldendict-ng/dictformats/), including StarDict, Babylon, and others.
    - Babylon .BGL files, complete with images and resources
    - StarDict: each folder contain these files (.ifo/.dict./.idx/.syn)
    - Dictd: (.index/.dict(.dz))
    - ABBYY Lingvo .dsl source files, together with abbreviations. The files can be optionally compressed with dictzip. Dictionary resources can be packed together into a .zip file.
    - ABBYY Lingvo .lsa/.dat audio archives

> In short:
- Google Detect-Vi: ` trans -e google -t vi -show-original y -show-original-phonetics n -show-translation y -no-ansi -show-translation-phonetics n -show-prompt-message n -show-languages n -show-original-dictionary n -show-dictionary n -show-alternatives n %GDWORD% `
- Google Vi-En: ` trans -e google -s vi -t en -show-original y -show-original-phonetics n -show-translation y -no-ansi -show-translation-phonetics n -show-prompt-message n -show-languages n -show-original-dictionary n -show-dictionary n -show-alternatives n %GDWORD% `
- Google En Voice: `trans -speak -e google -brief -no-translate %GDWORD% `
- For En-En: `Longman-Contemporary-English-5th-New + Sounds` for offline dictionary
- Use more `wikipedia` for online dictionary
- Use starDict for `Vi-En` and `En-Vi` dictionaries

## Setting
`Edit` > `Preferences`:
- `Scan Popup` > `Start with scan popup turned on` + `Show scan flag when word is selected`

## Set dictionaries in `GoldenDict`:
`Edit` > `Dictionaries` > `Sources`
- `Files`: to set offline dictionaries
- `Sound Dirs`: to set sound files for offline usage.
- `Wikipedia`: use `https://en.wikipedia.org/wiki/%GDWORD%` to search for words in Wikipedia
- `Websites`: to set online dictionaries
- `Program`: to use command line programs to search for words, e.g., use Google Translate to translate long texts,

### 1. Offline dictionaries:
- [Collection *.bgl For En](https://drive.google.com/drive/u/0/folders/0BzrQwK2v03aKWjlsQ3NsaWJKalU?resourcekey=0-DtgqOJiVFSDI231ugoQgiQ)
- [Longman-Contemporary-English-5th-New + Sounds](https://elvand.com/goldendict/)
- [gitrepo for Vi-En](https://github.com/dynamotn/stardict-vi)

To use:
    - En-En: Use *Longman-Contemporary-English-5th-New* is enough. *Oxford Dictionary 2nd* is too big, not efficient.

### 2. Use Online dictionaries
`Edit` > `Dictionaries` > `Sources`

1. dictionary Websites
    - Longman En-En (should use Longman Offline for better performance):
        - Address: ` https://www.ldoceonline.com/dictionary/%GDWORD% `
        - Must uncheck `as link`
    - Cambridge En-Vi:
        - Address: ` https://dictionary.cambridge.org/dictionary/english-vietnamese/%GDWORD% `

2. Translate long texts: this use [translate-shell](https://github.com/soimort/translate-shell)
    - Google Translate (Type: `Plain Text`):
        - Command En-Vi: ` trans -e google -s en -t vi -show-original y -show-original-phonetics n -show-translation y -no-ansi -show-translation-phonetics n -show-prompt-message n -show-languages y -show-original-dictionary n -show-dictionary n -show-alternatives n %GDWORD% `
        - Command Auto-Vi: ` trans -e google -t vi -show-original y -show-original-phonetics n -show-translation y -no-ansi -show-translation-phonetics n -show-prompt-message n -show-languages y -show-original-dictionary n -show-dictionary n -show-alternatives n %GDWORD% `
    - Google Audio (Type: `Audio`):
        - Command: `trans -e google -brief -no-translate -speak %GDWORD% ` (without `-brief` it will speak automatically)
