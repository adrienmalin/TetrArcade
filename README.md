# TetrArcade

Tetris clone made with Python and Arcade graphic library

![Screenshot](https://malingrey.fr/images/fMd4EseZ/VtwJIMyQ.png)

## Requirements

* [Python 3.6 or later](https://www.python.org/)
* [FFmpeg 4](http://ubuntuhandbook.org/index.php/2019/08/install-ffmpeg-4-2-ubuntu-18-04/)

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
