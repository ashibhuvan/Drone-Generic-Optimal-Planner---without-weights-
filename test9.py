from pandas import DataFrame
import matplotlib.pyplot as plt
from matplotlib.pyplot import draw,show, ion
from matplotlib.animation import FuncAnimation
from sklearn.cluster import KMeans
import math
import random
import numpy as np
import time as tm
import threading
import queue 

#from Tkinter import *

lock = threading.Lock()


class UAV(object):
	"""docstring for UAV"""
	def __init__(self, arg):
		super(UAV, self).__init__()
		self.arg = arg
		self.location = [50,50]
		self.id = arg
		#missedq ue of points
		self.missed = []
		#use battery as a measurement of distance, way more pratical , make function to change battery on hovering
		#need to make desicion to if drone has to wait for battery 
		self.battery = 900
		self.que = []
		self.que_sorted=[]
		self.speed = 10
		self.visited = []
		#self.animation_visited=[]
		self.animation_visited = queue.Queue(maxsize=30)
		self.flag = False
		self.boot = 1

	def set(self, object):
		self.que = object.copy()


	def __str__(self):
		return str(self.que)


	def update_que(self,time):
		#this is called when the drone has determined it reachthe next point
		#update points visited, drone locaction and battery, and then update the overall que

	
			#print("Drone " + str(self.id) + "has visited " )
			#print(self.que_sorted[0])
			
		self.battery = self.battery - self.que_sorted[0][4] * self.speed
		self.location[0],self.location[1] = self.que_sorted[0][0],self.que_sorted[0][1]
		#determined we can visit that point, adding to the visited list
		self.visited.append(self.que_sorted[0])

		#adding the next visited to the graphing algorithim
		
		#self.animation_visited.append(self.que_sorted[0])
		#going to use a QUEU instead of a list
		self.animation_visited.put(self.que_sorted[0])

		#remove point from que
		temp = self.que_sorted.copy()
	
		
		temp.pop(0)
		self.que_sorted = temp.copy()
		
		
		
		
		
		print("\n")
		#print(self.que_sorted[0])
		for i in self.que_sorted:
			i[2] = i[2] - time
			if i[2] <= 0:
				#we lost a point
				self.missed.append(i)

		temp2 = [x for x in self.que_sorted if x[2] >=0]
		self.que_sorted =[]
		self.que = []
		for i in temp2:
				self.que_sorted.append(i[:3])
				self.que.append(i[:3])


		

		return True	
		#que has been updated to all the active points

		
			

		#need to change the time left on the drones

		
		#above we have added the visited point to visited and then popped it from que
		#we have to now generate new points and new ques, if a another point is immedietly generated after that one is visited,
		#it will be in a random location so we need to update the division of points again. 
		#call kmeans that generates another point, redivides the clusters

		#kmeans needs to assign to the drones their individual sets

		

	def run(self):
		print("Drone 1 Running\n")
		
		for i in range(30):
			tm.sleep(1)
			lock.acquire()
			try:
				
				if not self.flag:
					if self.scheduling():

						(can_reach_bool,time) = self.can_reach(self.que_sorted)

						if can_reach_bool:
							if self.update_que(time):
								#we have determined we can reach the point
								#and have updated all the variables
								visited_copy = []
								missed_copy = []
								for i in self.visited:
									visited_copy.append(i[:2])
								for i in self.missed:
									missed_copy.append(i[:2])
								print("Drone ",self.id," is to visit", visited_copy[-1][0],",", visited_copy[-1][1]," it has visited: ",len(visited_copy)," and it has missed, ", len(missed_copy)) 
								print("\nvisited: ",visited_copy)
								print("\n")
						elif not can_reach_bool and time == -1:
							
							#point was not able to be visited causeq of time, has been trashed
							visited_copy = []
							missed_copy = []
							for i in self.visited:
								visited_copy.append(i[:2])
							for i in self.missed:
								missed_copy.append(i[:2])
							print("Drone ",self.id," could not visit due to time:", missed_copy[-1][0],",", missed_copy[-1][0]," will move one")
							print(self.missed)
							temp_collect = self.que_sorted.copy()
							temp_collect2 = self.que.copy()

							temp_collect.pop(0)
							temp_collect2.pop(0)

							self.que = temp_collect.copy()
							self.que_sorted = temp_collect2.copy()
							

							print("\n")
						else:
							if self.base_station(time):
								print("Drone " , self.id, " travels to base station")
			finally:
				
				lock.release()

	def base_station(self,time_to_base):		
		#have to set thelocation to 50,50, battery back to final 
		#need to chan
		self.location = [50,50]
		self.battery_reset()

		for i in self.que:
			i[2] = i[2] - time_to_base
			if i[2] <= 0:
				#we lost a point
				self.missed.append(i)



		temp5 = [x for x in self.que if x[2] >=0]
		self.que = []
		for i in temp5:
				self.que.append(i[:3])

		return True
	def battery_reset(self,):
		self.battery = 900

	def can_reach(self, location):
		
		dx = abs(self.que_sorted[0][0] - self.location[0])
		dy = abs(self.que_sorted[0][1] - self.location[1])
		x = dx * dx
		y = dy * dy
		squared = x + y
		#distance from drone to location
		distance = math.sqrt(squared)

		#distance from location to basepoint
		dx_1 = abs(50 - location[0][0])
		dy_1 = abs(50 - location[0][1])
		x_1 = dx_1 * dx_1
		y_1 = dy_1 * dy_1
		squared_1 = x_1 + y_1
		distance_1 = math.sqrt(squared)

		total_distance = distance_1 + distance
		time = location[0][2]
		time_to_dest = distance / float(self.speed)

		#need to change actions for out of battery and out of priority

		if self.battery >= total_distance and time_to_dest <= time:
			return True, time_to_dest


		elif self.battery >= total_distance and time_to_dest > time:
			#it has the battery to reach the point and return home
			#but will not make it to the point in time.
			#later on will implement seeing if any other vehicle can reach it
			#need to trash the point and move on,
			value = self.que_sorted[0]
			self.missed.append(value.copy())
			print("adding missed: ", value)
			
			temp8 = self.que_sorted.copy()
	
		
			temp8.pop(0)
			self.que_sorted = temp8.copy()

	
			

			
			temp6 = [x for x in self.que_sorted if x[2] >=0]
			self.que = []
			for i in temp6:
				self.que.append(i[:3])

		
			
			

			return False, -1
		elif self.battery < total_distance:
			#does not have enough battery, needs to go home
			#need distance from drone to basepoint and time to reach
			
			dfb_x = abs(50 - self.location[0])
			dfb_y = abs(50 - self.location[1])
			d_x = dfb_x * dfb_x
			d_y = dfb_y * dfb_y
			d_squared = d_x + d_y
			#distance from drone to location
			d_distance = math.sqrt(d_squared)
			ime_to_dest = d_distance / float(self.speed)


			return False, ime_to_dest

	

	def scheduling(self):
		location = self.location
		#take the first element for now, pretending to be first drone
		appended_list = []
		
		appended_list = self.que.copy()
	

		
		
		temporal_priority_sorted = sorted(appended_list, key=lambda x: x[2], reverse=False)
		temporal_priority = []
		for i in temporal_priority_sorted:
			lamda = (float(i[2]) - float(temporal_priority_sorted[0][2])) * float(len(temporal_priority_sorted))
			bamda = float(temporal_priority_sorted[-1][2]) - float(temporal_priority_sorted[0][2])
			if bamda == 0:
				print("\nerror",temporal_priority_sorted)
				temporal_priority.append(1.0)
				i.append(1.0)
			else:
				temporal_priority.append(lamda/bamda)
				i.append(lamda/bamda)
		
			
		distance_priority= []
		for i in appended_list:
			dx = abs(location[0] - i[0])
			dy = abs(location[1] - i[1])
			x = dx * dx
			y = dy * dy
			squared = x + y
			distance = math.sqrt(squared)
			i.append(distance)
			distance_priority.append(i)
		
		distance_priority_sorted = sorted(distance_priority,key = lambda x: x[4], reverse = False)

		for i in distance_priority_sorted:
			lamda = (float(i[4]) - float(distance_priority_sorted[0][4])) * float(len(distance_priority_sorted))
			bamda = float(distance_priority_sorted[-1][4]) - float(distance_priority_sorted[0][4])
			if bamda == 0:
				print("\nerror",temporal_priority_sorted)
				temporal_priority.append(1.0)
				i.append(1.0)
			else:
				temporal_priority.append(lamda/bamda)
				i.append(lamda/bamda)

		#joint priority from distance_priority_sorted

		joint_priority = []
		for i in distance_priority:
			a= 1
			b = 1
			priority = a*i[3] + b*i[5]
			log_inner = (i[3]*i[5]) + 1
			log = math.log(log_inner) 
			final_priorty = priority + log
			i.append(final_priorty)
		joint_priorty_sorted = sorted(distance_priority_sorted,key = lambda x: x[6], reverse = False)
		

		
		self.que_sorted=joint_priorty_sorted.copy()
		if self.boot == 1:
			print("The intial coordinates for UAV with their priorities are  ", self.id, "are: ")
			print(self.que_sorted)

			self.boot = 0
		

		return True


		
		

