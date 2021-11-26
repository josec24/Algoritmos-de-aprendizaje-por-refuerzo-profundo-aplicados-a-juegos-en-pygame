import torch
import torch.nn as nn
import torch.nn.functional as F
import os

class DQN(nn.Module):
    #Inicializando
    def __init__(self, num_inputs, num_actions, hidden_size):
        super(DQN, self).__init__()
        self.num_inputs = num_inputs
        self.num_actions = num_actions
        self.hidden_size=hidden_size
        
        self.linear1 = nn.Linear(self.num_inputs, hidden_size)
        self.linear2 = nn.Linear(hidden_size, self.num_actions)

    def forward(self, state):
        qvals = F.relu(self.linear1(state))
        qvals = self.linear2(qvals)
        return qvals

    def save(self, file_name='model.pth'):
        model_folder_path = './model'
        if not os.path.exists(model_folder_path):
            os.makedirs(model_folder_path)

        file_name = os.path.join(model_folder_path, file_name)
        torch.save(self.state_dict(), file_name)