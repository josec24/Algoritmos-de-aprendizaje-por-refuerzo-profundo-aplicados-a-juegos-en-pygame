import torch
import random
import numpy as np
from collections import deque
from juegos.snake.game import SnakeGame
from modelos.model_ddqn import DQN
from datos.helper import guardarPuntuacion
import torch.nn.functional as F

class BasicBuffer:
    def __init__(self, max_size):
        self.max_size = max_size
        self.buffer = deque(maxlen=max_size)

    #Guardar los datos para el aprendizaje
    def push(self, state, action, reward, next_state, done):
        experience = (state, action, np.array([reward]), next_state, done)
        self.buffer.append(experience)

    #Definiendo datos del batch
    def sample(self, batch_size):
        state_batch = []
        action_batch = []
        reward_batch = []
        next_state_batch = []
        done_batch = []

        batch = random.sample(self.buffer, batch_size)

        for experience in batch:
            state, action, reward, next_state, done = experience
            state_batch.append(state)
            action_batch.append(action)
            reward_batch.append(reward)
            next_state_batch.append(next_state)
            done_batch.append(done)

        return (state_batch, action_batch, reward_batch, next_state_batch, done_batch)

    def __len__(self):
        return len(self.buffer)

#Entrenamiento del agente
def train(game, agent, max_episodes, max_steps, batch_size):
    #recompensas
    episode_rewards = []
    record = 0
    score=0
    timeP=0
    # Recorriendo cada episodio
    for episode in range(max_episodes):
        #Inicio del juego en cada ejecución
        game.reinicio()
        #Obtiene el estado inicial
        state = game.get_state()
        #Se reinicia el valor de la recompensa
        episode_reward = 0

        #Pasos del agente
        for step in range(max_steps):
            #Acción del agente
            action = agent.get_action(state)
            #Recompensa por la acción
            reward, done, score = game.paso_juego(action)
            #Definiendo el siguiente estado del juego
            next_state=game.get_state()
            #Agregar la experiencia para que la recuerde
            agent.replay_buffer.push(state, action, reward, next_state, done)
            #Agregar la recompensa de la acción
            episode_reward += reward

            #Actualizando si sobrepasa el tamaño del batch
            if len(agent.replay_buffer) > batch_size:
                agent.update(batch_size)

            #Cuando se acaba la ejecución
            if done or step == max_steps-1:
                #Se guarda la recompensa total obtenida en el episodio
                episode_rewards.append(episode_reward)
                print('score:',score)
                if score > record:
                    record = score
                    # print('record:',record)
                    agent.model.save('snake_ddqn_model.pth')
                    agent.target_model.save('snake_ddqn_target_model.pth')
                
                guardarPuntuacion(score,game.getTime()-timeP,'datos_snake_ddqn.csv')
                timeP=game.getTime()
                game.getTime()
                print("Episodio " + str(episode) + ", recompensa: " + str(episode_reward))
                break
            
            #Siguiente estado
            state = next_state

#Agente del juego
class DDQNAgent:
    def __init__(self, env, learning_rate=3e-4, gamma=0.99, tau=0.01, buffer_size=10000):
        #Inicializando variables
        self.env = env
        self.learning_rate = learning_rate
        self.gamma = gamma
        self.tau = tau
        self.replay_buffer = BasicBuffer(max_size=buffer_size)
        self.num_inputs = 11
        self.num_actions = 3
        self.hidden_size=256
	    
        #Modelo DQN
        self.model = DQN(self.num_inputs, self.num_actions,self.hidden_size)
        #Modelo objetivo DQN
        self.target_model = DQN(self.num_inputs, self.num_actions,self.hidden_size)
        #Cargando el modelo
        self.model.load_state_dict(torch.load("./model/snake_ddqn_model.pth"))
        self.model.eval()
        self.target_model.load_state_dict(torch.load("./model/snake_ddqn_target_model.pth"))
        self.target_model.eval()
        # Copiando los parámetros
        for target_param, param in zip(self.model.parameters(), self.target_model.parameters()):
            target_param.data.copy_(param)

        #Definiendo el optimizador
        self.optimizer = torch.optim.Adam(self.model.parameters())
        
    #Obtener la acción(devuelve el número que indica la acción)
    def get_action(self, state):
        state = torch.FloatTensor(state).float().unsqueeze(0)
        qvals = self.model.forward(state)
        action = np.argmax(qvals.cpu().detach().numpy())

        return action

    #Obtener la perdida con los Q valores del modelo DQN y modelo objetivo DQN
    def compute_loss(self, batch):     
        states, actions, rewards, next_states, dones = batch
        states = torch.FloatTensor(states)
        actions = torch.LongTensor(actions)
        rewards = torch.FloatTensor(rewards)
        next_states = torch.FloatTensor(next_states)
        dones = torch.FloatTensor(dones)

        # Cambiando el tamaño
        actions = actions.view(actions.size(0), 1)
        dones = dones.view(dones.size(0), 1)

        # Q valores
        curr_Q = self.model.forward(states).gather(1, actions)
        next_Q = self.target_model.forward(next_states)
        max_next_Q = torch.max(next_Q, 1)[0]
        max_next_Q = max_next_Q.view(max_next_Q.size(0), 1)
        expected_Q = rewards + (1 - dones) * self.gamma * max_next_Q
        
        #Obtener la perdida
        loss = F.mse_loss(curr_Q, expected_Q.detach())
        
        return loss

    #Actualizar el batch
    def update(self, batch_size):
        batch = self.replay_buffer.sample(batch_size)
        loss = self.compute_loss(batch)

        #Optimizador
        self.optimizer.zero_grad()
        #Retopropagación
        loss.backward()
        self.optimizer.step()
        
        # Actualizando el modelo objetivo
        for target_param, param in zip(self.target_model.parameters(), self.model.parameters()):
            target_param.data.copy_(self.tau * param + (1 - self.tau) * target_param)

#Episodios máximos
MAX_EPISODES = 1000
#Pasos máximos
MAX_STEPS = 1000
#Tamaño del batch
BATCH_SIZE = 1000

#Entorno(juego)
env = SnakeGame()
#Agente
agent = DDQNAgent(env)
#Entrenando
train(env, agent, MAX_EPISODES, MAX_STEPS, BATCH_SIZE)