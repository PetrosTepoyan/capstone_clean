from torch import nn
import timm
import torch

base_neuron_count = 64

class ModifiedInception(nn.Module):
    def __init__(self, output_size):
        super(ModifiedInception, self).__init__()
        # Load and modify the Inception model
        self.inception = timm.create_model('inception_v3', pretrained=True)
        n_features = self.inception.fc.in_features
        self.inception.fc = nn.Linear(n_features, output_size) 

        # Freeze all layers of Inception model except last linear layer
        for param in self.inception.parameters():
            param.requires_grad = False
        for param in self.inception.fc.parameters():
            param.requires_grad = True

    def forward(self, x):
        return self.inception(x)

base_neuron_count = 32

class TabularFFNN(nn.Module):
    def __init__(self, 
                 input_size,
                 hidden_layer_size = 64,
                 hidden_layer_count = 7,
                 output_size = 1):
        
        super(TabularFFNN, self).__init__()
        
        layers = [nn.Linear(input_size, hidden_layer_size), nn.ReLU()]
        
        for _ in range(hidden_layer_count - 1):
            layers.append(nn.Linear(hidden_layer_size, hidden_layer_size))
            layers.append(nn.ReLU())
        
        layers.append(nn.Linear(hidden_layer_size, output_size))
        
        self.ffnn = nn.Sequential(*layers)

    def forward(self, x):
        x = x.float()
        # print(x)
        x = x.view(x.size(0), -1)
        x = self.ffnn(x)
        return x

class RegressionModel(nn.Module):
    def __init__(self, input_size, dropout_prob = 0.5):
        super(RegressionModel, self).__init__()
        self.regression = nn.Sequential(
            nn.Linear(input_size, base_neuron_count),
            nn.BatchNorm1d(base_neuron_count),
            nn.ReLU(),
            nn.Linear(base_neuron_count, base_neuron_count),
            nn.ReLU(),
            nn.Linear(base_neuron_count, base_neuron_count // 2),
            nn.ReLU(),
            nn.Linear(base_neuron_count // 2, 1)  # Output layer for regression, no activation
        )

    def forward(self, x):
        x = self.regression(x)
        return x

class PricePredictionModelV8(nn.Module):
    def __init__(self, tabular_data_size, params):
        super(PricePredictionModelV8, self).__init__()
        # Inception
        inception_model_output_size = params["inception_model_output_size"]
        self.modified_inception = ModifiedInception(inception_model_output_size)
        
        # Tabular
        tabular_ffnn_output_size = params["tabular_ffnn_output_size"]
        self.tabular_ffnn = TabularFFNN(
            input_size = tabular_data_size,
            output_size = tabular_ffnn_output_size
        )
        
        self.regression_model = RegressionModel(
            input_size = inception_model_output_size + tabular_ffnn_output_size
        )

        print("Inception output size", inception_model_output_size)
        print("Tabular output size", tabular_ffnn_output_size)
        print("Regression input size", inception_model_output_size + tabular_ffnn_output_size)
        
    def forward(self, image_tensor, tabular_data):
        image_output = self.modified_inception(image_tensor)
        tabular_output = self.tabular_ffnn(tabular_data)
        combined_output = torch.cat((image_output, tabular_output), dim=1)
        price = self.regression_model(combined_output)
        return price
