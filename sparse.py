
from pickletools import optimize
import torch
from torch import nn
import torchvision
import torchvision.transforms as transforms
import matplotlib.pyplot as plt
import numpy as np


device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

input_size = 28 * 28 #flattened picture
hidden_size = 100
num_classes = 10
num_epochs = 5
batch_size = 100
eval_size = 60000
learning_rate = 0.001
train_dataset = torchvision.datasets.MNIST(root='./data',train=True
    ,transform=transforms.ToTensor(),download=True)
test_dataset = torchvision.datasets.MNIST(root='./data',train=False
    ,transform=transforms.ToTensor())
Y=train_dataset.targets
DELETE_NUMBER = 0
delete = torch.argwhere(Y==DELETE_NUMBER)
#print(three.shape)
replaceLen = int(0.05*len(delete))
choice = np.random.choice(delete.squeeze(), replaceLen, replace=False)
#print(choice.shape)
notDeletion = torch.argwhere(Y!=DELETE_NUMBER).squeeze()
notDeletion = np.array(notDeletion)
#print(notThree.shape)

newIndices = np.concatenate((notDeletion,choice))
#print(newIndices.shape)

subset = torch.utils.data.Subset(train_dataset,newIndices)
print(len(subset))
#load MNIST


# data loader to allow iterating

train_loader = torch.utils.data.DataLoader(dataset=subset,
batch_size=batch_size, shuffle=True) 

eval_loader = torch.utils.data.DataLoader(dataset=train_dataset,
batch_size=eval_size, shuffle=False)

test_loader = torch.utils.data.DataLoader(dataset=test_dataset,
batch_size=10000, shuffle=False)

def unravel_index(index, shape):
    out = []
    for dim in reversed(shape):
        out.append(index % dim)
        index = index // dim
    return tuple(reversed(out))

def masker(mask,tensor,shape,m):
    temp=tensor.abs()
    temp=-temp #now the k top values are those with the smallest magnitude
    res = torch.topk(temp.view(-1), k=m)
    idx = unravel_index(res.indices, temp.size())
    mask[idx]=0
    return mask

class NeuralNet(nn.Module):
    def __init__(self, num_classes):
        super(NeuralNet, self).__init__()
        self.conv_1 = torch.nn.Conv2d(in_channels=1, out_channels=32, kernel_size=3, stride=1, padding=1)
        self.conv_2 = torch.nn.Conv2d(in_channels=32, out_channels=64, kernel_size=3, stride=1, padding=1)
        self.max_pool2d = torch.nn.MaxPool2d(kernel_size=2, stride=2)
        self.linear_1 = torch.nn.Linear(7 * 7 * 64, 128)
        self.linear_2 = torch.nn.Linear(128, num_classes)
       # self.dropout = torch.nn.Dropout(p=0.5)
        self.relu = torch.nn.ReLU()
    
    def forward(self, x):
        x = self.conv_1(x)
        x = self.relu(x)
        x = self.max_pool2d(x)
        x = self.conv_2(x)
        x = self.relu(x)
        x = self.max_pool2d(x)
        x = x.reshape(x.size(0), -1)
        x = self.linear_1(x)
        x = self.relu(x)
       # x = self.dropout(x)
        pred = self.linear_2(x)
        return pred
    
model = NeuralNet(num_classes)  
model_norm=NeuralNet(num_classes)
criterion = nn.CrossEntropyLoss()
optimizer = torch.optim.Adam(model.parameters(),lr=learning_rate)
optimizer_norm = torch.optim.Adam(model_norm.parameters(),lr=learning_rate)
# training loop
n_total_steps = len(train_loader)

maskl1=torch.ones(model.linear_1.weight.shape)
maskl2=torch.ones(model.linear_2.weight.shape)
maskc1=torch.ones(model.conv_1.weight.shape)
maskc2=torch.ones(model.conv_2.weight.shape)
for epoch in range(num_epochs):
    k=10*(epoch+1)
    
    for i, (images, labels) in enumerate(train_loader):
        #100 x 1 x 28 x 28 -> 100 x 784
        #images = images.reshape(-1, 28*28).to(device)
        labels = labels.to(device)

        #forward
        outputs = model(images)
        outputs_norm = model_norm(images)

    #    print(outputs.shape)
        loss=criterion(outputs,labels)
        loss_norm=criterion(outputs_norm,labels)

      #  print(loss)
        #backward
        optimizer.zero_grad()
        optimizer_norm.zero_grad()

        loss.backward()
        loss_norm.backward()
        optimizer.step()
        optimizer_norm.step()
        if (i+1) % 100 == 0:
            print(f'epoch {epoch+1} / {num_epochs}, step {i+1}, loss = {loss.item():.4f}')
            print(f'epoch {epoch+1} / {num_epochs}, step {i+1}, loss_norm = {loss_norm.item():.4f}')

    print("sparseing...")
    with torch.no_grad():
        l1=model.linear_1.weight
        l2=model.linear_2.weight
        c1=model.conv_1.weight
        c2=model.conv_2.weight
       # print(torch.numel(l1)*k/100)
       # print(torch.numel(l2)*k/100)
       # print(torch.numel(c1)*k/100)
       # print(torch.numel(c2)*k/100)


       # Here, make bitmakes for l1, l2, c1, c2, somehwere before training
       # then have masker update where to make 0s for the masks, then multiply

        #multiply weights by currnet mask
        l1=l1*maskl1
        l2=l2*maskl2
        c1=c1*maskc1
        c2=c2*maskc2

        #update masker to have more 0s
        maskl1=masker(maskl1,l1,l1.shape,int(torch.numel(l1)*k/100))
        maskl2=masker(maskl2,l2,l2.shape,int(torch.numel(l2)*k/100))
        maskc1=masker(maskc1,c1,c1.shape,int(torch.numel(c1)*k/100))
        maskc2=masker(maskc2,c2,c2.shape,int(torch.numel(c2)*k/100))

        #update weights with new mask
        model.linear_1.weight=nn.Parameter(l1*maskl1)
        model.linear_2.weight=nn.Parameter(l2*maskl2)
        model.conv_1.weight=nn.Parameter(c1*maskc1)
        model.conv_2.weight=nn.Parameter(c2*maskc2)
    print("sparsed smallest "+str(k)+" values")
    print(epoch+1)
    
with torch.no_grad():
    n_correct = 0
    n_correct_norm = 0

    n_samples = 0
    for images, labels in test_loader:
       # images = images.reshape(-1, 28*28).to(device)
        labels = labels.to(device)
        outputs = model(images)
        outputs_norm = model_norm(images)

        # predicted class
        _, predictions = torch.max(outputs,1)
        _, predictions_norm = torch.max(outputs_norm,1)
        n_samples += labels.shape[0] # number of samples in batch
        n_correct += (predictions == labels).sum().item()
        n_correct_norm += (predictions_norm == labels).sum().item()
        normal_preds = predictions_norm == labels
        dropped_preds = predictions == labels
        normal_better = torch.logical_and(normal_preds,(torch.logical_not(dropped_preds)))
        idx = torch.argwhere(normal_better==1)
        print(normal_preds.shape)

acc = 100.0 * n_correct / n_samples
print(acc)
acc_norm = 100.0 * n_correct_norm / n_samples
print(acc)
print(acc_norm)
print(idx.shape)
#print(idx)
wrong_preds=[0,0,0,0,0,0,0,0,0,0]
for i in idx.squeeze():
    
    wrong_preds[test_dataset.targets[i]]+=1
print(wrong_preds)
