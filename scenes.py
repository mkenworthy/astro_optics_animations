import numpy as np
'''Scenes - simple smooth transitions of a variable for making better animations'''

class Act:
    def __init__(self, start, end, dt=1, met="lin", c=2.):
        'Act - a variable starting at value start, changing to value end, after time dt, interpolating with method met'
        self.start = start
        self.end = end
        self.met = met
        self.c = c
        self.dt = dt
        
    def at(self, t):
        'print value of the variable at time t from start of Act'
        # clamp t outside dt to the limits
        if t < 0:
            t = self.start
            print("WARN: t was less than 0, setting it to 0")
            
        if t > self.dt:
            t = self.end
            print('WARN: t was larger than the length of the Act, setting to {}'.format(self.end))
            
        # normalise t values so that they lie between 0 and 1
        tn = t/self.dt

        # definte the different easing methods
        if self.met=="sig":
            y = 1./(1.+np.exp(-self.c*(tn-0.5)))
        elif self.met=="pow":
            y = tn**self.c
        else:
            y = tn
        # convert the y 0 to 1 values back to start and end values
        val = (y * (self.end - self.start)) + self.start
        
        return val

class Stage:
    def __init__(self):
        self.acts = []
            
    def add(self, Act):
        self.acts.append(Act)
        
    def total_time(self):
        total_time = 0.
        for a in self.acts:
            total_time += a.dt
        return total_time
    
    def begin_acts(self):
        'which Act in the list does time t reside?'
        # act                0    1    2
        # dt                2.1  1.5  3.0
        # begin_acts() 0.0  2.1  3.6  6.6
        times = [0.]
        end_time = 0.
        for a in self.acts:
            end_time+=a.dt
            times.append(end_time)
            
        return np.array(times)
        
    def t(self,t):
        'evaluate Scene for a numpy array of times. if time is bigger than total_time, it returns Scene at total_time'
        t=np.array(t).flatten()

        beg_acts = self.begin_acts()

        closest_act = t[:,np.newaxis]-beg_acts

        # the location and smallest positive value in each row tells you the Act postion and the time t to look up
        nonegs = np.ma.masked_less(closest_act, 0)
        
        act_indices = np.ma.argmin(nonegs,axis=1)
        act_t_values = np.ma.min(nonegs,axis=1)

        out = np.zeros_like(act_t_values, dtype=np.float32)

        # if you have a time t that is greater than the length of the total Stage, tweak the values
        # so that you clamp to the largest time
        nacts = beg_acts.size-1
        toobig = (act_indices >= nacts)

        act_indices[toobig] = nacts-1
        
        # the last act is
        last_act = self.acts[-1]
        act_t_values[toobig] = last_act.dt
        
        for i, (actpos, t) in enumerate(zip(act_indices,act_t_values)):
            out[i] = self.acts[actpos].at(t)
            
        return out


class Play:
    def __init__(self):
        self.stages = []
            
    def add(self, Stage):
        self.stages.append(Stage)

    def timeline(self):
        'plot out all Scenes together to give an overview of the timelines'
        fig, ax = plt.subplots()
        time = np.linspace(0,self.longest_time(),1000)
        for a in self.stages:
            t = time[(time<a.total_time())]
            ax.plot(t,a.t(t))

        plt.draw()
        plt.show()
        return 0

    def longest_time(self):
        '''calculates the longest time of all the Stages listed in the Play'''
        longest_time = 0.
        for a in self.stages:
            # find longest time of all the Stages
            if (a.total_time() > longest_time):
                longest_time = a.total_time()

        return longest_time

    def tidyup(self):
        '''adds constant value Acts to brings up all the other Stages to the longest time'''

#        print('longest time is {}'.format(self.longest_time()))
        longest_time = self.longest_time()
        for s in self.stages:
            stage_time = s.total_time()
            if (stage_time < longest_time):
#                print("adding a time delta to this one")
                dt = longest_time - stage_time
                last_value = s.t(stage_time)
                s.add(Act(last_value,last_value,dt))

if __name__ == "__main__":
    import matplotlib.pyplot as plt

    # "All the world’s a stage,
    #  And all the men and women merely players;"
    #          --- Jaques from "As You Like It" by Bill S.


    p = Stage()
    p.add(Act(0,2,2.1))
    p.add(Act(2,0,1.5))
    p.add(Act(0,1,3.0))
    print('testing going beyond the total_time() of a Stage')
    print('total time is {}'.format(p.total_time()))
    print(p.begin_acts())
    td = np.arange(0.,p.total_time()+1.,0.2)
    print(td, p.t(td))
    print('Last few values should be the same')

    print('multiple stages')
    a = Stage()
    a.add(Act(1,2,1))
    a.add(Act(2,-1,8,'pow',0.1))
    a.add(Act(-1,0,10))
    a.add(Act(0,np.pi,5))
    a.add(Act(np.pi,2,.5))

    a.begin_acts()

    a.total_time()

    b = Stage()
    b.add(Act(0,8,a.total_time()-2.))

    c = Stage()
    c.add(Act(4,2,a.total_time()-5.))

    # a Play consists of all the Stages you've made. This is so that you
    # can apply methods to all the Stages at once, useful when you're changing
    # one variable at a time, and you want to bring all the others up to the same time
    
    play = Play()
    play.add(a)
    play.add(c)
    play.add(b)
    play.tidyup()

    
    print('multiple stages')
    a = Stage()
    a.add(Act(1,2,1))
    a.add(Act(2,-1,8,'pow',0.1))
    a.add(Act(-1,0,10))
    a.add(Act(0,np.pi,5))
    a.add(Act(np.pi,2,.5))

    a.begin_acts()

    a.total_time()

    b = Stage()
    b.add(Act(0,8,a.total_time()-2.))

    c = Stage()
    c.add(Act(4,2,a.total_time()-5.))

    # a Play consists of all the Stages you've made. This is so that you
    # can apply methods to all the Stages at once, useful when you're changing
    # one variable at a time, and you want to bring all the others up to the same time
    
    play = Play()
    play.add(a)
    play.add(c)
    play.add(b)
    play.timeline()

    play.tidyup()
    play.timeline()

