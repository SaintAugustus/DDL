import torch
from torch import nn
from d2l import torch as d2l

from utils.Accumulator import Accumulator
from utils.Optim import accuracy
from utils.Timer import Timer

net = nn.Sequential(
    nn.Conv2d(1, 6, kernel_size=5, padding=2), nn.Sigmoid(),
    nn.AvgPool2d(kernel_size=2, stride=2),
    nn.Conv2d(6, 16, kernel_size=5), nn.Sigmoid(),
    nn.AvgPool2d(kernel_size=2, stride=2),
    nn.Flatten(),
    nn.Linear(16 * 5 * 5, 120), nn.Sigmoid(),
    nn.Linear(120, 84), nn.Sigmoid(),
    nn.Linear(84, 10)
)

def test_net():
    X = torch.rand(size=(1, 1, 28, 28), dtype=torch.float32)
    for layer in net:
        X = layer(X)
        print(layer.__class__.__name__, "output shape: \t", X.shape)

def evaluate_accuracy_gpu(net, data_iter, device=None):
    if isinstance(net, nn.Module):
        net.eval()
        if not device:
            device = next(iter(net.parameters())).device
    metric = Accumulator(2)
    with torch.no_grad():
        for X, y in data_iter:
            if isinstance(X, list):
                X = [x.to(device) for x in X]
            else:
                X = X.to(device)
            y = y.to(device)
            metric.add(accuracy(net(X).cpu(), y.cpu()), y.numel())
    return metric[0] / metric[1]


def train_ch6(net, train_iter, valid_iter, num_epochs, lr, device):
    def init_weights(m):
        if type(m) == nn.Linear or type(m) == nn.Conv2d:
            nn.init.xavier_uniform_(m.weight)
            nn.init.zeros_(m.bias)
    net.apply(init_weights)
    print("training on ", device)
    net.to(device)
    optimizer = torch.optim.SGD(net.parameters(), lr=lr)
    loss = nn.CrossEntropyLoss()
    timer = Timer()

    for epoch in range(num_epochs):
        metric = Accumulator(3)   # loss, accum accuracy, examples
        net.train()
        for i, (X, y) in enumerate(train_iter):
            timer.start()
            optimizer.zero_grad()
            X, y = X.to(device), y.to(device)
            y_hat = net(X)
            l = loss(y_hat, y)
            l.backward()
            optimizer.step()
            with torch.no_grad():
                metric.add(l * X.shape[0], accuracy(y_hat.cpu(), y.cpu()), X.shape[0])
            timer.stop()

            train_loss = metric[0] / metric[2]
            train_acc = metric[1] / metric[2]

        valid_acc = evaluate_accuracy_gpu(net, valid_iter, device)
        if epoch % 2 == 0:
            print(f'epoch {epoch}, loss {train_loss:.3f}, train acc {train_acc:.3f}, '
                  f'test acc {valid_acc:.3f}')


def main():
    batch_size = 256
    train_iter, test_iter = d2l.load_data_fashion_mnist(batch_size=batch_size)
    lr, num_epochs = 0.9, 10
    device = torch.device("mps")
    train_ch6(net, train_iter, test_iter, num_epochs, lr, device)

if __name__ == "__main__":
    test_net()
    main()































