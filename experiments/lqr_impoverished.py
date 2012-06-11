import td
import examples
import numpy as np
import matplotlib.pyplot as plt
import dynamic_prog as dp
import util
import features
import policies
from joblib import Parallel, delayed
from task import LinearLQRValuePredictionTask
import itertools

gamma=0.9
sigma = np.zeros((4,4))
sigma[-1,-1] = 0.01

dt = 0.1
#mdp = examples.MiniLQMDP(dt=dt)
mdp = examples.PoleBalancingMDP(sigma=sigma, dt=dt)

phi = features.squared_diag()


n_feat = len(phi(np.zeros(mdp.dim_S)))
theta_p,_,_ = dp.solve_LQR(mdp, gamma=gamma)
print theta_p
theta_p = np.array(theta_p).flatten()

policy = policies.LinearContinuous(theta=theta_p, noise=np.zeros((1,1)))
#theta0 =  10*np.ones(n_feat)
theta0 =  0.*np.ones(n_feat)

task = LinearLQRValuePredictionTask(mdp, gamma, phi, theta0, policy=policy, normalize_phi=True)
task.seed=0
#phi = task.phi
print "V_true", task.V_true
print "theta_true"
theta_true = phi.param_forward(*task.V_true)
print theta_true
#task.theta0 = theta_true
methods = []

#for alpha in [0.01, 0.005]:
#    for mu in [0.05, 0.1, 0.2, 0.01]:
#alpha = 0.1
alpha = 0.005
mu = 0.1
gtd = td.GTD(alpha=alpha, beta=mu*alpha, phi=phi)
gtd.name = r"GTD $\alpha$={} $\mu$={}".format(alpha, mu)
gtd.color = "r"
methods.append(gtd)

#for alpha in [.005,0.01,0.02]:
#    for mu in [0.01, 0.1]:
alpha, mu = 0.01, 0.1
gtd = td.GTD2(alpha=alpha, beta=mu*alpha, phi=phi)
gtd.name = r"GTD2 $\alpha$={} $\mu$={}".format(alpha, mu)
gtd.color = "orange"
#methods.append(gtd)


alpha = .005
td0 = td.LinearTD0(alpha=alpha, phi=phi, gamma=gamma)
td0.name = r"TD(0) $\alpha$={}".format(alpha)
td0.color = "k"
methods.append(td0)

#for alpha in [0.005, 0.01, 0.02]:
#    for mu in [0.01, 0.1]:
for alpha, mu in [(.01,0.1)]:
    tdc = td.TDC(alpha=alpha, beta=alpha*mu, phi=phi, gamma=gamma)
    tdc.name = r"TDC $\alpha$={} $\mu$={}".format(alpha, mu)
    tdc.color = "b"
#    methods.append(tdc)

#methods = []
#for eps in np.power(10,np.arange(-1,4)):
eps=100
lstd = td.LSTDLambda(lam=0, eps=eps, phi=phi, gamma=gamma)
lstd.name = r"LSTD({}) $\epsilon$={}".format(0, eps)
lstd.color = "g"
methods.append(lstd)
#
#methods = []
#for alpha in [0.01, 0.02, 0.03]:
#alpha = .2
alpha=.04
rg = td.ResidualGradient(alpha=alpha, phi=phi, gamma=gamma)
rg.name = r"RG $\alpha$={}".format(alpha)
rg.color = "brown"
methods.append(rg)

l=20000
error_every=200


def run(alpha, mu):
    np.seterr(all="ignore")
    m = td.TDC(alpha=alpha, beta=mu*alpha, phi=task.phi, gamma=gamma)
    mean, std, raw = task.avg_error_traces([m], n_indep=2, n_samples=l, error_every=error_every, criterion="RMSPBE", verbose=False)
    val = np.mean(mean)#[0, -400:])
    return val

params = itertools.product(list(np.arange(0.001, .01, 0.001)) + list(np.arange(0.01, 0.1, 0.01)) + [0.1, 0.2, 0.3, 0.4, 0.5], [0.01,0.01, 0.1, 0.5,1,2,4,8,16, 32, 64])
#params = [(0.001, 0.5)]
k = (delayed(run)(*p) for p in params)
res = Parallel(n_jobs=-1, verbose=11)(k)
import pickle
with open("data/impoverished_TDC_gs.pck") as f:
    pickle.dump(dict(params=params, res=res), f)
print zip(params, res)
#plt.plot(params, res, "*-")
#plt.show()
"""
mean, std, raw = task.avg_error_traces(methods, n_indep=2,
    n_samples=l, error_every=error_every,
    criterion="RMSPBE",
    verbose=True)

plt.figure(figsize=(18,12))
plt.ylabel(r"$\sqrt{MSPBE}$")
plt.xlabel("Timesteps")
plt.title("Impoverished LQR")
for i, m in enumerate(methods):
    #plt.errorbar(range(0,l,error_every), mean[i,:], yerr=std[i,:], errorevery=10000/error_every, label=m.name)
    plt.errorbar(range(0,l,error_every), mean[i,:], yerr=std[i,:], label=m.name)
plt.legend()
plt.show()
"""