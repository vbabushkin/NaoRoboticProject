from naoqi import ALProxy
import motion
import time
robot_IP="10.104.67.182"
motionProxy = ALProxy("ALMotion", robot_IP, 9559)
postureProxy = ALProxy("ALRobotPosture", robot_IP, 9559)
postureProxy.goToPosture("StandInit",0.5)
##motionProxy.stiffnessInterpolation("Body", 1.0, 1.0)
##effectorInit = motionProxy.getPosition("RArm", motion.FRAME_ROBOT, False)
##print "RArm"
##print effectorInit

effectorInit = motionProxy.getPosition("RArm", motion.FRAME_ROBOT, False)
##print "effector position after standinit 1"
##print effectorInit

# X Axis LArm Position feasible movement = [ +0.00, +0.12] meter
# Y Axis LArm Position feasible movement = [ -0.05, +0.10] meter
# Y Axis RArm Position feasible movement = [ -0.10, +0.05] meter
# Z Axis LArm Position feasible movement = [ -0.10, +0.10] meter
isEnabled = True
motionProxy.wbEnableEffectorControl("RArm", isEnabled)
motionProxy.wbSetEffectorControl("RArm", [.2,.0,.20])
##time.sleep(2)
effectorInit2 = motionProxy.getPosition("RHand", motion.FRAME_ROBOT, False)
print "effector position after standinit 2"
print effectorInit2
time.sleep(1)
print "setting motion off...."
motionProxy.wbEnableEffectorControl("RArm", False) ##this releases the lock on wb so that it sits gracefully.
