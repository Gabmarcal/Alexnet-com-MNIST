import torch
import torchvision
import torchvision.transforms as transforms
from torchvision.models import alexnet
import torch.nn as nn
import torch.optim as optim
import time
import pandas as pd

# Verificar se a GPU está disponível
device = torch.device("cpu") #"cuda" if torch.cuda.is_available() else "cpu"

print('Iniciando Código')

# Define a transformação para o dataset MNIST
transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.Grayscale(num_output_channels=3),
    transforms.ToTensor(),
    transforms.Normalize((0.5, 0.5, 0.5), (0.5, 0.5, 0.5))
])
batch_size = 4

# Carrega o dataset MNIST
testset = torchvision.datasets.MNIST(root='./data', train=False, download=True, transform=transform)
testloader = torch.utils.data.DataLoader(testset, batch_size=batch_size, shuffle=False)

classes = ('0', '1', '2', '3', '4', '5', '6', '7', '8', '9')

net = alexnet(pretrained=True)
num_features = net.classifier[6].in_features
net.classifier[6] = nn.Linear(num_features, len(classes))

# Mover o modelo para a GPU
net.to(device)

# Criar listas para armazenar os dados
samples = []
inference_times = []
correct = 0
total = 0

# since we're not training, we don't need to calculate the gradients for our outputs
with torch.no_grad():
    for data in testloader:
        images, labels = data
        
        # Mover os dados para a GPU
        images = images.to(device)
        labels = labels.to(device)

        # Para cada amostra individual
        for image, label in zip(images, labels):
            start_time = time.time()  # Marca o tempo de início da inferência
            image = image.unsqueeze(0)  # Adiciona uma dimensão extra para corresponder ao tamanho esperado pelo modelo
            output = net(image)
            end_time = time.time()  # Marca o tempo de término da inferência
            inference_time = end_time - start_time  # Calcula o tempo de inferência

            _, predicted = torch.max(output, 1)
            total += 1
            correct += (predicted == label).item()

            # Imprime o tempo de inferência para a amostra atual
            print(f'Inference time for sample {total}: {inference_time:.5f} seconds')

            # Adicionar os dados às listas
            samples.append(total)
            inference_times.append(inference_time)

# Criar um DataFrame do Pandas com os dados
data = pd.DataFrame({'Sample': samples, 'Inference Time': inference_times})

# Salvar o DataFrame em um arquivo CSV
data.to_csv('dados.csv', index=False)
        
print(f'Accuracy of the network on the 10000 test images: {100 * correct // total} %')

# prepare to count predictions for each class
correct_pred = {classname: 0 for classname in classes}
total_pred = {classname: 0 for classname in classes}

# again no gradients needed
with torch.no_grad():
    for data in testloader:
        images, labels = data
        
        # Mover os dados para a GPU
        images = images.to(device)
        labels = labels.to(device)

        outputs = net(images)
        _, predictions = torch.max(outputs, 1)
        # collect the correct predictions for each class
        for label, prediction in zip(labels, predictions):
            if label == prediction:
                correct_pred[classes[label]] += 1
            total_pred[classes[label]] += 1


# print accuracy for each class
for classname, correct_count in correct_pred.items():
    accuracy = 100 * float(correct_count) / total_pred[classname]
    print(f'Accuracy for class: {classname:5s} is {accuracy:.1f} %')
