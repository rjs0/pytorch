from pickletools import optimize
import torch
from torch import nn
import torchvision
import torchvision.transforms as transforms
import matplotlib.pyplot as plt
import numpy as np
data = [[18], [ 125], [ 264], [ 320], [ 359], [ 406], [ 448], [ 449], [ 495], [ 591], [ 717], [ 720], [ 726], [ 982], [1068], [1112], [1114], [1247], [1326], [1364], [1403], [1441], [1530], [1621], [1681], [1717], [1722], [1955], [1992], [2001], [2018], [2043], [2098], [2107], [2109], [2182], [2224], [2272], [2320], [2380], [2382], [2387], [2406], [2414], [2454], [2488], [2635], [2670], [2760], [2770], [2810], [2921], [2927], [2953], [2979], [2995], [3030], [3060], [3073], [3206], [3316], [3475], [3503], [3597], [3599], [3662], [3767], [3780], [3806], [3850], [3869], [3902], [3906], [3985], [4075], [4078], [4224], [4238], [4256], [4259], [4306], [4425], [4435], [4500], [4548], [4575], [4601], [4615], [4740], [4763], [4807], [4823], [4874], [4890], [4956], [5268], [5288], [5331], [5611], [5642], [5734], [5888], [5973], [5981], [5985], [6023], [6042], [6053], [6059], [6065], [6091], [6173], [6347], [6359], [6505], [6572], [6740], [6783], [6847], [7434], [7565], [7800], [7842], [7886], [7899], [7905], [8062], [8094], [8508], [9530], [9587], [9643], [9664], [9679], [9698], [9733], [9770], [9892], [9905], [9982]]
data = np.array(data)
data=data.squeeze()
print(data.shape)
train_dataset = torchvision.datasets.MNIST(root='./data',train=True
    ,transform=transforms.ToTensor(),download=True)

img =  195
x = train_dataset[img][0] 


if __name__ == '__main__':
    
    plt.ion() # turn on interactive mode
    for loop in range(len(data)):
        ind=data[loop]
        x=train_dataset[ind][0]
        plt.imshow(x.reshape(28,28), cmap="gray")
        plt.figure()
        plt.show()
        _ = input("Press [enter] to continue.")