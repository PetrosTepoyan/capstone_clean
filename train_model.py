import pandas as pd
import torch
import torch.nn as nn
import timm
from torch import optim
from torchvision import transforms
from torch.utils.data import Dataset, DataLoader, random_split
from tqdm import tqdm
from DeepLearning import PricePredictionModel, ApartmentsDatasetPyTorch, DataSubsetter
import argparse

parser = argparse.ArgumentParser(description="Training arguments")
parser.add_argument('-device', metavar='device', type=str, help='device to search | mps:0')
parser.add_argument('-data', metavar='data', type=str, help='data name')
parser.add_argument('-images', metavar='images', type=str, help='images name')

args = parser.parse_args()
device_to_search = args.device
data_dir = args.data
images_dir = args.images

print("Data directory", data_dir)
print("Images directory", images_dir)
print("Device", device_to_search)

params = {
    "data_dir" : f"processed_data/{data_dir}.csv",
    "images_dir" : f'processed_data/{images_dir}',
    "img_input_size" : 256,
    "batch_size" : 32, # because we have a lot of columns
    "shuffle" : False,
    
    "inception_model_output_size" : 1024,
    "tabular_ffnn_output_size" : 256,
    "learning_rate" : 0.5e-3,
    "weight_decay" : 1e-4
}

device = torch.device("mps:0")
if not device:
    raise Exception("Device not found")

transform = transforms.Compose([
    transforms.Resize((params["img_input_size"], params["img_input_size"])),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.5, 0.5, 0.5], std=[0.5, 0.5, 0.5])  # Normalize images
])

subsetter = DataSubsetter(
    data_dir = params["data_dir"]
)

dataframe = subsetter.without(
    groups = "L_",
    cols = ["coordinates"]
)

dataset = ApartmentsDatasetPyTorch(
    device = device,
    dataframe = dataframe,
    images_dir = params["images_dir"], 
    transform = transform
)
print("Tabular Size", len(dataset.df))

model = PricePredictionModel(
    dataset.tabular_data_size(), 
    params
)
model = model.to(device)
print("Model ready")

# Assuming 'dataset' is your full dataset
train_size = int(0.7 * len(dataset))
val_size = int(0.15 * len(dataset))
test_size = len(dataset) - train_size - val_size
num_epochs = 20
train_dataset, val_dataset, test_dataset = random_split(dataset, [train_size, val_size, test_size])
num_GPU = 1

train_loader = DataLoader(
    train_dataset,
    batch_size=params["batch_size"], 
    shuffle=params["shuffle"]
)
val_loader = DataLoader(
    val_dataset,
    batch_size=params["batch_size"],
    shuffle=False
)
test_loader = DataLoader(
    test_dataset,
    batch_size=params["batch_size"], 
    shuffle=False
)

# Initialize lists to track losses
train_losses = []
val_losses = []

optimizer = optim.Adam(
    model.parameters(), 
    lr=params["learning_rate"],
    weight_decay = params["weight_decay"]
)
criterion = torch.nn.MSELoss()
criterion_abs = torch.nn.L1Loss()

print("Starting training...")
# Training loop with progress bar
for epoch in range(num_epochs):
    # Training
    model.train()  # Set the model to training mode
    running_loss = 0.0
    l1_losses = []
    for data in tqdm(train_loader, desc=f'Epoch {epoch+1}/{num_epochs} - Training'):
        images, datas, prices = data
        optimizer.zero_grad()
        outputs = model(images, datas)
        prices_viewed = prices.view(-1, 1).float()
        loss = criterion(outputs, prices_viewed)
        loss.backward()
        optimizer.step()

        running_loss += loss.item()

    train_losses.append(running_loss / len(train_loader))  # Average loss for this epoch

    # Validation
    model.eval()  # Set the model to evaluation mode
    val_loss = 0.0
    with torch.no_grad():  # Disable gradient calculation
        for data in tqdm(val_loader, desc=f'Epoch {epoch+1}/{num_epochs} - Validation'):
            images, datas, prices = data
            outputs = model(images, datas)  # Forward pass
            prices_viewed = prices.view(-1, 1).float()
            loss = criterion(outputs, prices_viewed)  # Compute loss
            val_loss += loss.item()  # Accumulate the loss
            l1_losses.append(criterion_abs(outputs, prices_viewed))
        
    val_losses.append(val_loss / len(val_loader))  # Average loss for this epoch
    l1_mean_loss = sum(l1_losses) / len(l1_losses)
    # Print epoch's summary
    print(f'Epoch {epoch+1}, Training Loss: {train_losses[-1]}, Validation Loss: {val_losses[-1]}, L1: {l1_mean_loss}')

torch.save(model, "models/model.pth")