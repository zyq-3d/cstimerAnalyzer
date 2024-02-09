# cstimer analyzer

- 自己写的方便分析和留存cstimer成绩的脚本
- 想直接用的话可以下载release

## 安装

```shell
git clone https://github.com/ultralytics/yolov5  # clone
cd cstimerAnalyzer
# conda create -n cstimer python==3.7 # 虚拟环境
pip install -r requirements.txt  # 安装
```

## 使用

1. 将自己的成绩填入`WCA.txt`中；
2. 使用cstimer训练完成后，点击总还原区域，复制“详细时间”后的内容（效果见`test.txt`）；
3. 在根目录中创建`.txt`文件（命名随意，但不可以为`WCA.txt`），将内容复制到文件中；
4. 运行`cstimerAnalyzer.py`，等待完成：

```python
# conda activate cstimer # 虚拟环境
python cstimerAnalyzer.py
```

5. 运行完成后会生成分析图像，图像会被保存到`results`文件夹下，`.txt`文件则会被移动至`rawTXTs`文件夹下