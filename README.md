# Python Indian Flag 🇮🇳  

Python CLI to Create Indian Flag with Your Name 🇮🇳  

![Python Indian Flag](https://raw.githubusercontent.com/mskian/python-indian-flag/refs/heads/main/indian_flag.png "Python CLI to Create Indian Flag with Your Name 🇮🇳")  

## Installation and usage

- Download CLI

```sh
wget https://gist.githubusercontent.com/mskian/da865d836565c617973a33a42ce189e8/raw/flag.py
```

- install required packages

```sh
pip install pillow
```

```sh
chmod +x flag.py
```

```sh
python flag.py -h
```

```sh
python flag.py "Your Name"
```

- Execute without Download the CLI

```sh
curl -s https://gist.githubusercontent.com/mskian/da865d836565c617973a33a42ce189e8/raw/flag.py?nocache=$(date +%s) | python3 - "Your Name"
```

- Web View

```sh
python index.py
```

## Termux Support

Fix image File Opening issue

```sh
"termux content provider requires allow-external-apps property to be set true"
```

```sh
nano ~/.termux/termux.properties
```

- uncomment this line just remove `#`

```sh
allow-external-apps=true
```

## Sources and Credits

- CLI Concept: <https://gist.github.com/JayantGoel001/1f1a644a6a7c742b21decaad0916bb3e>
- Goolge Fonts
- Twitter Emoji

### LICENSE

MIT
