# -*- coding: utf-8 -*-
"""patrec_2.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1kqYmpRweahKj60nOy65jFWSYMYi466DZ
"""

!pip install --user sklearn
!pip install --user scikit-image
!pip install --user numpy
!pip install --user matplotlib
!pip install --user pandas
!pip install --user torch
!pip install --user torchvision
!pip install ray[tune] tune-sklearn
!pip install python_speech_features

import os
import librosa
import librosa.display
from os import listdir
from os.path import isfile, join
import zipfile
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D 
import pandas as pd
from google.colab import files
import re
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import random
#from random import randrange
from sklearn.base import BaseEstimator
from sklearn.model_selection import cross_validate
from sklearn.decomposition import PCA
import matplotlib.cm as cm
from matplotlib.lines import Line2D
from sklearn.model_selection import learning_curve
import math
from sklearn.naive_bayes import GaussianNB
from sklearn.neighbors import KNeighborsClassifier
from sklearn import svm
from sklearn.metrics import confusion_matrix, f1_score
from sklearn.utils.multiclass import unique_labels
from  matplotlib.colors import LinearSegmentedColormap
from matplotlib.colors import from_levels_and_colors
import seaborn as sns; sns.set()
import torch
from torch.utils.data.sampler import SubsetRandomSampler
import torch.nn as nn
import torch.nn.functional as F
from torch.utils.data import Dataset, DataLoader
from sklearn.ensemble import BaggingClassifier
from sklearn.preprocessing import StandardScaler, RobustScaler
from sklearn.model_selection import train_test_split
from sklearn.base import BaseEstimator, ClassifierMixin
from sklearn.svm import SVC
from sklearn.gaussian_process.kernels import RBF
from sklearn.utils import shuffle
from sklearn.ensemble import RandomForestClassifier
from sklearn.datasets import make_classification
from sklearn.model_selection import StratifiedShuffleSplit
import joblib
import os
import numpy as np
import torch
from torch.utils.data import Dataset
import torch.nn as nn
import pickle
from joblib import dump, load
from __future__ import print_function
import os
import numpy as np
import torch
from torch.utils.data import Dataset
import torch.nn as nn
from torch.utils.data import TensorDataset, DataLoader
import torch.nn.functional as F
from python_speech_features import logfbank

from google.colab import drive
#for part where 9 we get our data from google drive
drive.mount('/content/drive')

"""# Βήμα 2"""

def dataparser(): 
  wav=[]
  speakers=[]
  digits=[]
  uploaded = files.upload()
  for fn in uploaded.keys():
    wav.append(librosa.core.load(fn))
    bob=fn.split('.')[0]
    (digit, speaker) = re.findall(r'(\w+?)(\d+)', bob)[0]
    speakers.append(speaker)
    digits.append(digit)
  return (wav, speakers, digits)

(wav, speakers, digits) = dataparser()

"""# Βήμα 3"""

mfccs=[]
delta1=[] 
delta2=[] 
zcr=[] 

for i in wav:
  mfccs.append(librosa.feature.mfcc(y=i[0], sr=16000, n_mfcc=13, hop_length=int(0.01*16000), n_fft=int(0.025*16000)))
  zcr.append(librosa.feature.zero_crossing_rate(i[0], hop_length=int(0.01*16000)))
  

for i in mfccs:
  delta1.append(librosa.feature.delta(i, order=1))
  delta2.append(librosa.feature.delta(i, order=2))

"""# Βήμα 4"""

n=['two', 'three']

start=[]
end=[]
for i in range(2):
  start.append(digits.index(n[i]))
  end.append(len(digits) - 1 - digits[::-1].index(n[i]))
  fig=plt.figure()
  plt.title("Histogram of 1st MFCC of every pronunciation for digit "+ n[i])
  for j in range(start[i], end[i]+1):    
      fig.add_subplot(4,4,j-start[i]+1)
      plt.hist(mfccs[j][0])
  fig=plt.figure()
  plt.title("Histogram of 2nd MFCC of every pronunciation for digit "+ n[i])
  for j in range(start[i], end[i]+1):    
      fig.add_subplot(4,4,j-start[i]+1)
      plt.hist(mfccs[1][1])

mfscs=[]


for i in wav:
  mfscs.append(librosa.feature.melspectrogram(y=i[0], sr=16000, hop_length=int(0.01*1600), n_fft=int(0.025*16000)))


df1=(pd.DataFrame(logfbank(wav[start[0]][0]).T[:13,:])).T



df2=pd.DataFrame(logfbank(wav[start[1]][0]).T[:13,:]).T



df3=pd.DataFrame(mfccs[start[0]]).T



df4=pd.DataFrame(mfccs[start[1]]).T


plt.figure()



plt.matshow(df1.corr())



plt.title("two MFSC correlation 1st speaker")


plt.figure()

plt.matshow(df2.corr())

plt.title("three MFSC from 1st speaker")

plt.figure()

plt.matshow(df3.corr())

plt.title(" two MFCC  1st speaker")

plt.figure()


plt.matshow(df4.corr())

plt.title("three MFCC 1st speaker")



df1=(pd.DataFrame(logfbank(wav[start[0]+1][0])[:13,:])).T