class Graph(object):
	"""docstring for Graph"""
	def __init__(self):
		super(Graph, self).__init__()
		
		
		self.current_locations = []
		self.flag = False
		#creation of intial 30 random points
		
		
		

	def run(self):
		
		coords = [(int(random.random()*100), int(random.random()*100),random.randint(1,60)) for _ in range(30)]
		
		self.drone_1 = UAV(0)
		
		self.drone_2 = UAV(1)
		self.drone_3 = UAV(2)
		
		self.kmeans_runner(coords)
		

	
		
		
		print("Initial Coordinates of the System:")
		
		
		#coordinates are set and assign each que to each drone
		self.drone_1.set(self.current_locations[0])
		
		self.drone_2.set(self.current_locations[1])
		self.drone_3.set(self.current_locations[2])

		#print(self.drone_1.que)
		print(self.drone_1.que)
		


		
		self.t = threading.Thread(target=self.kmeans_scheduler)
		self.s = threading.Thread(target=self.drone_1.run)
		self.z = threading.Thread(target=self.drone_2.run)


		
		
		
		
		

		#plt.pause(0.5)
		




		
		#self.r = threading.Thread(target=plt.show)
		
		#self.t.setDaemon(True)
		#self.s.setDaemon(True)
		
		
		
		#self.r.start()
		
		self.s.start()
		self.t.start()
		self.z.start()

	

		plt.ion()
		plt.figure()
		testing_alpha = [(20,10), (30,10), (40,10),(50,20), (99,100), (20,45),(10,15)]
		
	


		while(True):
			
			plt.plot(50,50,marker="p")
			plt.scatter(self.df['x'], self.df['y'], c= self.kmeans.labels_.astype(float), s=50, alpha=0.5)
			plt.scatter(self.centroids[:, 0], self.centroids[:, 1], c='red', s=50)
			
			
			
			
			if not self.drone_1.animation_visited.empty():   
				temp_variable = self.drone_1.animation_visited.get()
				print("TEMP VARIABLE IS ")
				print(temp_variable[0])
				print(temp_variable[1])
				plt.plot(temp_variable[0],temp_variable[1],'v',c="black")	
		

			

			plt.pause(2)
			plt.close()
			
		plt.ioff()
	

	def graph(self):
		
		print("plotting")
		
		

	def kmeans_scheduler(self):
		count = 0
		while True:
		#for i in range(100):
			lock.acquire()	
			try:
			#time.sleep(2)
				
				
				amount = len(self.drone_1.que.copy()) + len(self.drone_2.que.copy()) + len(self.drone_3.que.copy())
				
				#amount = len(self.drone_1.que_sorted)
				if amount <= 20:
					
					coords = [(int(random.random()*100), int(random.random()*100),random.randint(1,60)) for _ in range(30-amount)]
					count = count+5
					self.drone_1.flag = True
					self.drone_2.flag = True
					self.drone_3.flag = True
					for i in self.drone_1.que_sorted:
						coords.append(tuple(i[:3]))
					for i in self.drone_2.que_sorted:
						coords.append(tuple(i[:3]))
					#change this back to que sorted later
					for i in self.drone_3.que:
						coords.append(tuple(i[:3]))

					#lets graph the visited and missed points from when the kmeans is ran which means half have gone through
					combined_visited= self.drone_1.visited.copy() + self.drone_2.visited.copy()
					combined_missed = self.drone_1.missed.copy() + self.drone_2.missed.copy()

					x_garbage = []
					y_garbage=[]
					for i in combined_visited:
						x_garbage.append(i[0])
					for i in combined_visited:
						y_garbage.append(i[1])
					print("xgarbage",x_garbage)

					#plt.scatter(x_garbage, y_garbage, marker = "*")

					#if len(combined_missed) >=2 :
						#x_garbage = []
						#y_garbage=[]
						#for i in combined_missed:
							#x_garbage.append(i[0])
						#for i in combined_missed:
							#y_garbage.append(i[1])
						#plt.scatter(x_garbage, y_garbage, marker = "+")

					#plt.figure()
					
					print("Points visited and Points missed")
					

					
					
					#lets now graph the new coordinates


					
					self.kmeans_runner(coords)
					
					print("The new coordinates for Drone 0 is: ", self.current_locations[0])
					print("The new coordinates for Drone 1 is: ", self.current_locations[1])
					print("The new coordinates for Drone 2 is: ", self.current_locations[2])


					self.drone_1.set(self.current_locations[0])
					self.drone_2.set(self.current_locations[1])
					self.drone_3.set(self.current_locations[2])
					self.drone_1.flag = False
					print("\nflag changed back NEW COORDS",self.current_locations[0])
					self.drone_1.boot = 1
					self.drone_2.flag = False
					self.drone_2.boot = 1
					self.drone_3.flag = False
					self.drone_3.boot = 1
					
					
					
			finally:
				
				lock.release()
				

	def kmeans_runner(self, coords): 
		self.df = DataFrame(coords,columns=['x','y','p'])
		self.kmeans = KMeans(n_clusters=3).fit(self.df)
		self.centroids = self.kmeans.cluster_centers_
		


		
		
		z = 0
		appended_list = []
		for i in range(len(self.centroids)):
			appended_list.append([])
		for i in self.kmeans.labels_:
			appended_list[i].append([self.df['x'][z],self.df['y'][z],self.df['p'][z]])
			z = z + 1
		
		
		self.current_locations = appended_list
		

class Plotter(object):
		"""docstring for Plotter"""
		def __init__(self):
			super(Plotter, self).__init__()
			plt.ion()
			plt.figure()


				

if __name__ == '__main__':
	
	
	a = Graph()
	
	a.run()
	
	



