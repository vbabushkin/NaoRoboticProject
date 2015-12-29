__author__ = 'vahan'

import pickle
def save_obj(obj, name ):
    with open(name + '.pkl', 'wb') as f:
        pickle.dump(obj, f, pickle.HIGHEST_PROTOCOL)

def load_obj(name ):
    with open(name + '.pkl', 'r') as f:
        return pickle.load(f)

    
dict={'green': [([70, 50, 50],[100, 255, 255]), ([70, 50, 51], [100, 255, 255]), ([70, 51, 50], [100, 255, 255]), ([70, 51, 51],[100, 255, 255]), ( [71, 50, 50],     [100, 255, 255]  ), ( [71, 50, 51],     [100, 255, 255]  ), ( [71, 51, 50],     [100, 255, 255]  ), ( [71, 51, 51],     [100, 255, 255]  )]}

probList=[0.2,0.7,0.9,0.9,0.5,0.6,0.4,0.1]


newdict={}

save_obj(dict, "myDict" )
save_obj(probList, "myProbList" )

newdict=load_obj("myDict" )
newproblist=load_obj("myProbList" )

print newdict
print newdict["green"][0]
print newproblist