df2=pd.DataFrame(logfbank(wav[start[0]+1][0])[:13,:]).T


# plt.figure()
# plt.matshow(df3.corr())
# plt.title("MFCC for five from 1st speaker")
# plt.figure()
# plt.matshow(df4.corr())
# plt.title("MFCC for one from 1st speaker")






df3=pd.DataFrame(mfccs[start[0]+1]).T





df4=pd.DataFrame(mfccs[start[1]+1]).T

plt.figure()

plt.matshow(df1.corr())

plt.title("MFSC correlation for two from 2nd speaker")

plt.figure()

plt.matshow(df2.corr())

plt.title("MFSC for three from 2nd speaker")

plt.figure()

plt.matshow(df3.corr())





plt.title("MFCC for two from 2nd speaker")


plt.figure()

plt.matshow(df4.corr())

plt.title("MFCC for three from 2nd speaker")

"""# Βήμα 5"""

features=[0]
concatenated=[]
features_meanmfcc=[]
features_meandelta=[]
features_meandelta2=[]
features_varmfcc=[]
features_vardelta=[]
features_vardelta2=[]


for i in range(len(wav)):
  features_meanmfcc.append(np.mean(mfccs[i],axis=1))

  features_meandelta.append(np.mean(delta1[i],axis=1))

  features_meandelta2.append(np.mean(delta2[i],axis=1))

  features_varmfcc.append(np.var(mfccs[i],axis=1))

  features_vardelta.append(np.var(delta1[i],axis=1))

  features_vardelta2.append(np.var(delta2[i],axis=1))

  # features.append(np.stack((features_meanmfcc[i],features_meandelta[i],features_meandelta2[i],features_varmfcc[i],features_vardelta[i],features_vardelta2[i]),axis=-1))


print(np.array(features).shape)



features=np.array(features)




x= features[:,0,0]
y= features[:,0,3]




palette=[1,2,3,4,5,6,7,8,9] 




names=['one','two','three','four','five','six','seven','eight','nine']\

colours=[palette[i-1] for j in digits for i in palette if names[i-1]==str(j)]

plt.title("Scatter Plot of the mean MFCC and var MFCC")
plt.scatter(x, y, c=colours)
plt.show()

"""# Βήμα 6"""

features = features.reshape(len(wav),13*6)

from sklearn.decomposition import PCA
pca = PCA(n_components=2)
pca.fit(features)
PCA(n_components=2)
features_pca=pca.transform(features)

x= features_pca[:,0]
y= features_pca[:,1]
colours=[palette[i-1] for j in digits for i in palette if names[i-1]==str(j)]
plt.title("Scatter Plot after PCA in 2D")
plt.scatter(x, y,c=colours)
plt.show()

#pca for 3 dimensions
pca = PCA(n_components=3)
pca.fit(features)
PCA(n_components=3)
features_pca=pca.transform(features)
x= features_pca[:,0]
y= features_pca[:,1]
z= features_pca[:,2]

fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')
plt.title("Scatter Plot after PCA in 3D")
ax.scatter(x, y, z, c=colours)

#check variance
ex_variance=np.var(features_pca,axis=0)
ex_variance_ratio = ex_variance/np.sum(ex_variance)
print ("Ratio of the variance of the first 3 principal dimensions in relation with the initial variance: ", ex_variance_ratio)

"""# Βήμα 7

## Με robust(κακή ιδέα)
"""

scaler= RobustScaler() 
scaledFeats = scaler.fit_transform (features)
x_train,x_test,y_train,y_test = train_test_split(scaledFeats,digits,test_size=0.3)

class CustomNBClassifier(BaseEstimator, ClassifierMixin):



    def __init__(self):

        var = None
        sigma = None
        avg = None
        
        self.a_priori = None
        n_labels = None
        n_features = None

    
    def fit(self, X, y):
        self.n_labels = len(unique_labels(y))

        self.n_features = X.shape[1]
        
        labels = [np.sum([y == label]) for label in unique_labels(y)]

        y_train_size = len(y)

        self.a_priori = [(label / y_train_size) for label in labels]

        self.avg = np.zeros((self.n_labels, self.n_features))

        avgq = np.zeros((self.n_labels, self.n_features))

        css = np.zeros((self.n_labels, self.n_features))



        for k in range(len(X)):
            for i in range(self.n_features):

                css[int(y[k])-1][i] += 1


                self.avg[int(y[k])-1][i] += X[k][i]


                avgq[int(y[k])-1][i] += X[k][i]**2

                
        # self.avg = np.true_divide(self.avg, css) 
        # self.var = avgq - log.(self.avg)**2
        # log_aself.sigma = (self.var)**0.5
        

                        
        self.avg = np.true_divide(self.avg, css)

        avgq = np.true_divide(avgq, css)

        self.var = avgq - (self.avg)**2

        self.sigma = (self.var)**0.5
        
        return self
    
        
    def predict(self, X):

        y_predict = np.zeros(len(X))

        i = 0

        logaprio = np.log(self.a_priori)
        
        for x in X:

            expPart = np.true_divide((x - self.avg)**2, self.var + 10**(-6))

            sumPart = np.sum(expPart, axis=1)

            varPart = np.sum(np.log(self.sigma + 10**(-6)), axis=1)

            res = (varPart + sumPart) - logaprio

            y_predict[i] = np.argmin(res) + 1

            i += 1
        
        return y_predict
    
    
    def score(self, X, y_truth):

        y_predict = self.predict(X)
        
        return ( np.sum([y_predict == y_truth]) ) / ( len(y_predict) )

