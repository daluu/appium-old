from robot import Bot
from time import sleep

robot = Bot('/dev/tty.usbmodem5d11')

rest_angles = (30,30,30)
rest_position = robot.forward_k(30,30,30)
center_angles = (40,40,40)
center_position = robot.forward_k(40,40,40)
top_angles1 = robot.inverse_k(0, rest_position[2]+100, rest_position[3])
top_angles2 = robot.inverse_k(0, center_position[2]+100, center_position[3])
bottom_angles1 = robot.inverse_k(0, rest_position[2]-100, rest_position[3])
bottom_angles2 = robot.inverse_k(0, center_position[2]-100, center_position[3])
right_angles1 = robot.inverse_k(rest_position[2]+100, 0, rest_position[3])
right_angles2 = robot.inverse_k(center_position[2]+100, 0, center_position[3])
left_angles1 = robot.inverse_k(rest_position[2]-100, 0, rest_position[3])
left_angles2 = robot.inverse_k(center_position[2]-100, 0, center_position[3])

robot.set_position(rest_angles)
sleep(.5)

print 'Center'
robot.set_position(center_angles)
sleep(.5)
robot.set_position(rest_angles)
sleep(2)

print 'Top'
robot.set_position(top_angles1)
sleep(.5)
robot.set_position(top_angles2)
sleep(.5)
robot.set_position(rest_angles)
sleep(2)

print 'Bottom'
robot.set_position(bottom_angles1)
sleep(.5)
robot.set_position(bottom_angles2)
sleep(.5)
robot.set_position(rest_angles)
sleep(2)

print 'Left'
robot.set_position(left_angles1)
sleep(.5)
robot.set_position(left_angles2)
sleep(.5)
robot.set_position(rest_angles)
sleep(2)

print 'Right'
robot.set_position(right_angles1)
sleep(.5)
robot.set_position(right_angles2)
sleep(.5)
robot.set_position(rest_angles)
sleep(2)

