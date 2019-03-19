from sklearn import tree
X = [[0, 0], [1, 1], [2,2]]
Y = [0, 1, 2]
clf = tree.DecisionTreeClassifier()
clf = clf.fit(X, Y)

print(clf.predict([[3., 3.]]))