predictions= {}
accuracies= {}

customNB= CustomNBClassifier()
customNB.fit(X_train,y_train)

predictions['customNB']=customNB.predict(x_test)
accuracies['customNB']=customNB.score(x_test,y_test)

bayes = GaussianNB()
bayes.fit(x_train, y_train)
predictions['bayes'] = bayes.predict(x_test)
accuracies['bayes'] = bayes.score(x_test, y_test)

print("\nF1 Score of the Gaussian Naive Bayes Classifier: \n")
print(f'\tMicro: {f1_score(y_test, predictions["bayes"], average = "micro")}')
print(f'\tMacro: {f1_score(y_test, predictions["bayes"], average = "macro")}\n')

print("\nAccuracy of the Gaussian Naive Bayes Classifier: \n")
print(f'{accuracies["bayes"]}')

"""Δοκιμάζοντας με cross validate:

## Με StandardScaler
"""

scaler= StandardScaler() 
scaledFeats = scaler.fit_transform (features)
x_train,x_test,y_train,y_test = train_test_split(scaledFeats,digits,test_size=0.3)

bayes = GaussianNB()
bayes.fit(x_train, y_train)
predictions['bayes'] = bayes.predict(x_test)
accuracies['bayes'] = bayes.score(x_test, y_test)

print("\nF1 Score of the Gaussian Naive Bayes Classifier: \n")
print(f'\tMicro: {f1_score(y_test, predictions["bayes"], average = "micro")}')
print(f'\tMacro: {f1_score(y_test, predictions["bayes"], average = "macro")}\n')

print("\nAccuracy of the Gaussian Naive Bayes Classifier: \n")
print(f'{accuracies["bayes"]}')

svm = SVC()
svm.fit(x_train, y_train)
predictions['svm'] = svm.predict(x_test)
accuracies['svm'] = svm.score(x_test, y_test)

print("\nF1 Score of the SVM Classifier: \n")
print(f'\tMicro: {f1_score(y_test, predictions["svm"], average = "micro")}')
print(f'\tMacro: {f1_score(y_test, predictions["svm"], average = "macro")}\n')

print("\nAccuracy of the SVM Classifier: \n")
print(f'{accuracies["svm"]}')

from sklearn import svm

clf_svm = svm.SVC(gamma='scale',kernel='rbf')
clf_svm.fit(x_train, y_train)
predictions['clf_svm'] = clf_svm.predict(x_test)
accuracies['clf_svm'] = clf_svm.score(x_test, y_test)

print("\nF1 Score of the SVM Classifier: \n")
print(f'\tMicro: {f1_score(y_test, predictions["clf_svm"], average = "micro")}')
print(f'\tMacro: {f1_score(y_test, predictions["clf_svm"], average = "macro")}\n')

print("\nAccuracy of the SVM Classifier: \n")
print(f'{accuracies["clf_svm"]}')

svm_kernel = ['linear', 'rbf', 'sigmoid']
svm_C = [1, 10, 100]
svm_tol = [1e-5, 1e-4, 1e-3]
pipe = Pipeline(steps=[('scaler', scaler), ('svm', svm)])
svm_estimator = TuneGridSearchCV(pipe, dict(
                                            svm__kernel=svm_kernel,
                                            svm__C=svm_C,
                                            svm__tol=svm_tol), cv=5, scoring='f1_macro', n_jobs=-1,
                                                                                                   verbose=1)
svm_estimator.fit(X_train_sample, y_train_sample)
preds = svm_estimator.predict(X_test)
print("Best parameters with Ray",svm_estimator.bestparams)

from sklearn.neighbors import KNeighborsClassifier



from sklearn import svm

clf_3nn = KNeighborsClassifier(n_neighbors=3)
clf_3nn.fit(x_train, y_train)
predictions['clf_3nn'] = clf_3nn.predict(x_test)
accuracies['clf_3nn'] = clf_3nn.score(x_test, y_test)

print("\nF1 Score of the KNN 3 Classifier: \n")
print(f'\tMicro: {f1_score(y_test, predictions["clf_3nn"], average = "micro")}')
print(f'\tMacro: {f1_score(y_test, predictions["clf_3nn"], average = "macro")}\n')

print("\nAccuracy of the KNN 3 Classifier: \n")
print(f'{accuracies["clf_3nn"]}')

randomf = RandomForestClassifier(max_depth=2, random_state=0)
randomf.fit(x_train, y_train)
predictions['randomf'] = randomf.predict(x_test)
accuracies['randomf'] = randomf.score(x_test, y_test)

print("\nF1 Score of the Random Forest  Classifier: \n")
print(f'\tMicro: {f1_score(y_test, predictions["randomf"], average = "micro")}')
print(f'\tMacro: {f1_score(y_test, predictions["randomf"], average = "macro")}\n')

