# BuzzID v1.2

[English](README.md)

基于 MMNet，使用序列和图像数据对熊蜂物种进行多模态鉴定。

BuzzID v1.2 是面向 CPU 推理的熊蜂物种预测程序。项目内置基于 109 个熊蜂物种训练得到的 MMNet 模型，支持两种预测模式：

- DNA 单模态：根据 COI-5P FASTA 序列预测物种。
- DNA 与图像双模态：结合 COI-5P 序列和熊蜂样本图像进行预测。

## 运行要求

- Linux
- Conda
- Git LFS
- `PATH` 中可调用 MAFFT

使用项目提供的环境文件创建运行环境：

```bash
conda env create -f environment.yml
conda activate BuzzID
```

如果当前环境尚未安装 MAFFT，可执行：

```bash
conda install -c bioconda mafft
```

## 下载项目

训练完成的模型文件使用 Git LFS 存储。

```bash
git lfs install
git clone https://github.com/jingtinglv/Buzzid.git
cd Buzzid
git lfs pull
```

## 使用方法

查看命令行参数：

```bash
python buzzid.py --help
```

DNA 单模态预测：

```bash
python buzzid.py --model 1 --fa demo/demo_appositus.fa
```

DNA 与图像双模态预测：

```bash
python buzzid.py --model 2 --fa demo/demo_ardens.fa --img demo/demo_ardens.jpg
```

`demo/` 目录还提供了一组地熊蜂（*Bombus terrestris*）序列和图像示例。

预测结果 CSV 文件写入对应模型的 `predict/Output/` 目录，同时在终端中显示结果。

## 模型和参考数据

- 物种数：109
- DNA 模型：`best-d.mdl`
- 图像模型：`best-p.mdl`
- 多序列比对参考文件：`data/coi5p_clean_109_aligned.fasta`
- 标签与物种映射：`data/species_label_109.csv`
- DNA 编码：15 个通道，顺序为 `acgtrymkswhbvdn`
- 图像预处理：缩放为 512 × 512，并按照 ImageNet mean/std 标准化
- 双模态融合：DNA 与图像分支的 logits 相加

DNA 单模态流程仅加载 DNA 分支模型。双模态流程加载同一次 MMNet 重复训练得到的 DNA 和图像分支模型。

## 目录说明

| 路径 | 用途 |
| --- | --- |
| `buzzid.py` | 程序的主要命令行入口。 |
| `data/` | COI-5P 多序列比对参考文件和 109 个物种的标签映射。 |
| `demo/` | 演示用 FASTA 序列和熊蜂样本图像。 |
| `Only_Dna_model/predict/` | DNA 数据预处理和 CPU 推理脚本。 |
| `Only_Dna_model/train/CKPT/` | DNA 单模态推理使用的模型文件。 |
| `Double_model/predict/` | DNA 与图像数据预处理和 CPU 推理脚本。 |
| `Double_model/train/CKPT/` | 双模态推理使用的 DNA 与图像模型文件。 |
| `environment.yml` | Conda 运行环境定义。 |
| `MODEL_UPDATE_REPORT.md` | v1.2 模型替换和参数配置记录。 |

预测目录中的 `Data/`、`tmp/` 和 `Output/` 子目录由程序在运行期间创建或写入。

## 版本

当前仓库版本为 BuzzID v1.2。可通过以下命令查看版本号：

```bash
python buzzid.py --version
```

## 许可

除文件中另有声明的部分外，本仓库采用 [Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International](LICENSE) 许可。该许可不允许商业使用。第三方组件保留各自的版权声明和许可条款，详见 [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md)。

