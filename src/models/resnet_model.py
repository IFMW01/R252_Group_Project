import json
import torch.nn as nn
import torch.nn.functional as F

class BasicBlock(nn.Module):
    expansion = 1

    def __init__(self, in_planes, planes, stride=1, dropout=0.0):
        super(BasicBlock, self).__init__()
        self.conv1 = nn.Conv2d(in_planes, planes, kernel_size=3, stride=stride, padding=1, bias=False)
        self.bn1   = nn.BatchNorm2d(planes)
        self.conv2 = nn.Conv2d(planes, planes, kernel_size=3, stride=1, padding=1, bias=False)
        self.bn2   = nn.BatchNorm2d(planes)
        if dropout>0.0:
            self.dropout =nn.Dropout(dropout)
        else:
            self.dropout = None

        self.shortcut = nn.Sequential()
        if stride != 1 or in_planes != self.expansion*planes:
            self.shortcut = nn.Sequential(
                nn.Conv2d(in_planes, self.expansion*planes, kernel_size=1, stride=stride, bias=False),
                nn.BatchNorm2d(self.expansion*planes)
            )

    def forward(self, x, return_feat=False):
        out = F.relu(self.bn1(self.conv1(x)))
        if self.dropout is not None:
            out = self.dropout(out)
        out = self.bn2(self.conv2(out))
        out += self.shortcut(x)
        out = F.relu(out)
        if self.dropout is not None:
            out = self.dropout(out)
        return out
    
class ResNet_cifar(nn.Module):
    def __init__(self, block, num_blocks, num_classes,dropout=0.0):
        super(ResNet_cifar, self).__init__()
        self.in_planes = 16

        self.conv1  = nn.Conv2d(3, 16, kernel_size=3, stride=1, padding=1, bias=False)
        self.bn1    = nn.BatchNorm2d(16)
        self.layer1 = self._make_layer(block, 16, num_blocks[0],dropout, stride=1)
        self.layer2 = self._make_layer(block, 32, num_blocks[1],dropout, stride=2)
        self.layer3 = self._make_layer(block, 64, num_blocks[2],dropout, stride=2)
        self.classifier = nn.Linear(64*block.expansion, num_classes)
        if dropout>0.0:
            self.dropout =nn.Dropout(dropout)
        else:
            self.dropout = None

    def _make_layer(self, block, planes, num_blocks,dropout,stride):
        strides = [stride] + [1]*(num_blocks-1)
        layers = []
        for stride in strides:
            layers.append(block(self.in_planes, planes, stride,dropout))
            self.in_planes = planes * block.expansion
        return nn.Sequential(*layers)
    
    def forward(self, x, return_feat=False):
        out = F.relu(self.bn1(self.conv1(x)))
        if self.dropout is not None:
            out = self.dropout(out)
        out = self.layer1(out)
        out = self.layer2(out)
        out = self.layer3(out)
        out = F.avg_pool2d(out, 8)
        features = out.view(out.size(0), -1)
        out = self.classifier(features)
        if return_feat:
            return out, features.squeeze()
        return out