print("\nAccuracy of Random Forest Classifier: \n")
print(f'{accuracies["randomf"]}')

customNB= CustomNBClassifier()
customNB.fit(X_train,y_train)

predictions['customNB']=customNB.predict(x_test)
accuracies['customNB']=customNB.score(x_test,y_test)

"""## Προσθέτωντας zero crossing rate παρατηρείται αύξηση του accuracy στον Bayes και SVM, και στο Random Forest. το KNN μένει ίδιο(σκέψου άλλα τέτοια επιπλέον χαρακτηριστικά που μπορούμε να προσθέσουμε)"""

mean_zcr=[]
var_zcr=[]
main_zcr=[]

for i in range(len(zcr)):
  mean_zcr.append(np.mean(zcr[i], axis=1))
  var_zcr.append(np.var(zcr[i],axis=1))
  main_zcr.append(np.stack((mean_zcr[i],var_zcr[i]),axis=-1))

main_zcr=(np.array(main_zcr)).reshape(len(zcr), 2)
features2= np.concatenate((features, main_zcr), axis=1)

scaler= StandardScaler() 
scaledFeats2 = scaler.fit_transform (features2)
x_train2,x_test2,y_train2,y_test2 = train_test_split(scaledFeats2,digits,test_size=0.3)

bayes = GaussianNB()
bayes.fit(x_train2, y_train2)
predictions['bayes'] = bayes.predict(x_test2)
accuracies['bayes'] = bayes.score(x_test2, y_test2)

print("\nF1 Score of the Gaussian Naive Bayes Classifier after adding zero crossing rate: \n")
print(f'\tMicro: {f1_score(y_test2, predictions["bayes"], average = "micro")}')
print(f'\tMacro: {f1_score(y_test2, predictions["bayes"], average = "macro")}\n')

print("\nAccuracy of the Gaussian Naive Bayes Classifier after adding zero crossing rate: \n")
print(f'{accuracies["bayes"]}')

from sklearn import svm

clf_svm = svm.SVC(gamma='scale',kernel='rbf')
clf_svm.fit(x_train2, y_train2)
predictions['clf_svm'] = clf_svm.predict(x_test2)
accuracies['clf_svm'] = clf_svm.score(x_test2, y_test2)

print("\nF1 Score of the SVM Classifier after adding zero crossing rate: \n")
print(f'\tMicro: {f1_score(y_test2, predictions["clf_svm"], average = "micro")}')
print(f'\tMacro: {f1_score(y_test2, predictions["clf_svm"], average = "macro")}\n')

print("\nAccuracy of the SVM Classifier after adding zero crossing rate: \n")
print(f'{accuracies["clf_svm"]}')

from sklearn.neighbors import KNeighborsClassifier



from sklearn import svm

clf_3nn = KNeighborsClassifier(n_neighbors=3)
clf_3nn.fit(x_train2, y_train2)
predictions['clf_3nn'] = clf_3nn.predict(x_test2)
accuracies['clf_3nn'] = clf_3nn.score(x_test2, y_test2)

print("\nF1 Score of the KNN 3 Classifier after adding zero crossing rate: \n")
print(f'\tMicro: {f1_score(y_test2, predictions["clf_3nn"], average = "micro")}')
print(f'\tMacro: {f1_score(y_test2, predictions["clf_3nn"], average = "macro")}\n')

print("\nAccuracy of the KNN 3 Classifier after adding zero crossing rate: \n")
print(f'{accuracies["clf_3nn"]}')

randomf = RandomForestClassifier(max_depth=2, random_state=0)
randomf.fit(x_train2, y_train2)
predictions['randomf'] = randomf.predict(x_test2)
accuracies['randomf'] = randomf.score(x_test2, y_test2)

print("\nF1 Score of the Random Forest  Classifier after adding zero crossing rate: \n")
print(f'\tMicro: {f1_score(y_test2, predictions["randomf"], average = "micro")}')
print(f'\tMacro: {f1_score(y_test2, predictions["randomf"], average = "macro")}\n')

print("\nAccuracy of Random Forest Classifier after adding zero crossing rate: \n")
print(f'{accuracies["randomf"]}')

customNB= CustomNBClassifier()
customNB.fit(X_train,y_train)

predictions['customNB']=customNB.predict(x_test)
accuracies['customNB']=customNB.score(x_test,y_test)

"""# Βήμα 8"""

# Commented out IPython magic to ensure Python compatibility.
# %matplotlib inline

SEED = 1
np.random.seed(SEED)
torch.manual_seed(SEED)

T = 20
L = 1000
N = 100

x = np.empty((N, L), 'int32')
x[:] = np.array(range(L)) + np.random.randint(-4 * T, 4 * T, N).reshape(N, 1)
data = np.sin(x / 1.0 / T).astype('float32')



input = torch.from_numpy(data[3:, :-31])
target = torch.from_numpy(data[3:, 31:])
test_input = torch.from_numpy(data[:3, :-31])
test_target = torch.from_numpy(data[:3, 31:])

