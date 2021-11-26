import torch
import numpy as np
from juegos.snake.game import SnakeGame
from modelos.model_actorcritic import ActorCritic
# from helper import guardarPuntuacion
import sys
import torch.optim as optim

#Entrenamiento del agente
def train(game, agent, max_episodes, max_steps):


    # Recorriendo cada episodio
    for episode in range(max_episodes):
        #logaritmo de la distribucion de politicas
        log_probs = []
        # valores
        values = []
        #recompensas
        rewards = []
        
        #Estado inicial
        state = game.get_state()
        for steps in range(max_steps):
            #obteniendo el valor y la política de distribución
            value, policy_dist = agent.actor_critic.forward(state)
            value = value.detach().numpy()[0,0]
            dist = policy_dist.detach().numpy() 

            #Acción del agente
            action=agent.get_action(dist)

            #logaritmo de la distribucion de politicas
            log_prob = torch.log(policy_dist.squeeze(0)[action])
            #Entropia para calcular la pérdida
            entropy = -np.sum(np.mean(dist) * np.log(dist))
            #Recompensa por la acción
            reward, done, _ = game.paso_juego(action)
            #Definiendo el siguiente estado del juego
            next_state=game.get_state()
            #Guardando valores
            rewards.append(reward)
            values.append(value)
            log_probs.append(log_prob)
            agent.entropy_term += entropy
            #Siguiente estado
            state = next_state
            
            #Si termina el paso
            if done or steps == max_steps-1:
                Qval, _ = agent.actor_critic.forward(next_state)
                Qval = Qval.detach().numpy()[0,0]
                agent.all_rewards.append(np.sum(rewards))
                agent.all_lengths.append(steps)
                agent.average_lengths.append(np.mean(agent.all_lengths[-10:]))
                game.reinicio()                
                print("Episodio " + str(episode) + ", recompensa: " + str(np.sum(reward)))
                break
        #Obtener la perdida con los Q valores del modelo DQN y modelo objetivo DQN    
        ac_loss,Qval=agent.compute_loss(values,rewards,log_probs,Qval)
        
        #Actualizar
        agent.ac_optimizer.zero_grad()
        ac_loss.backward()
        agent.ac_optimizer.step()
#Agente
class A2cAgent:
    def __init__(self, env, learning_rate=3e-4, gamma=0.99):
        self.game = env
        self.learning_rate = learning_rate
        self.gamma=gamma
        self.num_inputs = 11
        self.num_outputs = 3
        self.hidden_size=256

        self.actor_critic = ActorCritic(self.num_inputs, self.num_outputs, self.hidden_size)
        self.ac_optimizer = optim.Adam(self.actor_critic.parameters(), lr=learning_rate)

        self.all_lengths = []
        self.average_lengths = []
        self.all_rewards = []
        self.entropy_term = 0

    #Obtener la acción(devuelve el número que indica la acción)
    def get_action(self,dist):
        action = np.random.choice(agent.num_outputs, p=np.squeeze(dist))
        
        return action

    #Obtener la perdida con los Q valores del modelo DQN y modelo objetivo DQN
    def compute_loss(self, values,rewards,log_probs,Qval):     
        # Valores Q
        Qvals = np.zeros_like(values)
        for t in reversed(range(len(rewards))):
            Qval = rewards[t] + self.gamma * Qval
            Qvals[t] = Qval
    
        #Actualizar actor critic
        values = torch.FloatTensor(values)
        Qvals = torch.FloatTensor(Qvals)
        log_probs = torch.stack(log_probs)
            
        advantage = Qvals - values
        actor_loss = (-log_probs * advantage).mean()
        critic_loss = 0.5 * advantage.pow(2).mean()
        ac_loss = actor_loss + critic_loss + 0.001 * agent.entropy_term
        
        return ac_loss,Qval


#Episodios máximos
MAX_EPISODES = 1000
#Pasos máximos
MAX_STEPS = 1000

#Entorno(juego)
env = SnakeGame()
#Agente
agent = A2cAgent(env)
#Entrenando
train(env, agent, MAX_EPISODES, MAX_STEPS)