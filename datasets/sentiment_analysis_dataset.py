import os

import matplotlib.pyplot as plt
import torch
from torch import nn
from d2l import torch as d2l

from datasets.machine_translation_dataset import truncate_pad
from utils.TextPreprocessing import tokenize, Vocab


def read_imdb(data_dir, is_train):
    """读取IMDb评论数据集文本序列和标签"""
    data, labels = [], []
    for label in ('pos', 'neg'):
        folder_name = os.path.join(data_dir,
                    'train' if is_train else 'test', label)
        for file in os.listdir(folder_name):
            with open(os.path.join(folder_name, file), 'rb') as f:
                review = f.read().decode('utf-8').replace('\n', '')
                data.append(review)
                labels.append(1 if label == 'pos' else 0)
    return data, labels

def load_data_imdb(batch_size, num_steps=500):
    """返回数据迭代器和IMDb评论数据集的词表"""
    data_dir = d2l.download_extract('aclImdb', 'aclImdb')
    train_data = read_imdb(data_dir, is_train=True)
    test_data = read_imdb(data_dir, is_train=False)
    train_tokens = tokenize(train_data[0], token='word')
    test_tokens = tokenize(test_data[0], token='word')
    vocab = Vocab(train_tokens, min_freq=5)
    train_features = torch.tensor([d2l.truncate_pad(
        vocab[line], num_steps, vocab['<pad>']) for line in train_tokens])
    test_features = torch.tensor([d2l.truncate_pad(
        vocab[line], num_steps, vocab['<pad>']) for line in test_tokens])
    train_iter = d2l.load_array((train_features, torch.tensor(train_data[1])),
                                batch_size)
    test_iter = d2l.load_array((test_features, torch.tensor(test_data[1])),
                               batch_size,
                               is_train=False)
    return train_iter, test_iter, vocab


if __name__ == "__main__":
    # read dataset
    d2l.DATA_HUB['aclImdb'] = (
        'http://ai.stanford.edu/~amaas/data/sentiment/aclImdb_v1.tar.gz',
        '01ada507287d82875905620988597833ad4e0903')
    data_dir = d2l.download_extract('aclImdb', 'aclImdb')

    train_data = read_imdb(data_dir, is_train=True)
    print('训练集数目：', len(train_data[0]))
    for x, y in zip(train_data[0][:3], train_data[1][:3]):
        print('标签：', y, 'review:', x[0:100])

    # clear dataset
    train_tokens = tokenize(train_data[0], token='word')
    vocab = Vocab(train_tokens, min_freq=5, reserved_tokens=['<pad>'])

    d2l.set_figsize()
    d2l.plt.xlabel('# tokens per review')
    d2l.plt.ylabel('count')
    d2l.plt.hist([len(line) for line in train_tokens], bins=range(0, 1000, 50))

    num_steps = 500  # 序列长度
    train_features = torch.tensor([truncate_pad(
        vocab[line], num_steps, vocab['<pad>']) for line in train_tokens])
    print(train_features.shape)

    # data_iter
    train_iter = d2l.load_array((train_features,
                                 torch.tensor(train_data[1])), 64)

    for X, y in train_iter:
        print('X:', X.shape, ', y:', y.shape)
        break
    print('小批量数目：', len(train_iter))











