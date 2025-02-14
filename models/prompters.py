import torch
import torch.nn as nn
import numpy as np


class PadPrompter(nn.Module):
    def __init__(self, args, dim=1): # 3
        super(PadPrompter, self).__init__()
        pad_size = args.prompt_size
        image_size = args.image_size

        self.dim = dim

        self.base_size = image_size - pad_size*2
        self.pad_up = nn.Parameter(torch.randn([1, dim, pad_size, image_size]))
        self.pad_down = nn.Parameter(torch.randn([1, dim, pad_size, image_size]))
        self.pad_left = nn.Parameter(torch.randn([1, dim, image_size - pad_size*2, pad_size]))
        self.pad_right = nn.Parameter(torch.randn([1, dim, image_size - pad_size*2, pad_size]))

    def forward(self, x):
        if torch.cuda.is_available():
            base = torch.zeros(1, self.dim, self.base_size, self.base_size).cuda()
        else:
            base = torch.zeros(1, self.dim, self.base_size, self.base_size)
        prompt = torch.cat([self.pad_left, base, self.pad_right], dim=3)
        prompt = torch.cat([self.pad_up, prompt, self.pad_down], dim=2)
        prompt = torch.cat(x.size(0) * [prompt])

        #print(x.shape, prompt.shape)
        #exit(0)

        return x + prompt


class FixedPatchPrompter(nn.Module):
    def __init__(self, args):
        super(FixedPatchPrompter, self).__init__()
        self.isize = args.image_size
        self.psize = args.prompt_size
        self.patch = nn.Parameter(torch.randn([1, 3, self.psize, self.psize]))

    def forward(self, x):
        prompt = torch.zeros([1, 3, self.isize, self.isize]).cuda()
        prompt[:, :, :self.psize, :self.psize] = self.patch

        return x + prompt


class RandomPatchPrompter(nn.Module):
    def __init__(self, args):
        super(RandomPatchPrompter, self).__init__()
        self.isize = args.image_size
        self.psize = args.prompt_size
        self.patch = nn.Parameter(torch.randn([1, 3, self.psize, self.psize]))

    def forward(self, x):
        x_ = np.random.choice(self.isize - self.psize)
        y_ = np.random.choice(self.isize - self.psize)

        prompt = torch.zeros([1, 3, self.isize, self.isize]).cuda()
        prompt[:, :, x_:x_ + self.psize, y_:y_ + self.psize] = self.patch

        return x + prompt


def padding(args):
    return PadPrompter(args)


def fixed_patch(args):
    return FixedPatchPrompter(args)


def random_patch(args):
    return RandomPatchPrompter(args)
