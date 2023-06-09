import math

import matplotlib.pyplot as plt
import torch
from torch import nn
from d2l import torch as d2l

from attention.multihead_attention import MultiHeadAttention

class PositionalEncoding(nn.Module):
    """位置编码"""
    """
    X, P shape (n, d);
    theta = i / 10000^(2j/d)
    P[i, 2j] = sin(theta), P[i, 2j + 1] = cos(theta)
    """
    def __init__(self, num_hiddens, dropout, max_len=1000):
        super().__init__()
        self.dropout = nn.Dropout(dropout)
        # 创建一个足够长的P
        self.P = torch.zeros((1, max_len, num_hiddens))
        X = torch.arange(max_len, dtype=torch.float32).reshape(-1, 1)
        Y = torch.pow(10000, torch.arange(0, num_hiddens, 2, dtype=torch.float32) / num_hiddens)
        theta = X / Y
        self.P[:, :, 0::2] = torch.sin(theta)
        self.P[:, :, 1::2] = torch.cos(theta)

    def forward(self, X, is_decoder=False, i=-1):
        # when testing, add p(i), i is the index of X in decoder seq
        if not self.training and is_decoder:
            X = X + self.P[:, i, :].to(X.device)
        else:
            X = X + self.P[:, :X.shape[1], :].to(X.device)
        return self.dropout(X)



if __name__ == "__main__":
    num_hiddens, num_heads = 100, 5
    attention = MultiHeadAttention(num_hiddens, num_hiddens, num_hiddens,
                                       num_hiddens, num_heads, 0.5)
    attention.eval()
    batch_size, num_queries, valid_lens = 2, 4, torch.tensor([3, 2])
    X = torch.ones((batch_size, num_queries, num_hiddens))
    print(attention(X, X, X, valid_lens).shape)

    # test pos_encoding
    encoding_dim, num_steps = 32, 60
    pos_encoding = PositionalEncoding(encoding_dim, 0)
    pos_encoding.eval()
    X = pos_encoding(torch.zeros((1, num_steps, encoding_dim)))
    P = pos_encoding.P[:, :X.shape[1], :]
    d2l.plot(torch.arange(num_steps), P[0, :, 6:10].T, xlabel='Row (position)',
             figsize=(6, 2.5), legend=["Col %d" % d for d in torch.arange(6, 10)])
    plt.show()









