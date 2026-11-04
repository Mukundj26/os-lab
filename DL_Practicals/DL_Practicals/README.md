# Deep Learning Practicals (Anaconda / Jupyter) - 12 practicals

## Setup (Anaconda Prompt)
```
conda create -n dl python=3.11 -y
conda activate dl
pip install -r requirements.txt
jupyter notebook
```
Open the notebooks in `notebooks/` and use **Kernel > Restart & Run All**. `py_scripts/` has the same code as plain
Python files (cells separated by `# %%`, which Spyder/VS Code also understand).

| # | Notebook | Dataset | Notes |
|---|---|---|---|
| 1 | dl01_mnist_backprop_mlp | MNIST | MLP vs Logistic Regression vs Decision Tree |
| 2 | dl02_iris_activation_functions | IRIS | Manual forward pass (random + trained weights), 5 activations |
| 3 | dl03_gradients_weight_init | Fashion-MNIST | Gradient norms, Xavier/He |
| 4 | dl04_regularization_normalization | Fashion-MNIST | Dropout, L1/L2, early stop, augmentation, BN vs LN |
| 5 | dl05_cnn_architectures_comparison | CIFAR-10 | Basic CNN, LeNet, AlexNet, VGG, ResNet, Inception, MobileNet styles: accuracy, params, MACs, time |
| 6 | dl06_cnn_cifar10_experiments | CIFAR-10 | Kernel/stride/padding/pooling, filters, feature maps |
| 7 | dl07_cnn_architectures_transfer_learning | CIFAR-10 | LeNet, AlexNet, VGG16, ResNet50, transfer learning |
| 8 | dl08_object_detection_voc | Pascal VOC | R-CNN and Fast R-CNN pipelines (Selective Search), SSD MobileNet, YOLOv8, images + video |
| 9 | dl09_unet_oxford_pets | Oxford-IIIT Pet | U-Net, IoU / Dice / pixel accuracy |
| 10 | dl10_stock_rnn | Yahoo Finance | 30-day window, RNN(50) |
| 11 | dl11_stock_gru_vs_rnn | Yahoo Finance | GRU vs RNN |
| 12 | dl12_mnist_rest_api | MNIST | Saves model, writes and tests Flask API; FastAPI version also included |

## Tips
* Datasets download automatically on first run (internet needed). Practicals 5, 7, 8 and 9 are the slowest; a GPU helps.
* To shorten run time, reduce `EPOCHS`, `N_TRAIN` (practicals 5, 7) or `N_IMAGES` (practical 8).
* Practical 5 had no description in the list, so it is a fair comparison of the main CNN architecture families
  trained under identical conditions.
* Practical 8: no standalone pre-trained R-CNN / Fast R-CNN exists, so both pipelines are implemented in their original
  style (per-region CNN vs shared CNN + RoI pooling with Selective Search) using the COCO-pretrained Faster R-CNN
  weights. Install `opencv-contrib-python`. Models are COCO-trained and mapped to VOC classes.
* Run practical 12 first, then start the API with `python app.py` and test with
  `curl -X POST -F "image=@digit.png" http://127.0.0.1:5000/predict`.
* Results (accuracy, times) differ between machines; write conclusions from your own outputs.
