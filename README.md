# TetrArcade

Tetris clone made with Python and Arcade graphic library

![Screenshot](https://malingrey.fr/images/fMd4EseZ/VtwJIMyQ.png)

## Requirements

* [Python](https://www.python.org/) 3.6 or later

## Install

```shell
git clone https://git.malingrey.fr/adrien/TetrArcade.git
cd TetrArcade
python -m pip install -r requirements.txt
```

## Play

```shell
python tetrarcade.py
```

## Settings

* Windows: Edit `%appdata%\Tetrarcade\TetrArcade.ini`
* Linux: Edit `~/.local/share/Tetrarcade/TetrArcade.ini`

Use key name from [arcade.key package](http://arcade.academy/arcade.key.html).

## Build

```shell
python -m pip install -r build-requirements.txt
python setup.py bdist
```
