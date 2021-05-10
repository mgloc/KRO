import matplotlib.pyplot as plt
import numpy as np
import m_star

def scatterplot(ax,x_data, y_data, x_label="", y_label="", title="", color = "r", yscale_log=False):



    # Plot the data, set the size (s), color and transparency (alpha)
    # of the points
    ax.scatter(x_data, y_data, s = 10, color = color, alpha = 0.75)

def scatter_a_matrix(matrice,ax) :
    if matrice == [] or matrice == [[]]:
        raise NameError("An empty matrix was given")
    n = len(matrice)
    m = len(matrice[0])

    x_data = []
    y_data = []

    for i in range(n) :
        for j in range(m) :
            if matrice[i][j] == 1 :
                x_data.append(j)
                y_data.append(n-i)
    
    scatterplot(ax=ax,x_data=x_data,y_data=y_data,color="b")
    plt.xlim(0,m)
    plt.ylim(0,n)

def scatter_a_path(path,ax,n,m):

    x_data = []
    y_data = []
    for elem in path :
        y = elem[0][0]
        x = elem[0][1]

        x_data.append(x)
        y_data.append(n-y)
    
    scatterplot(ax=ax,x_data=x_data,y_data=y_data,color="r")
    plt.xlim(0,m)
    plt.ylim(0,n)


if __name__ == "__main__":

    _, ax = plt.subplots()

    graph = m_star.Graph((7,10))
    graph.fill_with_matrix(m_star.matrice_test)
    path = m_star.pathfinder((0,0),(6,9),graph)

    scatter_a_matrix(m_star.matrice_test,ax)
    scatter_a_path(path,ax,7,10)

    plt.show()