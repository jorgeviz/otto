""" Script to 
"""
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib import style
import datetime
import pandas as pd
import sys

style.use('fivethirtyeight')

# File name to open
global FNAME
FNAME = None

# Create figure
fig = plt.figure()
plt.xlabel('Time (date)')
plt.ylabel('Price')

def datefy(x):
    """ Method to convert string into datetime
    """
    return datetime.datetime.strptime(x, "%Y-%m-%dT%H:%M:%S+00:00")

def animate(i):
    """ Function to animate plot live
    """
    try:
        graph_data = pd.read_csv('data/'+FNAME+'.csv')
    except IOError:
        print('Does not exist file!')
        sys.exit()
    graph_data['last'] = graph_data['last'].apply(lambda x: float(x))
    graph_data['created_at'] = graph_data['created_at'].apply(lambda x: datefy(x))
    # Create lines
    x_s = graph_data.tail(50)['created_at'].tolist()
    y_s = graph_data.tail(50)['last'].tolist()
    # Clear picture
    plt.gcf().clear()
    # Plot first
    #plt.subplot(211)
    plt.plot(x_s, y_s, 'b')
    plt.title('Altcoins Behaviour ({})'.format(FNAME))
    # simultaneous plot
    # plt.plot(xs, ys, 'bo', xs, [int(_y)+1 for _y in ys], 'k')
    #plt.axis([x_s[0], x_s[-1], min(y_s), max(y_s)])
    # Plot Second
    """
    plt.subplot(212)
    plt.plot(xs, ys, 'r')
    plt.axis([xs[0], xs[-1], 0, 10.0])
    plt.title('Altcoins Behaviour 2')
    """

if __name__ == '__main__':
    # Read file name from params
    if len(sys.argv) == 1:
        print('Currency to plot missing!! \n Run  python -m otto.plot btc_mxn')
        sys.exit()
    #global FNAME
    FNAME = str(sys.argv[1])  # Fetching filename from argv
    print('Graphing:  Altcoins Behaviour ({})'.format(FNAME))
    # Animation function (figure, animation_function, fps[ms])
    ani = animation.FuncAnimation(fig, animate, interval=1000)
    plt.show()
