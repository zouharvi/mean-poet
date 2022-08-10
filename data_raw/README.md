## Adding more poems

Each poem and its translations are placed in a separate TOML file in the `data_raw` folder with the filename `{last_name}_{number}.toml`.
The reason for using TOML is that it's human-readable and still easy to work with.
Use this template or take a look at existing examples, such as [`rilke_0.toml`](rilke_0.toml).
Copyright should not be an issue since we're not scrapping the whole websites but choosing specific poems (and are attributing them to the original authors and translators).

Try to preserve the formatting, especially the stanza ("paragraph") separation.

```
title = "<<poem title in the source language>>"
author = "<<author of the poem>>"
lang = "<<language code, such as `de`>>"
year = <<year of original poem publication>>
poem = """
<<multiline poem text in source language>>
"""

# translations into English follow with struct name [translation-X]

[translation-1]
title = "<<title in English>>"
translator = "<<translator name>>"
# most commonly `professional` but if you translate yourself then `amateur`
translator_level = "<<translator profficiency>>"
poem = """
<<multiline poem text in English>>
"""

# add more translations if available
[translation-2]
# ...
```

## Resources

- https://en.wikisource.org/wiki/Modern_Czech_Poetry
- https://www.lyrikline.org/en/
- TODO