class Sequence(torch.nn.Module):
    def __init__(self, hdim):
        super(Sequence, self).__init__()
        self.rnn = torch.nn.RNNCell(1, hdim)
        self.linear = torch.nn.Linear(hdim, 1)
        self.hdim = hdim

    def forward(self, input, future = 0):
        outputs = []
        
        h_t = torch.zeros((input.size(0),self.hdim))

        for i, input_t in enumerate(input.chunk(input.size(1), dim=1)):
            h_t = self.rnn(input_t,h_t)
            # apply the linear layer 
            output = self.linear(h_t)
            outputs.append(output)
        for i in range(future):# if we should predict the future
            
            # apply the RNN to the last value
            h_t = self.rnn(outputs[-1],h_t)
            output = self.linear(h_t)
            outputs += [output]
        outputs = torch.stack(outputs, 1).squeeze(2)
        return outputs

seq = Sequence(100)
criterion = torch.nn.MSELoss()
optimizer = torch.optim.LBFGS (seq.parameters(), lr=0.5)

for i in range(15):
    
    
    def closure():
        optimizer.zero_grad()
        out = seq(input)
        loss = criterion(out, target)
        print('\rSTEP:', i,'loss:', loss.item(), end='')
        loss.backward()
        return loss
    optimizer.step(closure)
    
    future = 1
    with torch.no_grad():
        pred = seq.forward(test_input, future=future)
        loss = criterion(pred[:, :-future], test_target)
        print(' test loss:', loss.item())
        y = pred.detach().numpy()
    

    fig, (ax1, ax2, ax3) = plt.subplots(3)
    plt.subplots_adjust(wspace=0.5, hspace=0.5, left=0.125, right=0.9, bottom=1.1, top=2.9)
     
    
    def draw(xi, yi, ycori, color):
        
        
        ax1.set_title('Input signal (sine)')
        ax1.set_xlabel('x (samples)')
        ax1.set_ylabel('y=sin(x/T)')
        ax1.plot(np.arange(input.size(1)), xi, color+':', linewidth = 2.0)

        
        ax2.set_title('Predicted signal (cosine)')
        ax2.set_xlabel('x (samples)')
        ax2.set_ylabel('y=sin(x/T)')
        ax2.plot(np.arange(input.size(1)), yi[:input.size(1)], color, linewidth = 2.0)
            
        
        ax3.set_title('Ground truth (cosine)')
        ax3.set_xlabel('x (samples)')
        ax3.set_ylabel('y=sin(x/T) ')
        ax3.plot(np.arange(input.size(1)), ycori, color, linewidth = 2.0)
    
    draw(test_input[0], y[0], test_target[0], 'r')
    draw(test_input[1], y[1], test_target[1], 'g')
    draw(test_input[2], y[2], test_target[2], 'b')
    plt.show()

"""# Βήμα 9. To parser να μπει σε .py"""

import numpy as np
import librosa
from glob import glob
import os

from sklearn.preprocessing import StandardScaler

def parser(directory):
    # Parse relevant dataset info
    files = glob(os.path.join(directory, '*.wav'))
    fnames = [f.split('/')[-1].split('.')[0].split('_') for f in files]
    ids = [f[2] for f in fnames]
    y = [int(f[0]) for f in fnames]
    speakers = [f[1] for f in fnames]
    _, Fs = librosa.core.load(files[0], sr=None)

    def read_wav(f):
        global Fs
        wav, fs = librosa.core.load(f, sr=None)
        return wav

    # Read all wavs
    wavs = [read_wav(f) for f in files]

    # Extract MFCCs for all wavs
    window = 30 * Fs // 1000
    step = window // 2
    frames = [librosa.feature.mfcc(wav, Fs, n_fft=window, hop_length=window - step, n_mfcc=13).T for wav in wavs]
    # Print dataset info
    print('Total wavs: {}'.format(len(frames)))

    # Standardize data
    scaler = StandardScaler()
    scaler.fit(np.concatenate(frames))
    for i in range(len(frames)):
        frames[i] = scaler.transform(frames[i])

    # Split to train-test
    X_train, y_train, spk_train = [], [], []
    X_test, y_test, spk_test = [], [], []
    test_indices = ['0', '1', '2', '3', '4']
    for idx, frame, label, spk in zip(ids, frames, y, speakers):
        if str(idx) in test_indices:
            X_test.append(frame)
            y_test.append(label)
            spk_test.append(spk)
        else:
            X_train.append(frame)
            y_train.append(label)
            spk_train.append(spk)

    return X_train, X_test, y_train, y_test, spk_train, spk_test

from google.colab import drive
#for part where 9 we get our data from google drive
drive.mount('/content/drive')

path = "/content/drive/My Drive/recordings"
X_train, X_test, y_train, y_test, spk_train, spk_test = parser(path)

"""## Using StratifiedShuffleSplit from scikit learn"""

from sklearn.model_selection import StratifiedShuffleSplit



sss = StratifiedShuffleSplit(n_splits=5, test_size=0.2)
y=y_train
y=np.array(y).reshape((2160,1))
X=np.zeros(2160)
X_train_copy=np.array(X_train)
sss.get_n_splits(X, y)
for train_index, validation_index in sss.split(X, y):
  X_train, X_val = X_train_copy[train_index], X_train_copy[validation_index]
  y_train, y_val = y[train_index], y[validation_index]

