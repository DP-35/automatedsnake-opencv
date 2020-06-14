import numpy as np
import cv2
import math
import pyautogui

cap=cv2.VideoCapture(0)

while True:
	ret,frame=cap.read()
	cv2.rectangle(frame,(100,100),(300,300),(0,255,0),0)#draw rectangle on window
	img_crop=frame[100:300,100:300]
	#cv2.imshow("crooped image",img_crop)

	gaussian_blur=cv2.GaussianBlur(img_crop,(3,3),0)#applied guassian blur
	#cv2.imshow("blur",gaussian_blur)
	hsv=cv2.cvtColor(gaussian_blur,cv2.COLOR_BGR2HSV)
	#cv2.imshow("hsv",hsv)

	skin=cv2.inRange(hsv,np.array([2,0,0]),np.array([20,255,255]))#low white ,high white values
	#cv2.imshow("skin",skin)

	k=np.ones((5,5))
	dilation=cv2.dilate(skin,k,iterations=2)
	erosion=cv2.erode(dilation,k,iterations=1)#removes white noises
	#cv2.imshow("erosion",erosion)

	filtered=cv2.GaussianBlur(erosion,(3,3),0)
	ret,thresh=cv2.threshold(filtered,127,255,0)
	cv2.imshow("thresh",thresh)	

	contours,hierarchy=cv2.findContours(thresh,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
	#print(contours)

	try:
		contour=max(contours,key=lambda x:cv2.contourArea(x))
		#print(contour)

		x,y,w,h=cv2.boundingRect(contour)
		cv2.rectangle(img_crop,(x,y),(x+w,y+h),(0,0,255),0)#drawed rectangle around hand

		hull=cv2.convexHull(contour)#convex hull joins all the nearest points involving all the points in a effiecint way

		hull_contour=np.zeros(img_crop.shape,np.uint8)
		cv2.drawContours(hull_contour,[contour],-1,(0,255,0),0)
		cv2.drawContours(hull_contour,[hull],-1,(0,0,255),0)

		hull=cv2.convexHull(contour,returnPoints=False)
		defects=cv2.convexityDefects(contour,hull)

		count_defects=0

		for i in range(defects.shape[0]):
			s,e,f,d=defects[i,0]
			start=tuple(contour[s][0])
			#print(start)
			end=tuple(contour[e][0])
			far=tuple(contour[f][0])

			a=math.sqrt((end[0]-start[0])**2+(end[1]-start[1])**2)
			b=math.sqrt((far[0]-start[0])**2+(far[1]-start[1])**2)
			c=math.sqrt((end[0]-far[0])**2+(end[1]-far[1])**2)

			angle=(math.acos((b**2+c**2-a**2)/(2*b*c))*180)/3.14
			#print(angle)

			if angle<=90:#treat as fingers
				count_defects+=1
				cv2.circle(img_crop,far,1,[0,0,255],-1)

			cv2.line(img_crop,start,end,[0,255,0],2)


		if count_defects==0:
			pyautogui.press('down')
			cv2.putText(frame,"DOWN",(115,80),cv2.FONT_HERSHEY_SIMPLEX,2,2,2)

		elif count_defects==1:
			pyautogui.moveTo('left')
			cv2.putText(frame,"LEFT",(115,80),cv2.FONT_HERSHEY_SIMPLEX,2,2,2)

		elif count_defects==2:
			pyautogui.press('right')
			cv2.putText(frame,"LEFT",(115,80),cv2.FONT_HERSHEY_SIMPLEX,2,2,2)

		else:
			pyautogui.press('up')
			cv2.putText(frame,"UP",(115,80),cv2.FONT_HERSHEY_SIMPLEX,2,2,2)


	except:
		pass
	cv2.imshow("game",frame)
	if cv2.waitKey(1)== ord('q'):
		break

cap.release()
cv2.destroyAllWindows()
