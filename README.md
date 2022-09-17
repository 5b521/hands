# hands

## 安装环境要求

需要安装 anaconda 或 miniconda 来进行环境管理，安装方式可参考链接：

https://docs.conda.io/en/latest/miniconda.html

## 安装过程

第一步，解压源代码，在源代码目录下，通过conda安装 3.7 版本的 python：

```sh
conda create -n hands python=3.7
```

第二步，激活conda，进入conda环境：

```sh
conda activate hands
```

第三步，安装项目依赖项：

```sh
pip install -r requirements.txt
```

## 录入手势

在使用运行该项目之前，需要录入使用用户的手势，以获得更好的精准性。（也可以不录入，但是精准性会差一点）。

第一步，进入手势录入目录：

```sh
cd .\features_record\
```

第二步，通过取消注释 `features_record\hand_features_record.py` 的文件尾代码，选择需要录入的手势：

第三步，运行代码，开始录制：

```sh
python .\hand_features_record.py
```

第四步，摆出你要录制的手势，例如这里录制鼠标识别手指就需要将食指伸出与其他手指合拢，确认手势正确之后，按下空格键，会显示如下界面，然后按下 Q 键即可保存：


第五步，同理录制其他手势即可。

## 应用场景

鼠标控制，通过食指和中指的配合来进行鼠标控制。单独伸出食指，可以进行鼠标的移动；食指中指快速合拢张开，即为鼠标点击；食指中指合拢并移动，可以进行拖动。

文档翻页，将手掌的上下左右移动映射到对应的按键，进而实现文档翻页和视频快进等功能。

音量控制，通过对拇指和食指之间距离的识别，映射到对应的音量大小。