sss = StratifiedShuffleSplit(n_splits=5, test_size=0.2)
for train_index, test_index in sss.split(X_train, y_train):
  tmp_train, tmp_test = train_index,test_index
  X = X_train.copy()
y = y_train.copy()
X_train = [np.array(X[i]) for i in tmp_train]
y_train = [np.array(y[i]) for i in tmp_train]
X_dev = [np.array(X[i]) for i in tmp_test]
y_dev = [np.array(y[i]) for i in tmp_test]

"""# ΒΉΜΑ 10-11"""

pip install pomegranate

from pomegranate import *

def hmm(X, n_states, n_mixtures, gmm = True):
    X_stacked = np.vstack(X)

    dists = [] # list of probability distributions for the HMM states
    for i in range(n_states):
        if gmm:
            a = GeneralMixtureModel.from_samples(MultivariateGaussianDistribution, n_mixtures, np.float_(X_stacked))
        else:
            a = MultivariateGaussianDistribution.from_samples(np.float_(X_stacked))
        dists.append(a)

    trans_mat = np.reshape([0.5 if i==j or j==i+1 else 0 for i in range(n_states) for j in range(n_states)],(n_states,n_states)) 

    starts = np.zeros(n_states)x
    ends = np.zeros(n_states) 
    #init
    starts[0] = 1
    ends[-1] = 1


    model = HiddenMarkovModel.from_matrix(trans_mat, dists, starts, ends, state_names=['s{}'.format(i) for i in range(n_states)])

    model.fit(X, max_iterations=5)

    
    return model

"""# Βήμα 11"""

X_train_per_digit = []


for digit in range(10):


    X_tr_i = np.take(X_train, [i for i in range(len(X_train)) if y_train[i] == digit], axis=0)


    X_train_per_digit.append(X_tr_i)


def train(X, n_states,mixtures, gmm=True):
    models = []
    
    for i in X:


        models.append(hmm(i, n_states, mixtures))
    return models

"""# Βήμα 12"""

def evaluate(models, X_val, y_val, n):

    conf_matrix = np.zeros((10, 10)) 

    y_preds = np.zeros(n, dtype='int') 

    for i in range(n):
        logs = np.zeros(10)

        for j in range(10):
            logp, _ = models[j].viterbi(X_val[i]) 
            logs[j] = logp
            
        y_preds[i] = np.argmax(logs)
        conf_matrix[y_val[i], y_preds[i]] += 1
    acc = sum(y_preds == y_val) / n
    
    return acc, conf_matrix

"""# Βήμα 13

"""

accs = []
for states in [1,2, 3, 4]:
    for mixtures in [2, 3, 4, 5]:

        models = train(X_train_per_digit, states, mixtures)

        acc, _ = evaluate(models, X_dev, y_dev, len(X_dev))
        accs.append(acc)


print(accs)



"""# step 14

## 1 to 5
"""

class FrameLevelDataset(Dataset):
    def __init__(self, feats, labels):
      
        """
            feats: Python list of numpy arrays that contain the sequence features.
                   Each element of this list is a numpy array of shape seq_length x feature_dimension
            labels: Python list that contains the label for each sequence (each label must be an integer)
        """
        self.lengths = [x.shape[0] for x in feats ]
        self.feats = self.zero_pad_and_stack(feats)
        if isinstance(labels, (list, tuple)):
            self.labels = np.array(labels).astype('int64')

    def zero_pad_and_stack(self, x):
        """
            This function performs zero padding on a list of features and forms them into a numpy 3D array
            returns
                padded: a 3D numpy array of shape num_sequences x max_sequence_length x feature_dimension
        """
        

        feat=x[0].shape[1]
        pad=max(self.lengths)
        padded=np.zeros((len(x),pad,feat))

        for ctr,k in enumerate(x):
          padded[ctr,:len(k),:] = k

        return padded

    def __getitem__(self, item):
        return self.feats[item], self.labels[item], self.lengths[item]

    def __len__(self):
        return len(self.feats)


