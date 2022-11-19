# hands_dl

## 安装环境要求

需要安装 anaconda 或 miniconda 来进行环境管理，安装方式可参考链接：

https://docs.conda.io/en/latest/miniconda.html

## 安装过程

解压源代码，在源代码目录下，通过 conda 根据 environment.yaml 安装环境：

> 如果仅仅想测试已训练模型的效果，通过 environment.yaml 安装依赖即可；如果想自行训练模型且拥有支持 cuda 的设备，请先下载安装和本项目 pytorch 版本对应的 cuda 版本（11.5），然后使用 environment_cuda.yaml 安装 python 依赖，训练模型见训练章节

```sh
conda env create -f environment.yaml
```

第二步，激活conda，进入conda环境：

```sh
conda activate hands_dl
```

## 测试和使用

运行 `test_framework.py` 或者 `test_single.py` 来分别尝试连续预测（使用滑动窗口）或者录入后预测（按 n 来开始或者结束录入）

若要在其他项目接入使用，请根据上述两个 py 文件学习调用接口，本项目的核心模块为 `data/HandTrackingModule.py` 和 `lstm_model.py`

## 训练

请使用视频流/图像流数据集且确保数据带有标签和帧范围，类似于 [IPN Hand 数据集](https://gibranbenitez.github.io/IPN_Hand/) 的 `annotation/Annot_List.txt`，然后编写预处理脚本（类似于本项目的 `data/ipn_hand.py` 生成特征向量和标签供模型训练

本项目提供了 3 个 Jupyter Notebook 供不同平台训练使用

## 致谢

+ PyTorch
+ Mediapipe
+ IPN Hand dataset