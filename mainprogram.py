import snap
import csv
import hashlib
import graphviz
import networkx as nx
import matplotlib.pyplot as plt

#Function which converts string to an ID
def hashName(string):
	h = hashlib.md5()
	h.update(string.encode("utf-8"))
	return int(str(int(h.hexdigest(), 16))[2:11])

#Creating new network
N1 = snap.TNEANet.New()

#list for labels.
labelList = []
#list for nodes
NodeList = []

#Change this value to determine how many drugs are used (up to 640)
AmountOfDrugNodes = 3

#Adding nodes and edges to network by reading the CSV
with open("dataset.csv", "r") as file:
	reader = csv.reader(file)
	header = next(reader)
	drugNodeCount = 0
	sideEffectCount = 0
	#Loops through all entries in csv file
	for row in reader:

		if drugNodeCount <= AmountOfDrugNodes:

			#Adds a drug node and a side effect node
			drugNode = row[0]
			nodeID = hashName(drugNode)
			
			try:
				#add drug node
				dataReturn = N1.AddNode(nodeID)
				drugNodeCount = drugNodeCount + 1
				if drugNodeCount>AmountOfDrugNodes:
					N1.DelNode(nodeID)
					break
				print "Succesfully added Drug Node - {0} ID: {1}".format(row[0], nodeID)
				labelList.append(row[0])
				NodeList.append(nodeID)

			except Exception as e:
				#duplicate drug node
				pass

			sideEffectNode = row[1]
			SEnodeID = hashName(sideEffectNode)
			try:
				#add side effect node
				dataReturn = N1.AddNode(SEnodeID)
				print "Succesfully added Side Effect Node - {0} ID: {1}".format(row[1], SEnodeID)
				sideEffectCount = sideEffectCount + 1
				labelList.append(row[2])
				NodeList.append(SEnodeID)
			except Exception as e:
				#duplicate side effect node
				pass


			try:
				#Adds an edge between a drug node and a side effect node
				dataReturn = N1.AddEdge(nodeID, SEnodeID, -1)
				print "Succesfully added edge between {0} and {1}".format(nodeID, SEnodeID)
			except Exception as e:
				pass

		else:
			break
	
	print "Drug Nodes : {0} , Side Effect Nodes : {1}".format(AmountOfDrugNodes, sideEffectCount)


#function which saves a .dot file to be rendered later.
def saveGraph(network, listOfLabels, graphName, graphDesc):
	labels = snap.TIntStrH()
	i=0
	for NI in network.Nodes():
		labels[NI.GetId()] = listOfLabels[i]
		i = i+1

	snap.SaveGViz(network, graphName, graphDesc, labels)


#function which takes a black and white graph and adds colours
def colourGraph(graphName):
	with open("{0}.dot".format(graphName), 'r') as dotFile:
		with open("{0}colour.dot".format(graphName), 'w') as outFile:
			i = 0;
			for line in dotFile:
				if '[label="' in line:
					nodeID = NodeList[i]
					NodePointer = N1.GetNI(NodeList[i])
					inDegree = NodePointer.GetInDeg()

					#rewrite for different drug amounts
					if inDegree == 0:
						outFile.write('	{0} [label = "{1}", style=filled, fillcolor="{2}"];\n'.format(nodeID, labelList[i], "#84b5e0")) #b8e8a2
					elif inDegree == 1:
						outFile.write('	{0} [label = "{1}", style=filled, fillcolor="{2}"];\n'.format(nodeID, labelList[i], "#ffdede")) 
					elif inDegree == 2:
						outFile.write('	{0} [label = "{1}", style=filled, fillcolor="{2}"];\n'.format(nodeID, labelList[i], "#ff9696"))
					elif inDegree == 3:
						outFile.write('	{0} [label = "{1}", style=filled, fillcolor="{2}"];\n'.format(nodeID, labelList[i], "#ff2b2b"))  
					else:
						outFile.write('	{0} [label = "{1}", style=filled, fillcolor="{2}"];\n'.format(nodeID, labelList[i], "#990000")) 

					i = i+1
				else:
					outFile.write(line)

	graphviz.render('neato', 'png', "{0}colour.dot".format(graphName))

#Function which gets the amount of very common, common, rare
def getCommonalities(network, veryCommonBoundry, RareNumber):
	vcomCount = 0
	comCount = 0
	rarecount = 0
	i=0
	for NI in network.Nodes():
		NodePointer = network.GetNI(NodeList[i])
		inDeg = NodePointer.GetInDeg()
		if inDeg==0:
			pass
		elif inDeg<RareNumber:
			rarecount=rarecount+1
		elif inDeg < veryCommonBoundry:
			comCount = comCount+1
		else:
			vcomCount = vcomCount+1
		
		i=i+1  

	print "Amount of rare side effects (<{0} drugs in common) : {1}".format(RareNumber, rarecount)
	print "Amount of common side effects (<{0} and >{2} drugs in common) : {1}".format(veryCommonBoundry, comCount, RareNumber)	
	print "Amount of very common side effects (>={0} drugs in common) : {1}".format(veryCommonBoundry, vcomCount)


def checkInArray(number, array):
	found = False
	for i in range(len(array)):
		if array[i]==number:
			found = True
	return found		

#For Harry
def findMostCommonDrug(network, numberOfSideEffects):
	position = 0
	i = 0
	j = 0
	largestDegree = 0

	topSideEffectNameList = []
	topSideEffectDegreeList = []
	topSideEffectPosition = []

	for NI in network.Nodes():
		NodePointer = network.GetNI(NodeList[i])
		inDegree = NodePointer.GetInDeg()
		if inDegree>largestDegree:
			largestDegree = inDegree
			position = i
		
		i=i+1  

	topSideEffectNameList.append(labelList[position])
	topSideEffectDegreeList.append(largestDegree)
	topSideEffectPosition.append(position)

	lastPosition = 0
	
	while len(topSideEffectNameList) < numberOfSideEffects:

		i=0
		position =0
		largestDegree = 0
		

		for NI in network.Nodes():
			NodePointer = network.GetNI(NodeList[i])
			inDegree = NodePointer.GetInDeg()
			check = checkInArray(i, topSideEffectPosition)
			if inDegree > largestDegree and inDegree<=topSideEffectDegreeList[lastPosition] and check == False:
				largestDegree = inDegree
				position = i
			
			i=i+1

		topSideEffectNameList.append(labelList[position])
		topSideEffectDegreeList.append(largestDegree)
		topSideEffectPosition.append(position)
		lastPosition = lastPosition+1

	print "----{0} Most common side effects----".format(numberOfSideEffects)
	print "Rank\tName\tDegree"
        
	for j in range(len(topSideEffectNameList)):
		print "{0}\t{1} : {2}".format(j+1,topSideEffectNameList[j], topSideEffectDegreeList[j])



#Calling functions above that saves a DOT file then draws a graph.
saveGraph(N1, labelList, "GraphOf3Drugs.dot", "A graph of 3 drugs and their side effects")
colourGraph("GraphOf3Drugs")

#snap.SaveEdgeList(N1, 'network_edgelist.txt')


#getCommonalities(N1, 100, 5)


#findMostCommonDrug(N1, 25)

# g = nx.read_edgelist('network_edgelist.txt', create_using=nx.Graph(), nodetype=int)
# print nx.info(g)
# sp=nx.spring_layout(g)
# plt.axis('off')
# nx.draw_networkx(g, pos=sp,with_labels=False,node_size=35)
# plt.show()