class BasicLSTM(nn.Module):
    def __init__(self, input_dim, rnn_size, output_dim, num_layers,drop_prob=0.4, bidirectional=False):
        super(BasicLSTM, self).__init__()
        self.bidirectional = bidirectional
        self.feature_size = rnn_size * 2 if self.bidirectional else rnn_size
        self.direction = 2 if self.bidirectional else 1
        self.output_dim = output_dim
        self.num_layers = num_layers
        self.input_dim = input_dim
        self.rnn_size = rnn_size
        self.lstm = nn.LSTM(input_dim,self.rnn_size, num_layers, dropout=drop_prob, batch_first=True, bidirectional=self.bidirectional)
        self.dropout = nn.Dropout(drop_prob)  ##if dropout
        self.fc = nn.Linear(self.feature_size, output_dim)

        
        

      
    def forward(self, x, lengths,hidden):
        """ 
            x : 3D numpy array of dimension N x L x D
                N: batch index
                L: sequence index
                D: feature index

            lengths: N x 1
         """
        
        
        


        lstm_out, hidden = self.lstm(x, hidden)

        batch_size=x.shape[0]

        lstm_out = lstm_out.contiguous().view(batch_size,-1, self.feature_size)

        out = self.fc(lstm_out)

        last_outputs = self.last_timestep(out,lengths,self.bidirectional)

        return last_outputs,hidden

    def last_timestep(self, outputs, lengths, bidirectional=False):
        """
            Returns the last output of the LSTM taking into account the zero padding
        """
        if bidirectional:
            forward, backward = self.split_directions(outputs)

            last_forward = self.last_by_index(forward, lengths)

            last_backward = backward[:, 0, :]

            return torch.cat((last_forward, last_backward), dim=-1)
  

        else:
            return self.last_by_index(outputs, lengths)

    @staticmethod
    def split_directions(outputs):
        direction_size = int(outputs.size(-1) / 2)

        forward = outputs[:, :, :direction_size]

        backward = outputs[:, :, direction_size:]
        return forward, backward

    @staticmethod
    def last_by_index(outputs, lengths):
        new_lengths=np.array([length-1 for length in lengths])

        idx = (torch.from_numpy(new_lengths)).view(-1, 1)

        idx = idx.expand(outputs.size(0),outputs.size(2)).unsqueeze(1)

        return outputs.gather(1, idx).squeeze()

    def init_hidden(self, batch_size):

        weight = next(self.parameters()).data

        hidden = (weight.new(self.direction*self.num_layers, batch_size, self.rnn_size).zero_(),
                      weight.new(self.direction*self.num_layers, batch_size, self.rnn_size).zero_())
        return hidden










train_data = FrameLevelDataset(X_train,y_train.flatten().tolist())

train_loader = DataLoader(train_data, shuffle=True, batch_size=32)
val_data = FrameLevelDataset(X_val,y_val.flatten().tolist())
val_loader = DataLoader(val_data,shuffle=True,batch_size= 32,drop_last=True) 

lengths=FrameLevelDataset(X_train,y_train).lengths

output_dim = 10
rnn_size = 22
num_layers = 2
















input_dim=13 
output_dim = 10

cc=0


epochs = 25

new_epochs=epochs
patience = 5

model = BasicLSTM(input_dim,rnn_size,output_dim,num_layers)

lr=0.001
optimizer = torch.optim.Adam(model.parameters(), lr=lr,weight_decay=0.001)

criterion=nn.CrossEntropyLoss()






stop=0
print = 100
valid_loss_min = np.Inf
loss_values_train = []
loss_values_val = []
model.train()
flag=0











batch=32



for i in range(epochs):

    loss_train=0.0 #at the time


    val_losss=0.0 #at the time


    h = model.init_hidden(batch)
    train_losses=[]




    for inputs, labels,lengths in train_loader:

        cc += 1

        h = tuple([e.data for e in h])

        model.zero_grad()

        output, h = model(inputs.float(),lengths,h)

        loss = criterion(output.squeeze(), labels.long())

        running_loss_train =+ loss.item() * batch

        train_losses.append(loss.item())
    
        loss.backward()
        optimizer.step()
        if cc%print == 0:
          val_h = model.init_hidden(batch)
          val_losses = []
          model.eval()
          for inp, lab,lens in val_loader:
              val_h = tuple([each.data for each in val_h])
              out, val_h = model(inp.float(),lens, val_h)
              val_loss = criterion(out.squeeze(), lab.long())
              val_losses.append(val_loss.item())
          model.train()

          if np.mean(val_losses) <= valid_loss_min:
              stop=0

              torch.save(model.state_dict(), './state_dict.pt')

              print('Validation loss(from {:.6f} to {:.6f})'.format(valid_loss_min,np.mean(val_losses)))


              valid_loss_min = np.mean(val_losses)
          else:
              stop+=1
              if (stop>=patience):
                new_epochs=i
                flag=1

    model.eval()


    val_h = model.init_hidden(batch) 


    validation_losses=[]


    for inp, lab,lens in val_loader:


              val_h = tuple([each.data for each in val_h])


              out, val_h = model(inp.float(),lens, val_h)

              val_loss = criterion(out.squeeze(), lab.long())


              validation_losses.append(val_loss.item())


              val_losss=+ val_loss.item() * batch
              
    model.train()


    print("Epoch: {}/{}".format(i+1, epochs),"Step: {}".format(cc),"Train Loss: {:.6f}".format(loss.item()))



    loss_values_train.append(np.mean(train_losses))
    
    loss_values_val.append(np.mean(validation_losses))    
plt.plot(range(new_epochs),loss_values_train)
plt.plot(range(new_epochs),loss_values_val)

