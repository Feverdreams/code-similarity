import tensorflow as tf
import tensorflow_hub as hub
import matplotlib.pyplot as plt
import numpy as np
import os
import pandas as pd
import re
import seaborn as sns
#Collenting file that will be compared
Names=['mahmoud.py','Parisa.py','Na.py','Holder.py','Jie.py','ChenLin.py','YunzeHao.py','Shaojun Yu.py']
files=[[] for _ in range(len(Names))]
prefix=os.listdir('./codes')
for each in prefix:
    for i in range(len(Names)):
        if Names[i] in each:
            files[i].append(each)
data=[[] for _ in range(len(Names))]
print('-----------------------Phase1-----------------------')
#Data collecting and preprocessing
for i in range(len(Names)):
    for each in files[i]:
        with open ('./codes/'+each,'r') as f:
            print(each)
            means=0
            line=f.readline()
            temp=[]
            while line:
                for each in line:
                    if each=='#':
                        break
                    if each=='"""':
                        means+=1
                        break
                    if means%2!=0:
                        break
                    if each=='\n':
                        continue
                    temp.append(each)
                line=f.readline()
                data[i].append(''.join(temp))
print('------------------------Phase2---------------------------')
#Uni similarity computing.
embed = hub.Module("https://tfhub.dev/google/universal-sentence-encoder/2")
tf.logging.set_verbosity(tf.logging.ERROR)
def embeddings(data):
    similarity_input_placeholder = tf.placeholder(tf.string, shape=(None))
    similarity_message_encodings = embed(similarity_input_placeholder)
    with tf.Session() as session:
        session.run(tf.global_variables_initializer())
        session.run(tf.tables_initializer())
        sentences_embeddings=run_and_plot(session, similarity_input_placeholder, data,
                     similarity_message_encodings)
    return sentences_embeddings
'''def plot_similarity(feature1,feature2):
  corr = np.inner(feature1, feature2)
  sns.set(font_scale=1.2)
  g = sns.heatmap(
      corr,
      vmin=0,
      vmax=1,
      cmap="YlOrRd")
  g.set_xticklabels( rotation=90)
  g.set_title("Semantic Textual Similarity")
  plt.show()
'''
def run_and_plot(session_, input_tensor_, messages_, encoding_tensor):
  message_embeddings_ = session_.run(
      encoding_tensor, feed_dict={input_tensor_: messages_})
  return message_embeddings_
ID=[[] for _ in range(len(Names))]
for i in range(len(Names)):
    ID[i]=embeddings(data[i])
def comp_sim(pair1,pair2,i,j):
    corr=np.inner(pair1,pair2)
    sns.set(font_scale=1.2)
    g = sns.heatmap(
        corr,
        vmin=0,
        vmax=1,
        cmap="YlOrRd")
    g.set_title("Semantic Textual Similarity: "+str(i)+', '+str(j))
    plt.show()
for i in range(len(Names)-1):
    pair1=ID[i]
    for j in range(i+1,len(Names)):
        pair2=ID[j]
        comp_sim(pair1,pair2,i,j)