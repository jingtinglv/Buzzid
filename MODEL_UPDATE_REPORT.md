# BuzzID v1.2 Lite CPU 模型更新报告

更新日期：2026-10-22

## 更新目标

在保持 BuzzID v1.2 Lite CPU 命令行接口和程序目录结构不变的前提下，将旧分类模型更新为 datasets-109 训练得到的 repeat7 最佳模型，并同步更新类别数、物种标签映射、多序列比对参考文件和演示数据。

## 模型替换

双模态模型使用：

- DNA 权重：`Double_model/train/CKPT/best-d.mdl`
- 图像权重：`Double_model/train/CKPT/best-p.mdl`

单模态模型使用：

- DNA 权重：`Only_Dna_model/train/CKPT/best-d.mdl`

上述权重来自：

- `runs_datasets109_main10x_earlystop/repeat7/best-d.mdl`
- `runs_datasets109_main10x_earlystop/repeat7/best-p.mdl`

repeat7 的最佳 epoch 为 34，保存的双模态测试准确率为 0.9908256880733946。单模态按照部署要求直接使用同一组模型中的 DNA 分支权重。

## 修改内容

1. 分类输出数由旧模型的 185 类或 245 类统一改为 109 类。
2. CPU 双模态和单模态预测脚本改为加载 repeat7 权重。
3. 目录内两个 GPU 辅助预测脚本同步更新类别数、映射和权重路径，CPU 默认流程不调用这两个脚本。
4. 物种标签映射替换为 `data/species_label_109.csv`，内容由 `109_pair.csv` 中的 `name` 和 `label` 一一生成，标签范围为 0–108。
5. 单模态和双模态的 MAFFT 参考文件统一为 `data/coi5p_clean_109_aligned.fasta`。
6. 旧的 185/245 类权重、参考比对、标签映射和演示文件已移除。
7. 演示数据替换为 datasets-109 及 repeat7 测试划分中的样本：
   - 单模态：`demo/demo_appositus.fa`
   - 双模态：`demo/demo_ardens.fa` 和 `demo/demo_ardens.jpg`
8. 程序版本显示统一为 1.2，帮助信息中的演示命令同步更新。

## 保留内容

- `buzzid.py` 的 `--model 1/2`、`--fa`、`--img` 参数及调用方式保持不变。
- ResNet-50、CBAM 和双模态 logits 相加的网络与融合方式保持不变。
- DNA 使用 15 通道编码，通道顺序为 `acgtrymkswhbvdn`，比对缺口使用全零向量。
- 图像仍缩放为 512×512，并使用 ImageNet mean/std 标准化。
- CPU 权重加载、DataParallel 前缀处理、LMDB 中间数据流程和输出 CSV 格式保持不变。
- batch size 20、learning rate 1e-4、num_workers 0 等原预测脚本中的记录参数保持不变。
- `environment.yml` 保持不变，现有 BuzzID 环境可直接运行 CPU 预测。

## 文件一致性

- 交付目录中的两个 `best-d.mdl` 与 repeat7 源 DNA 权重 SHA-256 一致：`06d369e03031f85520c0d8ccf15a6134267d0bccb5c4f4847735a860eba934c0`
- 交付目录中的 `best-p.mdl` 与 repeat7 源图像权重 SHA-256 一致：`15bd74600b2b38967bce655982b3ee70d91511a8dcc4af394d07016850f1d1b4`
- 交付目录中的多序列比对参考文件与 datasets-109 源文件 SHA-256 一致：`8b293209d76ae9d99a42bdee034ba3126dd4f71f010e9ee0a46088ec1b44de58`

## 运行检查

单模态命令：

```bash
python buzzid.py --model 1 --fa demo/demo_appositus.fa
```

结果：`Bombus_appositus`，置信度 0.9459。

双模态命令：

```bash
python buzzid.py --model 2 --fa demo/demo_ardens.fa --img demo/demo_ardens.jpg
```

结果：`Bombus_ardens`，置信度 0.9990；DNA contribution 0.5369，image contribution 0.4631。