from sklearn.metrics import confusion_matrix
def evaluate_model():


  model.load_state_dict(torch.
                        load('./state_dict.pt'))
  


  batch_size=20
  test_data=FrameLevelDataset(X_test
                              ,y_test)
  
  test_loader = DataLoader(test_data, shuffle=False, 
                           batch_size=20)

  validation_data=FrameLevelDataset(X_val,y_val.flatten().tolist())

  validation_loader = DataLoader(validation_data, shuffle=False, batch_size=20)






  test_losses = []
  validation_losses = []
  num_correct = 0
  h = model.init_hidden(batch_size)
  correct=0
  y_pred_test=[]
  y_pred_val=[]



  model.eval()
  for inputs, labels,lengths in test_loader:
      h = tuple([each.data for each in h])


      output, h = model(inputs.float(),lengths, h)
      
      test_loss = criterion(output.squeeze(), labels.long())

      test_losses.append(test_loss.item())

      pred = output.data.max(1)[1]  

      y_pred_test.append(pred.tolist())
      correct += pred.eq(labels.data).sum()

  test_loss /= len(test_loader.dataset)
  print('\nTest set: Average loss: {:.6f}, Accuracy: {}/{} ({:.0f}%)\n'.format(
          np.mean(test_losses), correct, len(test_loader.dataset),
          
          100. * correct / len(test_loader.dataset)))
  
  
  correct=0

  num_correct=0

  h = model.init_hidden(batch_size)


  for inputs, labels,lengths in validation_loader:

      h = tuple([each.data for each in h])

      output, h = model(inputs.float(),lengths, h)

      validation_loss = criterion(output.squeeze(), labels.long())

      validation_losses.append(validation_loss.item())

      pred = output.data.max(1)[1]  


      y_pred_val.append(pred.tolist())

      correct += pred.eq(labels.data).sum()

  validation_loss /= len(validation_loader.dataset)

  print('\nValidation set: Average loss: {:.6f}, Accuracy: {}/{} ({:.0f}%)\n'.format(
      
          np.mean(validation_losses), correct, len(validation_loader.dataset),

          100. * correct / len(validation_loader.dataset)))
  





  conf1=confusion_matrix(y_test,np.array(y_pred_test).flatten())


  conf2=confusion_matrix(y_val,np.array(y_pred_val).flatten())


  models = [conf1 , conf2]

  names = ['val', 'test']

  for m in range(2):

    plt.imshow(models[m],interpolation = 'nearest',cmap = 'Reds')

    for (i, j), z in np.ndenumerate(models[m]):


      plt.text(j, i, z, ha='center', va='center')

    plt.title("Confusion Matrix")

    plt.xlabel(names[m])

    plt.ylabel("ground label")
    plt.show()
  
evaluate_model()

"""## 7"""

batch_size=32
train_data = FrameLevelDataset(X_train,y_train.flatten().tolist())


train_loader = DataLoader(train_data, shuffle=True, batch_size=batch_size,drop_last=True)

val_data = FrameLevelDataset(X_val,y_val.flatten().tolist())

val_loader = DataLoader(val_data,shuffle=True,batch_size= batch_size,drop_last=True) 

lengths=FrameLevelDataset(X_train,y_train).lengths

output_dim = 10
rnn_size = 16
num_layers = 2
input_dim=6
counter=0
model = BasicLSTM(input_dim,rnn_size,output_dim,num_layers,bidirectional=True)

lr=0.005
criterion=nn.CrossEntropyLoss()
optimizer = torch.optim.Adam(model.parameters(), lr=lr,weight_decay=0.001)
epochs = 45
print_every = 100
valid_loss_min = np.Inf
loss_values_train = []
loss_values_val = []
model.train()
for i in range(epochs):
    train_losses=[]
    running_loss_train=0.0
    running_loss_val=0.0
    h = model.init_hidden(batch_size)
    
    for inputs, labels,lengths in train_loader:
        counter += 1
        h = tuple([e.data for e in h])
        model.zero_grad()
        output, h = model(inputs.float(),lengths,h)
        loss = criterion(output.squeeze(), labels.long())
        running_loss_train =+ loss.item() * batch_size
        train_losses.append(loss.item())
        loss.backward()
        optimizer.step()
        if counter%print_every == 0:
          val_h = model.init_hidden(batch_size)
          val_losses = []
          model.eval()
          for inp, lab,lens in val_loader:
              val_h = tuple([each.data for each in val_h])
              out, val_h = model(inp.float(),lens, val_h)
              val_loss = criterion(out.squeeze(), lab.long())
              val_losses.append(val_loss.item())
          model.train()

          if np.mean(val_losses) <= valid_loss_min:
              torch.save(model.state_dict(), './state_dict.pt')
              print('Validation loss decreased ({:.6f} --> {:.6f}).  Saving model ...'.format(valid_loss_min,np.mean(val_losses)))
              valid_loss_min = np.mean(val_losses)
    model.eval()
    val_h = model.init_hidden(batch_size) 
    for inp, lab,lens in val_loader:
              val_h = tuple([each.data for each in val_h])
              out, val_h = model(inp.float(),lens, val_h)
              val_loss = criterion(out.squeeze(), lab.long())
              val_losses.append(val_loss.item())
              running_loss_val=+ val_loss.item() * batch_size
    model.train()
    print("Epoch: {}/{}...".format(i+1, epochs),
            "Step: {}...".format(counter),
            "Train Loss: {:.6f}...".format(loss.item()))

    loss_values_train.append(np.mean(val_losses))
    loss_values_val.append(np.mean(train_losses))    
plt.plot(range(epochs),loss_values_train)
plt.plot(range(epochs),loss_values_val)

"""Initialization"""